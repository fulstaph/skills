---
name: "code-simplifier"
description: "Simplify selected code for clarity and maintainability while preserving behavior and public interfaces. Use when explicitly asked to simplify or refactor a file, module, or defined change scope, including useful helper extraction and reducing unnecessary complexity."
---

# Code simplifier

Make the selected code easier to understand and maintain. Preserve observable
behavior and public interfaces. Favor clear structure over fewer lines.

## Establish scope and a baseline

1. Identify the requested file, module, or explicit change scope. If the target
   cannot be inferred from the conversation, ask one focused question before
   editing. Do not choose a repository-wide cleanup on the user's behalf.
2. Read applicable repository instructions, the target code, its callers, and
   nearby tests. Follow the project's language idioms, naming, formatting, and
   architecture. Trace relevant interactions outside scope without editing them.
3. Inspect existing working-copy changes. Capture the actual pre-edit files or
   diff, including uncommitted user work, so review compares against the real
   starting point. Do not reset, overwrite, or discard unrelated changes.
4. Identify the contracts that must remain: names and signatures, return values,
   serialization and persistence formats, errors, side effects, ordering,
   state transitions, timing, async behavior, and resource lifetimes.
   Find reflective, registered, exported, or dynamically called code before
   treating an apparently unused symbol as dead.
5. Identify focused checks that cover those contracts. Run existing relevant
   checks before editing when practical; retain any baseline failures.

## Simplify deliberately

- Reduce unnecessary nesting, duplicated logic, redundant state, and confusing
  names. Prefer straightforward branches and explicit data flow.
- Extract a helper when it names a coherent responsibility, makes repetition
  safer, or clarifies a complex step. Keep simple logic together when extraction
  would force readers to jump around without adding understanding.
- Reorganize responsibilities within the agreed scope when it improves clarity.
  Avoid speculative abstractions, new dependencies, feature changes, public API
  changes, and unrelated formatting churn.
- Preserve language-specific distinctions such as missing versus false-like
  values, equality and coercion, evaluation order, laziness, exceptions,
  cancellation, transaction boundaries, and sequential versus concurrent work.
  Do not replace sequential async work with parallel work merely for brevity.
- Remove code only with evidence it has no relevant callers or side effects.
  When equivalence is uncertain, retain the original construct and report why.
- Make changes in small coherent steps. Stop when the code is clearly improved;
  leave it unchanged when every proposed simplification adds risk or indirection.

Consult the [examples](references/examples.md) for common tradeoffs.

## Review and verify

1. Compare the candidate with the captured working-copy baseline. Check scope,
   contracts, project conventions, and whether the result is actually clearer.
2. If a read-only independent reviewer is available, use **at most one** when
   interconnected files or subtle state, async, or error paths warrant another
   perspective. Simple local changes need no delegation.
   Give the reviewer the request, scope, relevant original files or diff,
   candidate changes, contracts, and actual check results. Ask for concrete
   behavior regressions, scope creep, and readability problems. The reviewer
   must not edit files, spawn agents, or broaden scope. The main agent owns all
   edits, verification, and integration.
3. If review is unavailable, continue with an explicit self-review. Do not imply
   an independent review occurred. Assess findings yourself and keep only
   supported changes; review is evidence, not a substitute for checks.
4. Run relevant tests and any required project checks. Add a focused regression
   check only when an important behavior lacks coverage; do not rewrite tests
   to accept altered behavior. Compare failures with the baseline.
5. Reinspect the final diff and working-copy state for accidental changes.
   If checks cannot run, state the limitation and use conservative inspection;
   do not claim that tests passed or equivalence was proven.

## Report

Briefly describe what became clearer, the scope changed, checks actually run and
their outcomes, review used when relevant, and any remaining uncertainty or
intentionally retained complexity. If no edit improves the code safely, say so.
