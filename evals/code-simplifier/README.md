# Code simplifier evaluations

`cases.json` defines six initial scenarios and one supplemental requested-review
case. Three initial cases have executable fixtures; the other three exercise
target clarification and honest reports under capability limits.
Fixture tests establish the original contract, not the skill's effectiveness.

Run baseline checks from the repository root:

```sh
python3 -m unittest discover -s evals/code-simplifier/fixtures/python-simple -v
python3 -m unittest discover -s evals/code-simplifier/fixtures/python-dynamic -v
node --test evals/code-simplifier/fixtures/javascript-module/service.test.mjs
```

For a live evaluation, copy the case's inputs into separate scratch directories.
Use fresh agent contexts for the candidate (given the skill) and baseline (no
skill). Give each the same prompt and raw inputs without expected answers or
grading assertions. Preserve the original files and unchanged tests for grading.
Allow at most one read-only reviewer per candidate task under the skill's policy.

Inspect the patch, public signatures, effects, and report as well as running the
unchanged tests. Record source revision or skill content hash, agent/model,
prompts, checks and results, reviewer usage, and limitations in `results/`.
Do not count author self-review or passing fixture tests as live evaluations.
These small fixtures are a smoke evaluation, not broad proof of generality.

Author self-review covered the six initial scenario assertions. Actual
[0.1.0 evidence](results/0.1.0.md) records seven candidate runs, three no-skill
baseline runs, native smoke checks, and the limits of those observations.
