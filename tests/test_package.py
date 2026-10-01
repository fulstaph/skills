from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.package import package_release, release_notes
from tests.helpers import make_repository


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = make_repository(Path(self.temp.name) / "repo")
        self.output = Path(self.temp.name) / "output"

    def members(self, name):
        archive = next(p for p in package_release(self.root, self.output, "v0.1.0") if p.name == name)
        with zipfile.ZipFile(archive) as zipped:
            return set(zipped.namelist())

    def test_standalone_skill_keeps_references(self):
        names = self.members("code-simplifier-0.1.0.zip")
        self.assertIn("code-simplifier/SKILL.md", names)
        self.assertIn("code-simplifier/references/examples.md", names)

    def test_marketplace_keeps_hidden_manifests(self):
        names = self.members("agent-skills-0.1.0.zip")
        for path in (".agents/plugins/marketplace.json", ".codex-plugin/plugin.json",
                     ".claude-plugin/marketplace.json", ".claude-plugin/plugin.json"):
            self.assertIn("agent-skills/" + path, names)

    def test_scratch_and_git_files_are_excluded(self):
        for relative in (".git/secret", "scratch/token", ".venv/secret", "docs/superpowers/plans/draft.md",
                         "skills/code-simplifier/__pycache__/cache.pyc", "evals/runs/output.md"):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("sentinel")
        names = self.members("agent-skills-0.1.0.zip")
        self.assertFalse(any("/.git/" in p or "/scratch/" in p or "__pycache__" in p for p in names))
        self.assertFalse(any("superpowers" in p or "/evals/" in p for p in names))

    def test_tag_mismatch_prevents_artifacts(self):
        with self.assertRaises(ValueError):
            package_release(self.root, self.output, "v9.9.9")
        self.assertFalse(self.output.exists())

    def test_symlink_input_is_rejected(self):
        path = self.root / "skills/code-simplifier/references/examples.md"
        path.unlink()
        outside = self.root.parent / "outside.md"
        outside.write_text("private")
        path.symlink_to(outside)
        with self.assertRaises(ValueError):
            package_release(self.root, self.output, "v0.1.0")
        self.assertFalse(self.output.exists())

    def test_output_path_with_spaces(self):
        self.assertEqual(len(package_release(self.root, self.output / "release files", "v0.1.0")), 2)

    def test_release_notes_match_requested_version(self):
        with (self.root / "CHANGELOG.md").open("a") as stream:
            stream.write("\n## [0.0.1] - 2026-09-01\n\n- Earlier release.\n")
        self.assertEqual(release_notes(self.root, "0.1.0").strip(), "- Initial test release.")

    def test_symlinked_integration_directory_is_rejected(self):
        outside = self.root.parent / "outside"
        outside.mkdir()
        (outside / "secret.md").write_text("private")
        (self.root / "docs").mkdir()
        (self.root / "docs/integrations").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            package_release(self.root, self.output, "v0.1.0")
        self.assertFalse(self.output.exists())

    def test_archives_are_repeatable(self):
        first = {p.name: p.read_bytes() for p in package_release(self.root, self.output, "v0.1.0")}
        second = {p.name: p.read_bytes() for p in package_release(self.root, self.output / "other", "v0.1.0")}
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
