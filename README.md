# Skills

Reusable coding-agent skills built around the [Agent Skills format](https://agentskills.io/specification).

The first skill, `code-simplifier`, is being designed to simplify a selected file or module through structural refactoring while preserving behavior and public interfaces. It will support an optional independent review when the host provides subagents.

## Layout

The design spec is available in `docs/superpowers/specs/2026-10-01-code-simplifier-design.md`. Implementation will place the portable package in `skills/code-simplifier/`, with evaluation material and agent-specific integration documentation kept outside that package.

Shared instructions use ordinary capabilities rather than agent-specific tool names or invocation syntax. Native discovery and installation depend on the host agent.

## Versioning

Git history tracks source changes. Validated releases will use repository-wide semantic version tags, starting at `v0.1.0`, and a changelog explaining behavioral changes. The current documentation-only repository is not a released skill.

Installations use the skill directory from a selected release. Preserve local modifications when updating an installed copy. Remote publication and licensing can be configured when the repository is ready to share.
