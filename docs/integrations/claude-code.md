# Claude Code

Both native manifests expose the shared `skills/` directory through the
`coding-skills@coding-skills` bundle.

## Local installation

From the checkout:

```sh
claude plugin validate .
claude plugin marketplace add /path/to/skills
claude plugin install coding-skills@coding-skills
claude plugin list --json
```

Use your actual path. Registration and installation normally use user scope.
For a temporary project smoke check, add `--scope local` to both registration
and installation commands. Inspect existing registrations first and remove
only the state created by the smoke check.

Restart the session after installation. Claude's documented plugin skill syntax
is `/coding-skills:code-simplifier`; name the target in the request. The initial
smoke check used Claude Code 2.1.110: native validation, local registration,
installation, enabled-plugin listing, and matching installed skill files all
passed. Its plugin CLI exposes no skill inventory command; an actual slash-command
invocation was not run. The temporary local installation and registration were
removed after the check, restoring the previously empty listings.

`agent-skills` is reserved by Claude Code for official Anthropic marketplace
sources. Both adapters therefore use `coding-skills`. The portable archive is
still named `agent-skills-<version>.zip`.

## Versioned distribution and updates

When published, register the actual Git source or a checked-out release tag.
For an entirely local pinned install, extract `agent-skills-0.1.0.zip` and
register its `agent-skills/` directory. Review later releases before replacing
the pinned source and reinstalling the bundle. Consult the host's marketplace
controls for updating registrations rather than assuming local copies refresh.

For direct installation in another skills-compatible host, copy the standalone
`code-simplifier/` directory with its references. Avoid installing the same skill
both directly and through the plugin. The shared package requires no executables.

The shared instructions request explicit invocation; host-level automatic
selection is not enforced by the portable format.
