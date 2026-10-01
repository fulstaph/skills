# Skills

A curated, Git-backed marketplace of reusable coding-agent skills built around the [Agent Skills format](https://agentskills.io/specification).

The first skill, `code-simplifier`, is being designed to simplify a selected file or module through structural refactoring while preserving behavior and public interfaces. It will support an optional independent review when the host provides subagents.

## Layout

The design spec is available in `docs/superpowers/specs/2026-10-01-code-simplifier-design.md`. Implementation will place the portable package in `skills/code-simplifier/`, with evaluation material and agent-specific integration documentation kept outside that package. A human-readable catalog and a machine-readable `catalog.json` will index the shared packages.

Shared instructions use ordinary capabilities rather than agent-specific tool names or invocation syntax. Codex and Claude Code marketplace adapters will each expose the same `agent-skills` bundle from this repository. Native discovery and invocation follow each host's supported mechanisms.

## Versioning

Git history tracks source changes. Validated releases will use repository-wide semantic version tags, starting at `v0.1.0`, and a changelog explaining behavioral changes. Release metadata will stay consistent across the root version file, catalog, and native plugin manifests. The current documentation-only repository is not a released marketplace bundle.

Installations use the skill directory from a selected release. Preserve local modifications when updating an installed copy. Remote publication and licensing can be configured when the repository is ready to share.
