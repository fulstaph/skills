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

Restart the session after installation. Select the plugin's code-simplifier
skill explicitly and name the target. The exact observed invocation name and
native verification extent are recorded in the release evaluation report.

## Versioned distribution and updates

When published, register the actual Git source or a checked-out release tag.
For an entirely local pinned install, extract `agent-skills-0.1.0.zip` and
register its `coding-skills/` directory. Review later releases before replacing
the pinned source and reinstalling the bundle. Consult the host's marketplace
controls for updating registrations rather than assuming local copies refresh.

For direct installation in another skills-compatible host, copy the standalone
`code-simplifier/` directory with its references. Avoid installing the same skill
both directly and through the plugin. The shared package requires no executables.

The shared instructions request explicit invocation; host-level automatic
selection is not enforced by the portable format.
