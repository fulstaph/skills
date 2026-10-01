"""Build portable ZIPs from validated release inputs."""

import argparse
import json
from pathlib import Path
import re
import tempfile
import zipfile

if __package__:
    from .validate import has_symlink, is_within, read_text, validate_repository
else:
    from validate import has_symlink, is_within, read_text, validate_repository


FIXED_FILES = (
    "README.md", "VERSION", "CHANGELOG.md", "catalog.json",
    ".agents/plugins/marketplace.json", ".codex-plugin/plugin.json",
    ".claude-plugin/marketplace.json", ".claude-plugin/plugin.json",
)
EXCLUDED_DIRS = {".git", ".venv", "__pycache__", "scratch", "runs", "dist"}


def release_notes(root: Path, version: str) -> str:
    text = read_text(Path(root) / "CHANGELOG.md")
    heading = re.compile(r"^## \[" + re.escape(version) + r"\] - \d{4}-\d{2}-\d{2}\s*$", re.M)
    matches = list(heading.finditer(text))
    if len(matches) != 1:
        raise ValueError(f"CHANGELOG.md: expected one release heading for {version}")
    remaining = text[matches[0].end():]
    following = re.search(r"^## ", remaining, re.M)
    notes = remaining[:following.start()] if following else remaining
    if not notes.strip():
        raise ValueError(f"CHANGELOG.md: release {version} has no notes")
    return notes.strip() + "\n"


def package_files(root: Path, directory: Path) -> list[Path]:
    if has_symlink(directory, root) or not is_within(directory, root):
        raise ValueError(f"{directory.relative_to(root)}: symlinks or escaping paths are not permitted")
    result = []
    for path in sorted(directory.rglob("*")):
        if has_symlink(path, root):
            raise ValueError(f"{path.relative_to(root)}: symlinks are not permitted")
        parts = path.relative_to(directory).parts
        if any(part in EXCLUDED_DIRS for part in parts) or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_file():
            result.append(path)
    return result


def write_zip(path: Path, members: list[tuple[str, bytes]]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)


def package_release(root: Path, destination: Path, tag: str) -> list[Path]:
    root, destination = Path(root).absolute(), Path(destination).absolute()
    errors = validate_repository(root, expected_tag=tag)
    if errors:
        raise ValueError("\n".join(errors))
    version = read_text(root / "VERSION").strip()
    release_notes(root, version)  # Preflight notes before creating any artifacts.
    catalog = json.loads(read_text(root / "catalog.json"))
    files = [root / relative for relative in FIXED_FILES]
    if (root / "LICENSE").exists() or (root / "LICENSE").is_symlink():
        files.append(root / "LICENSE")
    for directory in (root / "skills", root / "docs/integrations"):
        if directory.exists() or directory.is_symlink():
            files.extend(package_files(root, directory))
    # Read every selected file before writing; failures cannot leave partial archives.
    contents = {}
    for path in files:
        if has_symlink(path, root) or not is_within(path, root):
            raise ValueError(f"{path.relative_to(root)}: symlinks or escaping paths are not permitted")
        if not path.is_file():
            raise ValueError(f"{path.relative_to(root)}: expected a regular file")
        contents[path.relative_to(root).as_posix()] = path.read_bytes()
    builds = {f"agent-skills-{version}.zip": [("agent-skills/" + p, data) for p, data in contents.items()]}
    for skill in catalog["skills"]:
        prefix = skill["path"] + "/"
        builds[f'{skill["name"]}-{version}.zip'] = [
            (skill["name"] + "/" + p[len(prefix):], data)
            for p, data in contents.items() if p.startswith(prefix)
        ]
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination) as staging:
        for name, members in builds.items():
            write_zip(Path(staging) / name, members)
        for name in builds:
            (Path(staging) / name).replace(destination / name)
    return [destination / name for name in builds]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()
    try:
        archives = package_release(args.root, args.output, args.tag)
        (args.output / "release-notes.md").write_text(
            release_notes(args.root, read_text(args.root / "VERSION").strip()), encoding="utf-8"
        )
    except (ValueError, OSError, UnicodeError) as exc:
        print(exc)
        return 1
    for archive in archives:
        print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
