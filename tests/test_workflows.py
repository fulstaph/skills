from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]


def workflow(name):
    return yaml.load((ROOT / ".github/workflows" / name).read_text(), Loader=yaml.BaseLoader)


class WorkflowTests(unittest.TestCase):
    def test_ci_runs_for_pr_and_main(self):
        ci = workflow("ci.yml")
        self.assertIn("pull_request", ci["on"])
        self.assertEqual(ci["on"]["push"]["branches"], ["main"])

    def test_ci_has_read_only_permissions(self):
        ci = workflow("ci.yml")
        self.assertEqual(ci["permissions"]["contents"], "read")
        for job in ci["jobs"].values():
            self.assertNotEqual(job.get("permissions", {}).get("contents"), "write")

    def test_release_runs_for_version_tags(self):
        self.assertEqual(workflow("release.yml")["on"]["push"]["tags"], ["v*"])

    def test_publish_requires_successful_verify(self):
        publish = workflow("release.yml")["jobs"]["publish"]
        self.assertEqual(publish["needs"], "verify")
        self.assertNotIn("if", publish)  # Default success gate must not be overridden.

    def test_only_publish_has_content_write(self):
        release = workflow("release.yml")
        self.assertEqual(release["permissions"]["contents"], "read")
        self.assertEqual(release["jobs"]["publish"]["permissions"]["contents"], "write")
        for name, job in release["jobs"].items():
            if name != "publish":
                self.assertNotEqual(job.get("permissions", {}).get("contents"), "write")

    def test_release_uses_packager_and_notes_artifact(self):
        jobs = workflow("release.yml")["jobs"]
        verify = jobs["verify"]
        commands = "\n".join(s.get("run", "") for s in verify["steps"])
        self.assertIn('python scripts/validate.py --root . --tag "$RELEASE_TAG"', commands)
        self.assertIn('python scripts/package.py --root . --output dist --tag "$RELEASE_TAG"', commands)
        upload = next(s for s in verify["steps"] if s.get("uses", "").startswith("actions/upload-artifact@"))
        self.assertIn("dist/*.zip", upload["with"]["path"])
        self.assertIn("dist/release-notes.md", upload["with"]["path"])
        publish = jobs["publish"]["steps"]
        download_index = next(i for i, s in enumerate(publish) if s.get("uses", "").startswith("actions/download-artifact@"))
        self.assertEqual(publish[download_index]["with"]["name"], upload["with"]["name"])
        release_index = next(i for i, s in enumerate(publish) if "gh release create" in s.get("run", ""))
        self.assertLess(download_index, release_index)
        self.assertIn("--notes-file dist/release-notes.md", publish[release_index]["run"])


if __name__ == "__main__":
    unittest.main()
