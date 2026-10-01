"""Validate the shared catalog, portable skills, and native adapters."""

import argparse
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import string
from urllib.parse import unquote, urlsplit

import yaml


VERSION_PATTERN = r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
NAME_PATTERN = r"[a-z0-9]+(?:-[a-z0-9]+)*"


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node):
    loader.flatten_mapping(node)
    return unique_pairs(loader.construct_pairs(node, deep=True))


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def is_within(path: Path, boundary: Path) -> bool:
    return path.resolve().is_relative_to(boundary.resolve())


def has_symlink(path: Path, boundary: Path) -> bool:
    while path != boundary:
        if path.is_symlink():
            return True
        if path.parent == path:
            break
        path = path.parent
    return boundary.is_symlink()


def portable_relative(value: str) -> bool:
    return bool(value) and not (
        PurePosixPath(value).is_absolute() or PureWindowsPath(value).drive
        or "\\" in value
    )


def frontmatter(path: Path) -> dict:
    text = read_text(path)
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        raise ValueError("missing YAML frontmatter")
    data = yaml.load(match.group(1), Loader=UniqueLoader)
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data


def link_destination(text: str, start: int) -> str:
    """Read angle or bare destinations, preserving balanced URL parentheses."""
    while start < len(text) and text[start].isspace():
        start += 1
    angle = start < len(text) and text[start] == "<"
    if angle:
        start += 1
    result, depth = [], 0
    while start < len(text):
        char = text[start]
        if char == "\\" and start + 1 < len(text) and text[start + 1] in string.punctuation:
            result.append(text[start + 1])
            start += 2
            continue
        if angle:
            if char == ">" or char in "\r\n":
                break
        elif char.isspace() or (char == ")" and depth == 0):
            break
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        result.append(char)
        start += 1
    return "".join(result)


def markdown_targets(text: str):
    # Ignore code examples. Scan destinations independently of label nesting;
    # this is deliberately conservative about malformed labels, too.
    text = re.sub(r"(?m)^(`{3,}|~{3,})[^\n]*\n.*?^\1[^\n]*$", "", text, flags=re.S)
    text = re.sub(r"(`+)(.*?)\1", "", text, flags=re.S)
    for match in re.finditer(r"\]\(", text):
        target = link_destination(text, match.end())
        if target:
            yield target
    for match in re.finditer(r"(?m)^[ \t]{0,3}\[[^\n]+\]:[ \t]*", text):
        target = link_destination(text, match.end())
        if target:
            yield target


def validate_repository(root: Path, expected_tag: str | None = None) -> list[str]:
    root = Path(root).absolute()
    errors = []

    def error(path, message):
        label = path.relative_to(root).as_posix() if isinstance(path, Path) else path
        errors.append(f"{label}: {message}")

    def load_json(relative):
        path = root / relative
        try:
            if has_symlink(path, root):
                raise ValueError("symlinks are not permitted")
            data = json.loads(read_text(path), object_pairs_hook=unique_pairs)
            if not isinstance(data, dict):
                raise ValueError("must be a JSON object")
            return data
        except (OSError, UnicodeError, ValueError, RecursionError) as exc:
            error(relative, str(exc))
            return {}

    version = ""
    try:
        if has_symlink(root / "VERSION", root):
            raise ValueError("symlinks are not permitted")
        version = read_text(root / "VERSION").strip()
        if not re.fullmatch(VERSION_PATTERN, version):
            error("VERSION", "must be a semantic version X.Y.Z without leading zeroes")
    except (OSError, UnicodeError, ValueError) as exc:
        error("VERSION", str(exc))
    if expected_tag is not None:
        if not re.fullmatch("v" + VERSION_PATTERN, expected_tag) or expected_tag != "v" + version:
            error("VERSION", f"tag {expected_tag!r} must match v{version}")
    try:
        changelog = root / "CHANGELOG.md"
        if has_symlink(changelog, root):
            raise ValueError("symlinks are not permitted")
        if not re.search(r"^## \[" + re.escape(version) + r"\] - \d{4}-\d{2}-\d{2}$", read_text(changelog), re.M):
            error(changelog, f"missing release heading for {version}")
    except (OSError, UnicodeError, ValueError) as exc:
        error("CHANGELOG.md", str(exc))

    catalog = load_json("catalog.json")
    if type(catalog.get("schemaVersion")) is not int or catalog.get("schemaVersion") != 1:
        error("catalog.json", "schemaVersion must be 1")
    if catalog.get("version") != version:
        error("catalog.json", "version must match VERSION")
    entries = catalog.get("skills")
    if not isinstance(entries, list):
        error("catalog.json", "skills must be an array")
        entries = []
    seen_names, seen_paths = set(), set()
    catalog_skills = {}
    for entry in entries:
        if not isinstance(entry, dict):
            error("catalog.json", "each skill must be an object")
            continue
        name, relative = entry.get("name"), entry.get("path")
        if not isinstance(name, str) or not re.fullmatch(NAME_PATTERN, name) or len(name) > 64:
            error("catalog.json", "invalid skill name")
            continue
        if name in seen_names:
            error("catalog.json", f"duplicate skill name: {name}")
        seen_names.add(name)
        if not isinstance(relative, str) or not portable_relative(relative) or ".." in PurePosixPath(relative).parts:
            error("catalog.json", f"invalid relative skill path: {relative!r}")
            continue
        if relative != f"skills/{name}":
            error("catalog.json", f"path must be skills/{name}")
            continue
        if relative in seen_paths:
            error("catalog.json", f"duplicate skill path: {relative}")
        seen_paths.add(relative)
        if not isinstance(entry.get("description"), str) or not entry["description"].strip():
            error("catalog.json", f"{name}: description must be a nonempty string")
        tags = entry.get("tags")
        if not isinstance(tags, list) or not tags or any(not isinstance(t, str) or not t.strip() for t in tags):
            error("catalog.json", f"{name}: tags must be nonempty strings")
        path = root / relative
        if has_symlink(path, root) or not is_within(path, root / "skills"):
            error("catalog.json", f"{relative}: skill path escapes or uses a symlink")
            continue
        if not (path / "SKILL.md").is_file():
            error("catalog.json", f"{relative}: missing SKILL.md")
        catalog_skills[relative] = entry

    skills_root = root / "skills"
    if has_symlink(skills_root, root):
        error("skills", "symlinks are not permitted")
        discovered = []
    else:
        discovered = sorted(skills_root.glob("*/SKILL.md"))
    if not discovered:
        error("catalog.json", "no skill packages discovered")
    for skill in discovered:
        package = skill.parent
        relative = package.relative_to(root).as_posix()
        entry = catalog_skills.get(relative)
        if entry is None:
            error("catalog.json", f"uncatalogued skill: {relative}")
        if has_symlink(skill, root):
            error(skill, "symlinks are not permitted")
            continue
        try:
            data = frontmatter(skill)
            allowed = {"name", "description", "license", "compatibility", "metadata"}
            for key in data.keys() - allowed:
                error(skill, f"unsupported or nonportable frontmatter field: {key}")
            name, description = data.get("name"), data.get("description")
            if not isinstance(name, str) or not re.fullmatch(NAME_PATTERN, name) or len(name) > 64 or name != package.name:
                error(skill, "name must be a valid lowercase identifier matching its directory (max 64)")
            if not isinstance(description, str) or not description.strip() or len(description) > 1024:
                error(skill, "description must be a nonempty string of at most 1024 characters")
            for key in ("license", "compatibility"):
                if key in data and not isinstance(data[key], str):
                    error(skill, f"{key} must be a string")
            if isinstance(data.get("compatibility"), str) and len(data["compatibility"]) > 500:
                error(skill, "compatibility must be at most 500 characters")
            if "metadata" in data and (not isinstance(data["metadata"], dict) or any(
                not isinstance(k, str) or not isinstance(v, str) for k, v in data["metadata"].items()
            )):
                error(skill, "metadata must map strings to strings")
            if entry and (entry.get("name") != name or entry.get("description") != description):
                error("catalog.json", f"{relative}: name/description must match SKILL.md")
        except (OSError, UnicodeError, ValueError, TypeError, yaml.YAMLError, RecursionError) as exc:
            error(skill, str(exc))
        for resource in sorted(package.rglob("*")):
            if has_symlink(resource, root):
                error(resource, "symlinks are not permitted")
        for document in sorted(package.rglob("*.md")):
            if has_symlink(document, root):
                continue
            try:
                for target in markdown_targets(read_text(document)):
                    if target.startswith("#"):
                        continue
                    # Drive paths must not be mistaken for external URI schemes.
                    if not portable_relative(target):
                        error(document, f"absolute or nonportable resource link: {target}")
                        continue
                    url = urlsplit(target)
                    if url.scheme or url.netloc:
                        if url.scheme in {"http", "https", "mailto"}:
                            continue
                        error(document, f"unsupported resource link scheme: {target}")
                        continue
                    local = unquote(url.path)
                    path = document.parent / local
                    if not portable_relative(local) or not is_within(path, package) or has_symlink(path, package):
                        error(document, f"resource link escapes package or uses a symlink: {target}")
                    elif not path.is_file():
                        error(document, f"missing referenced resource: {target}")
            except (OSError, UnicodeError, ValueError) as exc:
                error(document, str(exc))

    for relative in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
        manifest = load_json(relative)
        if manifest.get("name") != "coding-skills":
            error(relative, "name must be coding-skills")
        if manifest.get("version") != version:
            error(relative, "version must match VERSION")
        if manifest.get("skills") not in ("./skills/", ["./skills/"]):
            error(relative, "skills must discover ./skills/")
    for relative, source in (
        (".agents/plugins/marketplace.json", {"source": "local", "path": "./"}),
        (".claude-plugin/marketplace.json", "./"),
    ):
        marketplace = load_json(relative)
        if marketplace.get("name") != "coding-skills":
            error(relative, "marketplace name must be coding-skills")
        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list) or len(plugins) != 1 or not isinstance(plugins[0], dict):
            error(relative, "plugins must contain one coding-skills bundle")
            continue
        plugin = plugins[0]
        if plugin.get("name") != "coding-skills":
            error(relative, "plugin name must be coding-skills")
        if plugin.get("version") != version:
            error(relative, "plugin version must match VERSION")
        if plugin.get("source") != source:
            error(relative, "plugin source must point to repository root ./")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--tag")
    args = parser.parse_args()
    errors = validate_repository(args.root, args.tag)
    if errors:
        print("\n".join(errors))
        return 1
    print("Validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
