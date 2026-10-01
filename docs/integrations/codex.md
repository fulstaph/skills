# Codex

The repository exposes the `agent-skills` plugin from the `agent-skills`
marketplace. Its shared source is `skills/`.

## Local installation

```sh
codex plugin marketplace add /Users/georgy_bokovikov/coding/skills --json
codex plugin add agent-skills@agent-skills --json
codex plugin list --marketplace agent-skills --json
```

Use your own checkout path on another machine. Inspect existing registrations
before installing; preserve an existing marketplace with the same name until
you establish which source it uses. Host/cache writes use normal host approval.

Start a fresh session after installation so its skill inventory can refresh.
Explicitly select the code-simplifier skill and name the target file or module.
Native discovery and the exact invocation name are recorded after smoke checks
in the release evaluation report.

## Versioned distribution and updates

After a remote exists, register its actual Git URL with
`codex plugin marketplace add <git-url> --ref v0.1.0 --json`. Replace the
placeholder with the published URL; no remote is configured in this repository
yet. A tag pins the source; inspect a new release and deliberately change the
registration ref or install the new tagged checkout to update. Do not expect a
local registration to automatically track all future commits.

For a direct skill install, extract `code-simplifier-0.1.0.zip` and copy the whole
`code-simplifier/` directory, including `references/`, to a supported skill
directory. Use either this route or the native plugin route to avoid duplicate
instructions. The portable package has no executable dependencies.

The shared instructions request explicit invocation. A host's automatic skill
selection remains a host capability; the portable format does not enforce it.
