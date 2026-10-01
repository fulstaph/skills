# Agent Skills

A curated Git-backed marketplace of reusable coding-agent skills using the
[Agent Skills format](https://agentskills.io/specification). Each portable
package contains instructions and relative resources. Host-specific discovery
lives in small native adapters outside the package.

## Catalog

| Skill | Purpose | Optional capability |
| --- | --- | --- |
| [code-simplifier](skills/code-simplifier/SKILL.md) | Simplify a selected file, module, or change scope while preserving behavior and public interfaces | One read-only reviewer for subtle or interconnected changes |

Ask the agent to use code-simplifier and name a target, for example:
“Use code-simplifier to simplify the payment module while preserving behavior.”
The skill can extract useful helpers and reorganize responsibilities within
scope. It follows project conventions and reports actual checks and limitations.

## Install

The `coding-skills` marketplace exposes one bundle, `coding-skills`, backed by
the shared `skills/` directory:

- [Codex native setup](docs/integrations/codex.md)
- [Claude Code native setup](docs/integrations/claude-code.md)
- Other compatible hosts: extract the standalone skill ZIP and copy the entire
  `code-simplifier/` directory, including `references/`, into a supported skill
  directory. Select a release deliberately and preserve local modifications.

Choose one installation route per host to avoid duplicate skills. Native skill
selection follows host conventions. The core skill requires no other installed
skill, executable dependency, or subagent support.

## Development checks

Repository tooling uses Python 3.12+ and PyYAML; the JavaScript behavior fixture
uses Node.js 22+. These dependencies are not installed with the skill.
Development commands and evaluation/design links apply to the full Git checkout.
The marketplace ZIP contains the portable skills and integration guides.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py --root .
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m unittest discover -s evals/code-simplifier/fixtures/python-simple -v
.venv/bin/python -m unittest discover -s evals/code-simplifier/fixtures/python-dynamic -v
node --test evals/code-simplifier/fixtures/javascript-module/service.test.mjs
.venv/bin/python scripts/package.py --root . --output dist --tag v0.1.0
```

On Windows use the virtual environment's `Scripts/python.exe` executable.
Validation checks duplicate fields, skill metadata, relative resource containment,
catalog completeness, native adapter identities, and release versions. Packaging
creates `agent-skills-0.1.0.zip`, one ZIP per skill, and changelog-derived notes.
Archives include native manifests and resources and exclude development files.

## Catalog and contributions

`catalog.json` is this repository's small discovery index, not a cross-host
marketplace standard. Schema version 1 has a repository `version` and `skills`
array. Each entry has `name`, `description`, `path` (`skills/<name>`), and `tags`.
Name and description must match the package's frontmatter exactly. Every package
appears once. Native adapters expose the whole curated bundle.

To add a skill, create `skills/<name>/SKILL.md`, add relative resources as needed,
update both the catalog and this table, and provide representative manual
evaluations. Keep host-specific details outside the shared package. Run the
local checks before submitting changes.
Packaging rejects a skill named `agent-skills` because its standalone archive
would collide with the marketplace archive. Required references must survive
archive filtering; links into excluded scratch/cache directories fail packaging.

## Versioning and releases

All skills and adapters share `VERSION`, initially `0.1.0`, and repository tags
of the form `vX.Y.Z`. Update the catalog, both plugin manifests, both marketplace
plugin entries, and [CHANGELOG.md](CHANGELOG.md) together. Use patch versions for
clarifications without intended behavior changes, minor versions for added
skills/capabilities, and major versions for incompatible contracts. Before 1.0,
document breaking changes explicitly even when using a minor release.

CI checks pull requests and updates to `main` with read-only permissions. Tag
releases repeat validation and tests, package the tagged source, and pass the
same archives and notes to a separate publication job. Only that job has content
write permission. Action revisions are pinned to official immutable commits.

Before pushing a release tag, run [manual evaluations](evals/code-simplifier/README.md)
with fresh candidate and baseline contexts, review their evidence, and smoke-test
native adapters. Hosted CI checks metadata and original fixture behavior; it
does not run paid agent evaluations or authenticated host sessions. These
evidence categories are reported separately.

Source: [fulstaph/skills](https://github.com/fulstaph/skills).
GitHub runs validation for pull requests and changes to `main`. Pushing a version
tag runs the release workflow and publishes verified ZIPs with release notes.
Install from a selected tag and review later releases before updating.

The approved [design](docs/superpowers/specs/2026-10-01-code-simplifier-design.md)
and [implementation plan](docs/superpowers/plans/2026-10-01-agent-skills-marketplace.md)
record the initial decisions.
