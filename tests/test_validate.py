import json
from pathlib import Path
import tempfile
import unittest

from scripts.validate import validate_repository
from tests.helpers import make_repository, write_json


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = make_repository(Path(self.temp.name) / "repo")
        self.skill = self.root / "skills/code-simplifier/SKILL.md"

    def mutate_json(self, relative, change):
        path = self.root / relative
        value = json.loads(path.read_text())
        change(value)
        write_json(path, value)

    def rejected(self, affected_file):
        errors = validate_repository(self.root)
        self.assertTrue(errors)
        self.assertTrue(any(affected_file in error for error in errors), errors)

    def test_valid_repository_has_no_errors(self):
        self.assertEqual(validate_repository(self.root), [])

    def test_release_tag_must_match_version(self):
        self.assertTrue(validate_repository(self.root, expected_tag="v9.9.9"))

    def test_duplicate_yaml_keys_rejected(self):
        self.skill.write_text(self.skill.read_text().replace('name: "code-simplifier"',
            'name: "code-simplifier"\nname: "other"'))
        self.rejected("skills/code-simplifier/SKILL.md")

    def test_non_string_description_rejected(self):
        self.skill.write_text(self.skill.read_text().replace('"Test refactoring skill"', '42'))
        self.rejected("skills/code-simplifier/SKILL.md")

    def test_catalog_parent_escape_rejected(self):
        self.mutate_json("catalog.json", lambda d: d["skills"][0].update(path="../outside"))
        self.rejected("catalog.json")

    def test_absolute_catalog_path_rejected(self):
        self.mutate_json("catalog.json", lambda d: d["skills"][0].update(path=str(self.skill.parent)))
        self.rejected("catalog.json")

    def test_reference_escape_rejected(self):
        self.skill.write_text(self.skill.read_text() + "\n[secret](../outside.md)\n")
        self.rejected("skills/code-simplifier/SKILL.md")

    def test_reference_symlink_rejected(self):
        resource = self.skill.parent / "references/examples.md"
        resource.unlink()
        outside = self.root.parent / "outside.md"
        outside.write_text("outside")
        resource.symlink_to(outside)
        self.rejected("skills/code-simplifier/SKILL.md")

    def test_missing_reference_rejected(self):
        (self.skill.parent / "references/examples.md").unlink()
        self.rejected("skills/code-simplifier/SKILL.md")

    def test_duplicate_catalog_name_rejected(self):
        self.mutate_json("catalog.json", lambda d: d["skills"].append(d["skills"][0].copy()))
        self.rejected("catalog.json")

    def test_uncatalogued_skill_rejected(self):
        self.mutate_json("catalog.json", lambda d: d.update(skills=[]))
        self.rejected("catalog.json")

    def test_manifest_name_mismatch_rejected(self):
        self.mutate_json(".codex-plugin/plugin.json", lambda d: d.update(name="wrong"))
        self.rejected(".codex-plugin/plugin.json")

    def test_native_version_drift_rejected(self):
        self.mutate_json(".claude-plugin/plugin.json", lambda d: d.update(version="9.9.9"))
        self.rejected(".claude-plugin/plugin.json")

    def test_duplicate_json_keys_rejected(self):
        path = self.root / "catalog.json"
        path.write_text(path.read_text().replace('"schemaVersion": 1', '"schemaVersion": 1, "schemaVersion": 2'))
        self.rejected("catalog.json")

    def test_malformed_catalog_shape_returns_diagnostics(self):
        for value in ([], {"skills": [None]}, {"skills": "wrong"}):
            with self.subTest(value=value):
                write_json(self.root / "catalog.json", value)
                self.rejected("catalog.json")

    def test_nested_reference_escape_rejected(self):
        (self.skill.parent / "references/examples.md").write_text("[secret](../../outside.md)")
        self.rejected("skills/code-simplifier/references/examples.md")

    def test_external_links_and_anchors_are_allowed(self):
        self.skill.write_text(self.skill.read_text() + "\n[web](https://example.org) [heading](#simplifier)\n")
        self.assertEqual(validate_repository(self.root), [])

    def test_host_specific_tool_restrictions_rejected(self):
        self.skill.write_text(self.skill.read_text().replace("---\n#", "allowed-tools: shell\n---\n#"))
        self.rejected("skills/code-simplifier/SKILL.md")

    def test_nested_label_escape_rejected(self):
        self.skill.write_text(self.skill.read_text() + "\n[escape [nested label]](../../outside.md)\n")
        self.rejected("skills/code-simplifier/SKILL.md")

    def test_nested_label_missing_reference_rejected(self):
        self.skill.write_text(self.skill.read_text() + "\n[missing [nested label]](references/missing.md)\n")
        self.rejected("skills/code-simplifier/SKILL.md")

    def test_nested_label_existing_resource_is_allowed(self):
        self.skill.write_text(self.skill.read_text() + "\n[example [nested label]](references/examples.md)\n")
        self.assertEqual(validate_repository(self.root), [])

    def test_parenthesized_resource_filename_is_allowed(self):
        (self.skill.parent / "references/example(v1).md").write_text("# Example\n")
        self.skill.write_text(self.skill.read_text() + "\n[example](references/example(v1).md)\n")
        self.assertEqual(validate_repository(self.root), [])


if __name__ == "__main__":
    unittest.main()
