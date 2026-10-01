import json
from pathlib import Path


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def make_repository(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    skill = root / "skills/code-simplifier"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        '---\nname: "code-simplifier"\ndescription: "Test refactoring skill"\n---\n'
        '# Simplifier\n\nSee [examples](references/examples.md).\n', encoding="utf-8"
    )
    (skill / "references/examples.md").write_text("# Examples\n", encoding="utf-8")
    (root / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    (root / "README.md").write_text("# Test marketplace\n", encoding="utf-8")
    (root / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [0.1.0] - 2026-10-01\n\n- Initial test release.\n", encoding="utf-8"
    )
    write_json(root / "catalog.json", {
        "schemaVersion": 1, "version": "0.1.0", "skills": [{
            "name": "code-simplifier", "description": "Test refactoring skill",
            "path": "skills/code-simplifier", "tags": ["coding", "refactoring", "readability"]
        }]
    })
    for host in ("codex", "claude"):
        write_json(root / f".{host}-plugin/plugin.json", {
            "name": "agent-skills", "description": "Portable skills",
            "version": "0.1.0", "skills": "./skills/"
        })
    write_json(root / ".agents/plugins/marketplace.json", {
        "name": "agent-skills", "plugins": [{
            "name": "agent-skills", "version": "0.1.0",
            "source": {"source": "local", "path": "./"}
        }]
    })
    write_json(root / ".claude-plugin/marketplace.json", {
        "name": "agent-skills", "owner": {"name": "Test Owner"}, "plugins": [{
            "name": "agent-skills", "version": "0.1.0", "source": "./"
        }]
    })
    return root
