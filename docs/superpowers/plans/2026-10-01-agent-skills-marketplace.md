# Agent Skills Marketplace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a local, versioned, agent-agnostic skills marketplace with a behavior-preserving code simplifier, native Codex and Claude Code adapters, and CI/release workflows.

**Architecture:** Keep reusable instructions in `skills/code-simplifier/` and expose that directory through two native plugin manifests at the repository root. A small Python validator and packager maintain catalog, path, and release consistency outside the installed skill. Agent evaluations supply behavioral evidence separately from deterministic CI.

**Tech Stack:** Markdown, JSON, Python 3.12+, [PyYAML 6.0.3](https://pypi.org/project/PyYAML/), Python unittest/zipfile, Node.js 22+ for JavaScript evaluation fixtures, Git, GitHub Actions, installed Codex and Claude Code CLIs.

**Spec:** [Approved design](../specs/2026-10-01-code-simplifier-design.md).

## Global Constraints

- Canonical repository: `/Users/georgy_bokovikov/coding/skills`. All task file paths below are relative to that root. At the start of planning, it contained only `README.md` and the design spec, with a clean working tree on `main`.
- "Native adapters expose one plugin bundle named `agent-skills` from a marketplace also named `agent-skills`."
- "The initial bundle contains only `code-simplifier`; adding a later skill updates the shared catalog and bundle."
- "Do not require host-specific tool names, model identifiers, native invocation syntax, absolute machine paths, or another installed skill."
- "Do not add executable scripts, dependencies, or language-specific configuration to the installed skill."
- "The main agent owns scope, edits, tests, and integration. A single optional subagent provides a read-only independent review after the candidate refactor is available."
- "The reviewer must not edit files, spawn additional agents, or broaden the task."
- "Use Git history for changes and repository-wide semantic release tags, beginning with `v0.1.0` after validation."
- "CI uses read-only repository permissions. Only the release-publishing job receives repository-content write permission."
- "Paid agent calls are not part of automatic PR CI."
- Keep a portable copy and review artifacts under `/Users/georgy_bokovikov/Documents/Codex/2026-10-01/let/outputs`. Preserve existing user edits and host registrations. Host configuration writes use the normal approval flow; do not override home-directory environment variables to evade it.
- The repository remains local until publication is explicitly requested. Hosted Actions and release publication are reported as unexecuted until a remote and authorized push exist.

## Review Focus

1. Duplicate YAML fields or malformed scalar metadata must fail clearly rather than silently select a different description. Covered by Task 2.
2. Parent traversal, absolute paths, and symlinks must not let catalog entries or packaged resources escape the source package. Covered by Tasks 2 and 3.
3. A valid-looking catalog or native manifest must not hide an omitted skill, mismatched identity, or stale release version. Covered by Task 2.
4. A standalone archive must retain referenced examples, and the marketplace archive must retain hidden native manifests while excluding scratch files. Covered by Task 3.
5. Stateful/async logic, dynamic hooks, missing targets, and unavailable reviewers must retain behavior and produce honest reports. Covered by Tasks 1 and 5.

---

## File Structure and Ownership

| Files | Responsibility |
| --- | --- |
| `skills/code-simplifier/SKILL.md`, `references/examples.md` | Portable workflow and concise examples |
| `evals/code-simplifier/cases.json`, `fixtures/`, `results/` | Prompts, behavioral checks, and actual evaluation evidence |
| `VERSION`, `CHANGELOG.md`, `catalog.json` | Shared release and discovery metadata |
| `.agents/plugins/marketplace.json`, `.codex-plugin/plugin.json` | Codex adapter |
| `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json` | Claude Code adapter |
| `scripts/validate.py` | Metadata, containment, catalog, and release checks |
| `scripts/package.py` | Portable archives and changelog-derived release notes |
| `tests/helpers.py`, `test_validate.py`, `test_package.py`, `test_workflows.py` | Focused regression tests for repository tooling |
| `requirements-dev.txt`, `.gitignore` | Validator dependency and generated-file exclusions |
| `.github/workflows/ci.yml`, `release.yml` | Automatic validation and gated publication |
| `README.md`, `docs/integrations/codex.md`, `claude-code.md` | Catalog, setup, invocation, updates, and limitations |

The plan creates no separate registry service, website, paid-evaluation automation, or universal installer. The native adapters and custom catalog are views of one shared source package.

### Task 1: Portable Skill and Behavioral Evaluation Inputs

**Files:** Create `skills/code-simplifier/SKILL.md`, `skills/code-simplifier/references/examples.md`, `evals/code-simplifier/cases.json`, `evals/code-simplifier/README.md`, `evals/code-simplifier/fixtures/python-simple/{amounts.py,test_amounts.py}`, `evals/code-simplifier/fixtures/javascript-module/{service.mjs,service.test.mjs}`, `evals/code-simplifier/fixtures/python-dynamic/{hooks.py,test_hooks.py}`.

**Interfaces:** Consumes the approved spec and the Agent Skills format. Produces a package named `code-simplifier`; `cases.json` has `skill_name` and `evals`, each with `id`, `prompt`, `expected_output`, `files`, and `assertions`. Fixture checks can be run unchanged against baseline and agent-edited copies.

- [ ] **Step 1: Define the evaluation cases before writing instructions.** Include `simple-python`, `async-javascript`, `dynamic-hook`, `ambiguous-target`, `reviewer-unavailable`, and `checks-unavailable`. The async case uses interconnected production/test files, exercising independent review. The unavailable cases explicitly constrain the evaluation environment and require an honest verification report. Store prompts in `cases.json`; refer to the later Task 5 evidence procedure.
- [ ] **Step 2: Write failing behavioral checks for the three executable fixtures.** Use these concrete assertions:

```python
# python-simple/test_amounts.py
assert classify_amount(None) == "missing"
assert classify_amount(0) == "zero"
assert classify_amount(2) == "positive"
assert classify_amount(-2) == "negative"
# python-dynamic/test_hooks.py
assert dispatch("after_save", "record") == "saved:record"
# Also assert a missing dynamic name still raises KeyError.
```

For JavaScript, export `processItems(items, {validate, save, emit})` from `service.mjs`. Tests assert sequential per-item `validate`, `save`, and `emit` events; returned results in input order; and propagation of a `save` rejection with no later item or emit executed. Use Node's built-in `node:test` and assertions, with no npm packages.
- [ ] **Step 3: Run the fixture checks before their implementations exist.** Run `python3 -m unittest discover -s evals/code-simplifier/fixtures/python-simple -v`, the equivalent command for `python-dynamic`, and `node --test evals/code-simplifier/fixtures/javascript-module/service.test.mjs`. Expect missing-module/export failures.
- [ ] **Step 4: Implement intentionally verbose baseline fixtures.** `classify_amount(value: int | None) -> str` uses nested branches with the exact behavior above. `hooks.py` provides `after_save(value: str) -> str` and `dispatch(name: str, value: str) -> str`, using dynamic name lookup so the hook looks locally unused. The JS module uses explicit sequential control flow and preserves rejection and event order. These are input examples, not the simplifier implementation.
- [ ] **Step 5: Run the same checks and confirm all pass.** These passes establish fixture behavior only; do not label them successful skill evaluations.
- [ ] **Step 6: Author the portable instructions and examples.** At execution time, read the available skill-creator guidance before authoring, adapting its packaging guidance to the approved portable layout. Keep `SKILL.md` under 200 lines, with quoted `name` and `description` scalar metadata, the agreed structural scope, project conventions, original-code capture that preserves user edits, behavior/interface invariants, conditional one-reviewer delegation, verification, and concise reporting. Use generic capabilities; link `[examples](references/examples.md)`. Include Python truthiness and JS async-order examples and explain when helper extraction adds indirection. Do not add `agents/openai.yaml` or another required skill dependency.
- [ ] **Step 7: Check the instruction package against each case's assertions.** Record this as author self-review, not a live agent evaluation. Task 5 performs fresh-context runs and may revise the package.
- [ ] **Step 8: Commit this coherent deliverable.** Commit only the skill and evaluation inputs as `feat: add portable code simplifier and evaluation fixtures`.

### Task 2: Catalog, Native Manifests, and Repository Validator

**Files:** Create `VERSION`, `CHANGELOG.md`, `catalog.json`, the four native manifests listed above, `requirements-dev.txt`, `.gitignore`, `scripts/__init__.py`, `scripts/validate.py`, `tests/__init__.py`, `tests/helpers.py`, `tests/test_validate.py`.

**Interfaces:** Consumes Task 1's package. Produces `validate_repository(root: Path, expected_tag: str | None = None) -> list[str]` in `scripts/validate.py`, returning no errors on success and path-qualified diagnostics on failure. Produces `make_repository(root: Path) -> Path` in `tests/helpers.py`, constructing a minimal valid test repository, independent of the production package. CLI: `python3 scripts/validate.py --root . [--tag v0.1.0]`, exit 0 with `Validation passed`, otherwise nonzero with diagnostics.

- [ ] **Step 1: Create the test fixture helper and validator tests.** The helper writes a simple `code-simplifier` skill with description `Test refactoring skill`, a Markdown link to an existing `references/examples.md`, a matching catalog, `VERSION` containing `0.1.0`, a README, a changelog section headed `## [0.1.0] - 2026-10-01` with body `- Initial test release.`, and both root-sourced `agent-skills` native adapters. Test names/assertions include:

```python
def test_valid_repository_has_no_errors(self):
    self.assertEqual(validate_repository(self.root), [])

def test_release_tag_must_match_version(self):
    self.assertTrue(validate_repository(self.root, expected_tag="v9.9.9"))
```

Also create `test_duplicate_yaml_keys_rejected` (duplicate `name` in frontmatter), `test_non_string_description_rejected` (`description: 42`), `test_catalog_parent_escape_rejected` (`path: ../outside`), `test_absolute_catalog_path_rejected` (an absolute package path), `test_reference_escape_rejected` (link to `../outside.md`), `test_reference_symlink_rejected` (a resource symlink), `test_missing_reference_rejected` (remove the linked resource), `test_duplicate_catalog_name_rejected` (repeat an entry), `test_uncatalogued_skill_rejected` (remove its entry), `test_manifest_name_mismatch_rejected` (change one plugin name), and `test_native_version_drift_rejected` (set one manifest version to `9.9.9`). For each named rejection test, use the same diagnostic assertions after its one mutation:

```python
self.assertTrue(errors)
self.assertTrue(any(affected_file in error for error in errors))
```

Set `affected_file` to the actual mutated file's repository-relative path. The catalog-omission test names `catalog.json`; resource failures name the referring `SKILL.md`. Tests may assert the relevant field name as well without pinning complete diagnostic prose.
- [ ] **Step 2: Run `python3 -m unittest tests.test_validate -v`.** Expect missing `scripts.validate`/`validate_repository` failures.
- [ ] **Step 3: Add the tooling dependency and exclusions.** Pin `PyYAML==6.0.3` in `requirements-dev.txt`; use a repository `.venv` for implementation verification. Ignore `.venv/`, `__pycache__/`, `dist/`, evaluation run directories, and temporary `.claude/settings.local.json`; retain compact committed evaluation reports. The dependency stays outside the installed skill.
- [ ] **Step 4: Create the tooling environment.** Run `python3 -m venv .venv`; expect `.venv/bin/python` to exist. On Windows, use the corresponding `Scripts` executable path.
- [ ] **Step 5: Install the pinned validator dependency.** Run `.venv/bin/python -m pip install -r requirements-dev.txt`; expect PyYAML 6.0.3 to be installed in that environment.
- [ ] **Step 6: Implement the validator.** Parse frontmatter with a duplicate-key-rejecting subclass of `yaml.SafeLoader`, and JSON with duplicate-key rejection. Enforce the Agent Skills required types/lengths/naming; reject this repository's forbidden `allowed-tools` field. Resolve catalog paths and local Markdown resource links within their permitted root; reject absolute/parent escapes and symlinks in package inputs. External links and heading anchors are not local files. Ensure every discovered `skills/*/SKILL.md` appears once in the catalog. Check both plugin sources are `./`, shared discovery is `./skills/`, plugin/marketplace identity is `agent-skills`, version fields agree with `VERSION`, and a supplied tag matches `vX.Y.Z` and the version. Require a matching changelog release heading. Collect useful errors rather than printing a traceback for malformed user-authored data.
- [ ] **Step 7: Write production metadata and native manifests.** Set `VERSION` to `0.1.0`, catalog `schemaVersion` to 1 and `version` to `0.1.0`. The catalog contains Task 1's actual frontmatter name/description, `path: skills/code-simplifier`, and tags `coding`, `refactoring`, `readability`. Use root-sourced `agent-skills` entries in both marketplaces; Codex uses its verified local-source object, Claude uses `source: ./`. Both plugin manifests point to `./skills/` and have version `0.1.0`. Use the repository's actual Git author name where ownership is required; omit unprovided contact information and remote URLs. The changelog heading is `## [0.1.0] - 2026-10-01`, describing the initial skill, adapters, and validation without claiming evaluations already passed.
- [ ] **Step 8: Run validator tests and validate the real repository.** Run `.venv/bin/python -m unittest tests.test_validate -v` and `.venv/bin/python scripts/validate.py --root . --tag v0.1.0`. Expect all tests to pass and `Validation passed`.
- [ ] **Step 9: Run `claude plugin validate .`.** Expect successful native validation; correct schema/path problems without altering shared instructions. Codex native registration/loading remains Task 5; do not call structural checks a native-load test.
- [ ] **Step 10: Commit as `feat: add skill catalog and native marketplace validation`** with the exact files owned by this task.

### Task 3: Portable Release Packaging

**Files:** Create `scripts/package.py`, `tests/test_package.py`; modify `scripts/validate.py` only if an uncovered release condition needs a validator check.

**Interfaces:** Consumes `validate_repository` and `tests.helpers.make_repository`. Produces `package_release(root: Path, destination: Path, tag: str) -> list[Path]`, returning only the created ZIP paths, and `release_notes(root: Path, version: str) -> str` in `scripts/package.py`. Invalid release input raises `ValueError` with validator diagnostics. CLI: `python3 scripts/package.py --root . --output dist --tag v0.1.0`, producing archives and writing `dist/release-notes.md` using `release_notes`.

- [ ] **Step 1: Write packaging tests before the packager.** Test archive contents with `zipfile.ZipFile`, not byte snapshots:

```python
def test_standalone_skill_keeps_references(self):
    archives = package_release(self.root, self.output, "v0.1.0")
    skill_zip = next(p for p in archives if p.name == "code-simplifier-0.1.0.zip")
    with zipfile.ZipFile(skill_zip) as archive:
        names = set(archive.namelist())
    self.assertIn("code-simplifier/SKILL.md", names)
    self.assertIn("code-simplifier/references/examples.md", names)
```

Also test `test_marketplace_keeps_hidden_manifests`, `test_scratch_and_git_files_are_excluded`, `test_tag_mismatch_prevents_artifacts`, `test_symlink_input_is_rejected`, `test_output_path_with_spaces`, and `test_release_notes_match_requested_version`. For tag mismatch, assert the output directory has no published archives.

Use these assertions in the named tests after opening the corresponding archive or changing the single test input:

```python
self.assertIn("agent-skills/.agents/plugins/marketplace.json", names)
self.assertIn("agent-skills/.codex-plugin/plugin.json", names)
self.assertIn("agent-skills/.claude-plugin/marketplace.json", names)
self.assertIn("agent-skills/.claude-plugin/plugin.json", names)
self.assertFalse(any("/.git/" in name or "/scratch/" in name for name in names))
with self.assertRaises(ValueError):
    package_release(self.root, self.output, "v9.9.9")
self.assertEqual(len(package_release(self.root, self.output / "release files", "v0.1.0")), 2)
self.assertEqual(release_notes(self.root, "0.1.0").strip(), "- Initial test release.")
```

The symlink test points a packaged resource outside its package and asserts `ValueError` before archives appear. The scratch/Git test creates sentinel files before packaging and asserts their exclusion.
- [ ] **Step 2: Run `.venv/bin/python -m unittest tests.test_package -v`.** Expect a missing packager/function failure.
- [ ] **Step 3: Implement the two functions and CLI.** Validate before writing archives. Create `agent-skills-0.1.0.zip` rooted at `agent-skills/`, containing README, VERSION, CHANGELOG, catalog, all native manifests, shared skills, integration docs when present, and a license only if one exists. Each skill ZIP is rooted at its skill name. Use an explicit file allowlist, sorted members, and reject symlinks; exclude Git, environments, caches, eval runs, design/plan documents, tests, and repository tooling. Extract only the requested changelog section for release notes. Use filesystem APIs rather than shell command interpolation.
- [ ] **Step 4: Run packager and validator tests, then build the real archives.** Run `.venv/bin/python -m unittest tests.test_validate tests.test_package -v` and `.venv/bin/python scripts/package.py --root . --output dist --tag v0.1.0`. Expect passing tests, both archive paths, and matching release notes; inspect the ZIP member lists.
- [ ] **Step 5: Commit as `feat: package marketplace and portable skill releases`.** Generated `dist/` archives remain ignored.

### Task 4: CI/CD and Installation Documentation

**Files:** Create `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `tests/test_workflows.py`, `docs/integrations/codex.md`, `docs/integrations/claude-code.md`; modify `README.md`.

**Interfaces:** Consumes the validator/packager CLIs and fixture test commands. Produces workflows using those same interfaces and guides for the `agent-skills@agent-skills` native bundle. No model credentials or paid evaluation runner is introduced.

- [ ] **Step 1: Write workflow behavior tests.** Parse workflows with `yaml.BaseLoader` so YAML 1.1's boolean treatment of `on` does not corrupt the assertions. Test `test_ci_runs_for_pr_and_main`, `test_ci_has_read_only_permissions`, `test_release_runs_for_version_tags`, `test_publish_requires_successful_verify`, `test_only_publish_has_content_write`, and `test_release_uses_packager_and_notes_artifact`. Assert the triggers, permissions, `needs: verify`, validation/packaging command interfaces, and artifact handoff. These tests verify release gating, not all GitHub Actions runtime behavior.

```python
self.assertIn("pull_request", ci["on"])
self.assertEqual(ci["on"]["push"]["branches"], ["main"])
self.assertEqual(ci["permissions"]["contents"], "read")
self.assertEqual(release["on"]["push"]["tags"], ["v*"])
self.assertEqual(release["jobs"]["publish"]["needs"], "verify")
self.assertEqual(release["jobs"]["publish"]["permissions"]["contents"], "write")
```

Additionally assert no CI job or non-publish release job requests content-write permission, and that `verify` uploads the packager's ZIPs/notes while `publish` downloads the same artifact before publishing.
- [ ] **Step 2: Run `.venv/bin/python -m unittest tests.test_workflows -v`.** Expect missing workflow-file failures.
- [ ] **Step 3: Implement the CI workflow.** Use an Ubuntu runner and Python 3.12, install `requirements-dev.txt`, run `python scripts/validate.py --root .`, `python -m unittest discover -s tests -v`, the two Python fixture checks, and the Node fixture checks with Node 22. Use read-only permissions and bounded job timeouts. Pin referenced actions to verified immutable commits from their official repositories and record the corresponding release in a comment. Agent evaluations and authenticated native host sessions stay outside CI.
- [ ] **Step 4: Implement the release workflow.** Trigger on `v*` tags; the packager rejects tags outside `vX.Y.Z`. A read-only `verify` job repeats CI checks, passes `github.ref_name` through a quoted environment variable to the validator/packager, and uploads the archives and notes. A `publish` job with `needs: verify` downloads those exact artifacts and uses the normal repository token to create the GitHub Release with the packaged notes. Give only `publish` content-write permission. Do not interpolate untrusted expressions directly into shell program text.
- [ ] **Step 5: Write the README and integration guides.** Document the human catalog, custom catalog schema, optional capabilities, local commands, tag-pinned distribution, deliberate updates, manual evaluations, and release prerequisites. Codex commands verified locally are `codex plugin marketplace add /Users/georgy_bokovikov/coding/skills --json`, `codex plugin add agent-skills@agent-skills --json`, and `codex plugin list --marketplace agent-skills --json`; for distribution, explain the supported Git `--ref` option without inventing a remote. Claude commands are `claude plugin validate .`, `claude plugin marketplace add <local-path>`, and `claude plugin install agent-skills@agent-skills`. Document actual verified native skill namespacing after Task 5, plus direct copying of the standalone skill for other hosts. Clearly distinguish manual direct installation from native installation to avoid duplicates.
- [ ] **Step 6: Run all repository tests, validation, fixture checks, and packaging locally.** Expect passing results and complete archives. If available, run a workflow linter as an additional check; report whether it ran. Native validation/loading and hosted Actions execution remain separate evidence categories.
- [ ] **Step 7: Commit as `ci: validate and release the skills marketplace`.** The workflow files are committed but will not run on a hosting service until an authorized push.

### Task 5: Live Evaluations, Native Smoke Checks, and Initial Local Release

**Files:** Create `evals/code-simplifier/results/0.1.0.md`; update `evals/code-simplifier/README.md`, `CHANGELOG.md`, the integration guides, and any skill instructions whose evaluations fail. Retain user deliverables under the projectless workspace's `outputs/` directory.

**Interfaces:** Consumes all previous deliverables. Produces evidence tied to the exact tested source revision, a validated local `v0.1.0` tag and release archives, and an installed Codex bundle or a precise report of an external installation block.

- [ ] **Step 1: Run clean-context candidate and baseline evaluations.** Copy each fixture into separate scratch directories outside the source package, keeping original inputs for comparison. Run the executable cases with and without the candidate skill; for later iterations, use the prior skill snapshot as baseline. Use isolated subagent contexts or another available fresh-context mechanism; do not create user-owned chats without explicit authorization. For the ambiguous case, supply no target and assert a scope question precedes edits. For unavailable-review and unavailable-check cases, assert no false claim of independent review or executed tests. Candidate runs must honor the core skill's one-read-only-reviewer rule when that capability is available; baseline runs have no supplied skill.
- [ ] **Step 2: Grade actual outputs.** Run the unchanged fixture checks against each candidate patch, compare public names/signatures and JS event order, inspect dynamic-hook retention, review readability and scope, and record actual reviewer usage. Record agent/model when available, source revision or content hash, prompts, executed commands, outcomes, and limitations. Use `not run` for unavailable cases; do not substitute author self-review or passing baseline fixtures for an executed evaluation.
- [ ] **Step 3: Correct supported skill failures and rerun affected evaluations/checks.** Revalidate catalog description if frontmatter changes. Leave uncertain transformations out of sample patches and ensure the report accurately explains the gaps. Commit evaluation evidence and any fixes as `test: record code simplifier evaluation evidence`.
- [ ] **Step 4: Validate and smoke-test native adapters.** Inspect existing Codex/Claude marketplaces and installations first; preserve conflicting names and existing user settings. Run `claude plugin validate .` and record its result. Register/install the requested bundle in Codex using the Task 4 commands, then confirm the installed manifest and `skills/code-simplifier/SKILL.md` are present and the plugin is enabled. Check actual native discovery/invocation if available; record the extent of verification. For Claude, use `--scope local` for registration/install smoke checks from a temporary project so the repository does not acquire published user configuration; verify the bundle appears in `claude plugin list --json` and its skill inventory where supported, then remove only test-created local registration/install state. Use normal approvals for host/cache writes and report any native block without bypassing it.
- [ ] **Step 5: Perform the execution method's independent final review.** If Native was selected, one fresh read-only reviewer on the most capable available model checks the complete repository diff against the approved spec, including skill semantics, catalog/manifests, artifact contents, workflow permissions, and evidence claims. If Subagent-driven was selected, retain its task reviews and whole-branch review. Resolve supported findings and rerun affected checks. Update evidence and integration docs to match the final package. A review of runtime logic should include the original working-copy state, not just Git HEAD.
- [ ] **Step 6: Run the final local validation suite and commit the reviewed source.** Run all Task 4 checks, `claude plugin validate .`, and the real packaging command. Ensure `git diff --check` passes, user work remains intact, and the report distinguishes local/native checks from hosted checks. Commit changes as `chore: finalize agent skills v0.1.0` if there are remaining changes.
- [ ] **Step 7: Create the initial local release tag only after the checks and review pass.** Confirm `v0.1.0` does not exist, then run `git tag -a v0.1.0 -m "Agent skills marketplace v0.1.0"`. Produce final archives from a clean extraction of that tagged source with the packager, rather than including ignored local files. If installation or evaluation blockers remain, leave the release untagged and report exactly what remains.
- [ ] **Step 8: Retain and show the deliverables.** Copy the standalone skill directory to `/Users/georgy_bokovikov/Documents/Codex/2026-10-01/let/outputs/code-simplifier/`; copy both release ZIPs, release notes, and the evaluation report under `outputs/`. Compare the retained package with tagged source. Report repository location, commit/tag, Codex installation result, Claude verification extent, evaluation results, and local CI results. Hosted CI and remote publication remain unexecuted while the repository has no remote.

## Plan Self-Review

- Spec coverage: Task 1 covers portable instructions, structural scope, invariants, reviewer policy, and evaluation inputs; Task 2 covers catalog/native metadata/versions; Task 3 covers distribution artifacts; Task 4 covers documentation/CI/CD; Task 5 covers actual evaluations, native installation, review, and local release.
- Interface consistency: `validate_repository`, `package_release`, `release_notes`, and `make_repository` are defined once and referenced by the same names. CLI root/output/tag flags are stable across tests, workflows, and documentation.
- Review focus: each of the five listed failure classes has named tests or an actual behavioral evaluation procedure in its owning task.
- Verification limits: structural tests, fixture baselines, live evaluations, native loading, local archive checks, and hosted workflow runs are recorded separately.
- Proportion: the plan specifies contracts, assertions, commands, and task boundaries; implementation bodies are left to the implementer. No product files have been created during planning.

## Execution Handoff

The user must review this written plan and choose an execution method before implementation. The earlier approval of optional subagents inside the resulting simplifier skill does not select how this repository will be implemented.

Recommended method: **Native**, implementing tasks in this session with one independent final reviewer. The validator, catalog, adapters, and packager share interfaces and release metadata, so a single implementation context avoids repeated setup. **Subagent-driven** remains available for a fresh implementer and reviewers at each task boundary, followed by whole-branch review.
