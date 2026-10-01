# Agent Skills Marketplace and Code Simplifier Design

Date: 2026-10-01
Status: Ready for written-spec review

## Purpose and agreed intent

Create a general-purpose, agent-agnostic skill named `code-simplifier` that refactors a user-selected file or module to reduce complexity and improve readability and maintainability. Keep its source in the local Git repository `/Users/georgy_bokovikov/coding/skills`.

The user selected structural refactoring: the skill may extract helpers and reorganize responsibilities while preserving behavior and public interfaces. It adapts to each project's language, framework, and conventions. The user approved an optional independent subagent review for larger or behaviorally subtle changes.

The design assumes explicit invocation and direct editing. Both assumptions were presented as part of the approved design. The skill is a reusable instruction package, not a separate program or a language-specific static-analysis tool.

The user additionally requested agent portability, Git-based distribution and versioning, and creation of a repository named `skills` in their `coding` directory. Codex is the first installation target; the shared instructions must not depend on Codex.

The user approved treating the repository as a curated, Git-backed skill marketplace, including both Codex and Claude Code marketplace integrations in the first release. `code-simplifier` is its first skill. The initial marketplace is a repository catalog with native installation adapters; future skills can use the same layout and release process.

The user also approved automated repository validation and tagged-release publishing, with agent evaluations run manually before releasing changes to a skill. CI/CD configuration is part of the source repository and introduces no runtime requirement for installed skills.

## Selected approach

Use a concise guided workflow with concrete boundaries and examples. A rules-only checklist offers less guidance for scope and verification; a tooling-driven system adds dependencies and favors particular languages. A guided skill can use the tools already available in a project without requiring new infrastructure.

The installed ECC `code-simplifier` agent is a local reference for clarity and consistency principles. Its default focus on recently modified code differs from this skill's explicit file-or-module scope. The new skill must express the agreed workflow independently and omit unrelated agent instructions.

## Repository, package, and portability

The canonical source repository is `/Users/georgy_bokovikov/coding/skills`, with the skill in `skills/code-simplifier/`. Its package contains:

- `SKILL.md`: discovery metadata, invocation guidance, refactoring workflow, invariants, subagent policy, and completion requirements.
- `references/examples.md`: short examples showing useful structural simplification and tempting changes that alter behavior.

Follow the shared [Agent Skills specification](https://agentskills.io/specification): YAML frontmatter with `name` and `description`, followed by Markdown instructions and relative resource links. The skill name must match its directory name. Keep the main instructions concise and load examples only when useful.

Use ordinary capability descriptions such as reading files, editing code, running project checks, and delegating a review. Do not require host-specific tool names, model identifiers, native invocation syntax, absolute machine paths, or another installed skill. Do not use experimental tool-allowlist metadata in the shared package. Optional reviewers remain capability-dependent.

Agent Skills-compatible hosts can discover the package using their supported installation mechanism. Other coding agents can be explicitly directed to read and follow `SKILL.md`; automatic discovery and native invocation are not promised for every host.

Agent-specific setup belongs in repository integration documentation and marketplace/plugin manifests outside the shared skill package. Codex per-skill display metadata is optional, not a required core file. The initial shared package omits `agents/openai.yaml`; a future host-specific overlay may add it without changing the shared workflow. Explicit invocation is expressed in the shared description and body. A host may additionally support metadata that enforces explicit-only activation, but the shared format alone does not enforce that policy.

Do not add executable scripts, dependencies, or language-specific configuration to the installed skill. Evaluation fixtures and validation tooling may live separately in the source repository.

Repository documentation comprises a README with the human-readable catalog, purpose, installation, and invocation; separate Codex and Claude Code integration guides; a changelog for releases; this design spec; and the implementation plan after its review gate. Keep representative evaluation scenarios and results alongside the source, outside the installed skill directory.

After implementation validation, register the local marketplace and install its native bundle into Codex so it can be used across projects. Inspect existing registrations and installations before writing and preserve existing content. Direct installation of `skills/code-simplifier/` into a host's skill directory remains a documented alternative; use one installation method per host to avoid duplicate discovery. Keep the initial Claude Code scope to adapter validation and a local load/install smoke check when possible. Document any check that requires unavailable capabilities. Do not change the cached ECC or Superpowers plugins.

Retain a portable copy at `outputs/code-simplifier/` and keep this spec's user-facing copy synchronized with the repository document. The Git repository is the source of truth; installed copies are release artifacts, and changes made there must be brought back into source before release.

## Curated marketplace and native adapters

The root README is the human catalog. A custom `catalog.json` is the machine-readable index, with `schemaVersion`, repository release `version`, and a `skills` array. Each skill entry contains `name`, repository-relative `path`, `description`, and `tags`. Names and descriptions match the corresponding `SKILL.md` frontmatter; paths identify existing packages inside the repository. Explain the schema in the README and validate consistency. An agent can explicitly read the index to select a skill; the index itself does not promise automatic discovery by every host.

Native adapters expose one plugin bundle named `agent-skills` from a marketplace also named `agent-skills`. Keep marketplace entry names and plugin names consistent. Both bundles use the repository root as their plugin source and discover the same `skills/` directory. This avoids duplicated skill instructions and paths that escape a cached plugin root. The initial bundle contains only `code-simplifier`; adding a later skill updates the shared catalog and bundle.

The repository layout includes:

```text
skills/
  README.md
  VERSION
  CHANGELOG.md
  catalog.json
  .agents/plugins/marketplace.json
  .codex-plugin/plugin.json
  .claude-plugin/marketplace.json
  .claude-plugin/plugin.json
  .github/workflows/
    ci.yml
    release.yml
  skills/code-simplifier/
    SKILL.md
    references/examples.md
  docs/integrations/
    codex.md
    claude-code.md
  docs/superpowers/specs/
  docs/superpowers/plans/
  evals/
  scripts/
  tests/
```

Codex's marketplace adapter follows the current installed marketplace format at `.agents/plugins/marketplace.json`, paired with `.codex-plugin/plugin.json`. The local Codex CLI supports registration of local or Git marketplace sources. Use its available commands to confirm discovery, registration, installation, and loaded skill paths during implementation.

Claude Code uses `.claude-plugin/marketplace.json` with marketplace ownership and plugin source metadata, and `.claude-plugin/plugin.json` for the bundle. Follow its [marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces) and [manifest reference](https://code.claude.com/docs/en/plugins-reference). Validate the files and exercise local loading or installation with the installed CLI. Integration guides describe each host's native namespacing and invocation.

Use actual repository Git identity where ownership metadata is required, without inventing contact addresses or a future remote URL. Omit optional public URLs until there is a real hosted repository. The manifests carry only the shared skills and required descriptive metadata; no additional runtime component is needed.

## Versioning and distribution

Use Git history for changes and repository-wide semantic release tags, beginning with `v0.1.0` after validation. Do not tag the incomplete documentation-only repository as a release. A root `VERSION` file defines the bundle release, and both native plugin manifests and the custom catalog must agree with it. Patch versions clarify or correct instructions within the existing contract; minor versions add compatible capabilities; major versions change defaults, scope, or required capabilities. The changelog explains relevant behavior changes and verification evidence.

Distribute the marketplace through local registration initially and through the Git repository when a remote is configured. Document native installation for Codex and Claude Code and a direct, tag-pinned skill-directory installation for other agents. A GitHub remote can additionally support the existing Codex repository/path/ref skill installer. Installers and marketplace clients are host integrations, not dependencies of the shared skill.

The repository supplies immutable release tags and documents deliberate, version-aware updates. Native marketplace clients manage their own caches and update behavior; describe and verify each available host's mechanism rather than claiming all clients automatically pin the same way. Direct-copy updates preserve local modifications: inspect the installed copy, back it up if necessary, and replace it with the selected release. The existing Codex skill installer rejects an already-existing destination; it does not provide automatic upgrades. Do not add a custom runtime updater.

The current request creates a local Git repository. Remote hosting, visibility, and publication licensing are selected when publication is requested.

## CI/CD and evaluation policy

Use GitHub Actions for repository CI and release publishing once the repository is hosted on GitHub. Keep the same deterministic validation and packaging commands runnable locally, so the repository remains usable before remote setup and with another Git host.

The CI workflow runs on pull requests and pushes to `main`. It checks:

- Shared skill frontmatter, directory names, required metadata, and resource references.
- Unique catalog entries, agreement with skill metadata, and package paths contained in the repository.
- Native marketplace/plugin manifest structure, names, component paths, and shared-package discovery configuration.
- Release version consistency across `VERSION`, the catalog, and emitted native version fields.
- Focused tests of the validation and packaging helpers, including invalid metadata, missing files, and inconsistent versions.
- Executable evaluation-fixture checks where provided. These verify behavior specifications and evaluation helpers; they do not by themselves demonstrate that an agent followed the skill successfully.

Use native host validators where the runner supports them without agent credentials. Otherwise, repository checks cover the manifest structure and paths, and native validation/loading is reported separately from the local smoke checks. CI must not silently present structural checks as proof of native loading.

Agent evaluations remain a manual development and pre-release step initially. Run representative prompts in a fresh context against the candidate skill and a baseline or previous version, then assess concrete outputs. For refactoring cases, run behavioral tests against the produced patch and inspect readability, scope, and interface preservation. Record the skill revision, agent/model when known, scenarios, executed checks, results, and limitations. The [Agent Skills evaluation guide](https://agentskills.io/skill-creation/evaluating-skills) supplies the baseline-comparison approach. Paid agent calls are not part of automatic PR CI.

Before releasing changed skill instructions, run the relevant manual evaluations and review their evidence. Keep this human release requirement distinct from automated schema and fixture checks. The initial release evaluates the acceptance scenarios described below.

The release workflow runs when a maintainer pushes a version tag in the form `vX.Y.Z`. It reruns deterministic validation, verifies that the tag agrees with release metadata and the corresponding changelog entry, and builds a marketplace archive plus separate portable skill archives from the tagged source. Publish a GitHub Release containing those archives and release notes only after verification passes. Include the native manifest directories in the marketplace archive and retain the directory structure of each standalone skill.

CI uses read-only repository permissions. Only the release-publishing job receives repository-content write permission. Publication uses the repository's normal workflow credentials; no agent API credentials are needed for these two workflows. A future evaluation automation can be designed separately if manual evaluation becomes a bottleneck.

Local validation, archive creation, and workflow review are part of implementation verification. Running hosted Actions or publishing a GitHub Release requires a configured remote and an authorized push. Report that distinction explicitly while the repository remains local.

## Invocation and scope

Typical use: invoke the skill by the host's supported mechanism and provide a file, directory representing a module, or a clearly identified module in the current conversation. Codex's `$code-simplifier` syntax belongs in its integration documentation rather than the shared workflow.

Use the explicit target or an unambiguous target already established by the user. If neither exists, ask one focused question before editing. Do not silently fall back to all recently changed files or the whole repository.

Read adjacent callers, tests, configuration, and contracts to understand the target. Edits stay within the selected target and the minimum supporting files necessary for the same refactor, such as a colocated helper or a focused test. If a change requires unrelated work, a public-interface change, or an expansion to another subsystem, leave that change as a proposal and continue any independent simplifications already within scope.

## Refactoring workflow

1. Read applicable project instructions and inspect the working-tree state. Identify and preserve the user's existing edits.
2. Inspect the selected code, relevant callers, tests, and language or framework conventions. Identify public boundaries and behavior that must stay stable.
3. Establish the relevant verification baseline using available project checks. Inspect a failure enough to distinguish an existing problem from one introduced by the refactor; do not fix unrelated failures automatically.
4. Identify a small set of improvements with a concrete readability benefit. Briefly communicate the intended edits and proceed within the authorized scope; the skill adds no routine approval gate of its own.
5. Apply cohesive changes. Prefer clear control flow, descriptive internal names, useful responsibility boundaries, and fewer competing abstractions.
6. Use optional independent review when warranted by the policy below. Resolve supported findings before completion.
7. Run relevant checks and review the final diff for unintended behavior or scope changes. Report the resulting improvements and the verification evidence.

## Simplification rules

Useful changes include reducing unnecessary nesting, introducing guard clauses where equivalent, extracting helpers that name a coherent responsibility, clarifying internal names, removing redundant indirection, and consolidating genuinely equivalent duplicated logic.

Extraction and consolidation are choices, not quotas. Keep straightforward code inline when a helper would add navigation or indirection without clarifying it. Do not create a generalized framework for a single use case. Do not optimize for the shortest code, line-count reduction, or a complexity score.

Follow the existing project's idioms. Remove dead code or unused imports only when their lack of use and side effects is supported by evidence. Account for reflection, registries, dynamic loading, import-time execution, framework hooks, and generated interfaces before removal. Do not remove logging, validation, error handling, or comments explaining constraints merely because they look verbose.

## Behavior and interface invariants

Preserve externally observable behavior, including return values, output formats, errors and their handling, validation, mutation, side effects and their ordering, resource cleanup, and contractual ordering or concurrency behavior.

Preserve public exports, function signatures, protocols, serialization formats, and framework-discovered entry points. Renaming an internal implementation detail is allowed only when its actual consumers remain compatible. Avoid changing dependency versions or adding dependencies for a refactor.

Treat transformations involving asynchronous code, lazy evaluation, truthiness, coercion, ownership, aliasing, evaluation order, floating-point operations, or resource lifetimes as behavior-sensitive. Inspect the semantics for the project's language before applying them. Do not mechanically replace callback chains with async/await or merge branches that have different effects.

If equivalence cannot be established with reasonable evidence, keep the uncertain transformation out of the patch and explain the opportunity or verification gap. An empty patch is acceptable when the code is already clear or no supported improvement exists.

## Optional subagent review

The main agent owns scope, edits, tests, and integration. A single optional subagent provides a read-only independent review after the candidate refactor is available.

Use the reviewer when the diff crosses interconnected files or changes logic with subtle state, errors, side-effect ordering, or asynchronous behavior. Ordinary local simplifications can remain with the main agent. Honor a user's request to enable or skip review.

Give the reviewer the target, applicable instructions, preserved contracts, the original code or a trustworthy before/after comparison that includes pre-existing user edits, the candidate diff, and verification results. A Git HEAD comparison alone is insufficient if the original target already contained uncommitted changes. Ask for concrete findings about behavioral drift, interface changes, scope expansion, or abstractions that make the code harder to understand. Each finding should identify the code and a plausible behavioral or maintenance consequence.

The reviewer must not edit files, spawn additional agents, or broaden the task. The main agent assesses each finding, resolves supported issues, and reruns checks affected by its corrections. Reviewer agreement supports the assessment; it does not replace tests or prove equivalence.

If subagents are unavailable, perform the same review in the main agent and report that independent review was unavailable. Do not fail or require additional setup solely because subagent tooling is missing.

## Verification and failure handling

Use existing tests, type checks, builds, and lint checks that cover the changed code. Prefer focused checks; run broader checks when the project requires them or the refactor affects shared behavior. Do not install tools solely to satisfy a generic checklist.

Add targeted behavioral or characterization tests when the transformation introduces material uncertainty and existing coverage does not resolve it. Avoid tests that simply mirror implementation details or exist only to accompany a low-impact edit.

If a refactor introduces a failure, correct or remove the agent's failing change while preserving pre-existing user work. Do not use a blanket reset or revert of the entire working tree. Report pre-existing failures separately from introduced failures.

When relevant checks cannot run, state the reason and distinguish static review from executed verification. Leave uncertain transformations unapplied. Never claim that behavior was proved unchanged just because checks passed.

The completion response briefly states what became simpler, which checks ran and their outcome, any limitations or skipped transformations, and any independent review findings that remain unresolved. Do not create commits or pull requests automatically unless the user or project instructions authorize them.

## Skill validation and acceptance criteria

Validate the package's required frontmatter, naming, file references, and core instructions against the shared Agent Skills format using available validators during implementation. Check that the shared package has no host-specific tool or invocation requirements and that optional review degrades cleanly when unavailable. Separately validate the custom catalog, release-version consistency, and both native marketplace adapters. Verify the first Codex native installation using local integration guidance and perform an available Claude Code native smoke check. Distinguish schema validation from actual host loading in the results.

Evaluate representative scenarios rather than only checking the instruction text:

1. A straightforward single-file refactor produces a readable equivalent result with no unnecessary helper hierarchy or subagent use.
2. An interconnected module exercises the optional reviewer and retains public contracts, error behavior, and side-effect ordering.
3. A second language exercises language-appropriate reasoning instead of applying JavaScript-specific habits everywhere.
4. An ambiguous target prompts a focused scope question before any edit.
5. A dynamic or framework-discovered entry point is retained despite appearing locally unused.
6. Missing subagents or unavailable tests produce an honest limitation report without a false verification claim.
7. An agent without Codex tools can follow the core workflow; host-specific setup and invocation stay in integration documentation.
8. Both native adapters expose the same shared package, custom catalog entries resolve to existing skills, and release metadata agrees across all representations.
9. Local deterministic CI commands pass; validation rejects malformed packages; release archives contain the expected shared and native files; and a mismatched release tag is rejected. Hosted workflow execution and publication are recorded separately from local checks.

Use focused executable before/after checks for scenarios with concrete behavioral claims. Record what was executed, what was inspected, and what remains unverified. Revise the skill if an evaluation reveals a failure.

Acceptance requires a valid, concise Agent Skills package in the requested Git repository; behavior-preserving structural scope; no mandatory host-specific capabilities or new dependencies in the skill; optional read-only subagent review with a fallback; a consistent human and machine-readable catalog; validated Codex and Claude Code marketplace integrations; CI and release workflows with passing local validation and packaging checks; documented manual evaluation evidence; documented releases and installation; and a retained portable copy plus a confirmed first Codex native installation, or a clear report of a specific installation block. Report the exact extent of Claude Code loading verification and hosted CI/CD execution.

## Review and implementation handoff

This spec is the next review artifact. Written-spec approval permits the Superpowers writing-plans stage. Implementation begins only after the user reviews the resulting implementation plan and selects its execution method, as required by the explicitly invoked brainstorming workflow.

The requested local source repository now supplies version control for the design document. Keep the projectless workspace copy available for review, and record design approval before starting the implementation-plan stage.
