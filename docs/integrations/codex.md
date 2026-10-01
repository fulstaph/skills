# Codex

The repository exposes the `coding-skills` plugin from the `coding-skills`
marketplace. Its shared source is `skills/`.

## Local installation

```sh
codex plugin marketplace add /Users/georgy_bokovikov/coding/skills --json
codex plugin add coding-skills@coding-skills --json
codex plugin list --marketplace coding-skills --json
```

Use your own checkout path on another machine. Inspect existing registrations
before installing; preserve an existing marketplace with the same name until
you establish which source it uses. Host/cache writes use normal host approval.

Start a fresh session after installation so its skill inventory can refresh.
Explicitly select `coding-skills:code-simplifier` (for example,
`$coding-skills:code-simplifier`) and name the target file or module.
Codex CLI 0.155.1 reports that exact name as enabled in its native skill inventory,
with plugin ID `coding-skills@coding-skills`. The installed skill matches the
evaluated source. Inventory discovery was verified; a model turn launched through
the installed plugin was not run. See the release evaluation report for evidence.

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

The name `coding-skills` avoids Claude Code's reserved `agent-skills` marketplace
name while keeping both native adapters consistent. Release ZIPs retain the
generic `agent-skills-<version>.zip` archive name.
