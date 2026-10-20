# Agent maintenance procedure

Use this procedure when asked to install or update dotagents, or when executing a
recurring update the user has explicitly requested. No recurring job is installed
by default. Do not create one just because dotagents is installed.

## First installation

1. Follow the clone instructions in [README.md](README.md). Keep the checkout at
   its permanent location; the local plugin marketplace and MCP launchers reference it.
2. Select the requested agents (`--agent all`, `claude`, or `codex`), whether MCP
   is wanted, and any documented destination overrides. With the selected clients
   closed for MCP changes, run `python3 update.py --install --with-mcp` from the
   checkout, adding `--agent` if needed. Omit `--with-mcp` for skills only.
   This installs and records the recipe. Do not print or commit credentials.
3. Complete [MCP setup](mcp/README.md) on the destination machine. Installation
   alone does not supply tokens, install server dependencies, or verify services.
4. Restart clients and perform the verification below.

Existing standalone installations with version-1 profiles must first pull the
plugin release with `git pull --ff-only`, then register their original agent/MCP
options and legacy directory overrides using `update.py --install`. Set the intended
`CODEX_HOME` and `CLAUDE_CONFIG_DIR` for nonstandard plugin homes. Version-2 profiles
save those homes. Do not guess a missing installation scope. Legacy skill links
are removed only after that agent's plugin installs successfully.

## Requested or scheduled updates

1. Locate the permanent checkout and its `.dotagents-install.json`. Missing or
   invalid settings require registering the intended installation first.
2. Run `python3 /absolute/path/to/dotagents/update.py --dry-run`. This fetches
   metadata and reports the revision change; it does not preview the incoming
   revision's configuration changes. Git authentication must already work without
   interaction for unattended jobs.
3. For all plugin or MCP updates, apply during a maintenance window when the
   selected clients are closed. An agent running inside one of those clients can
   perform the Git preview, but should hand off the apply command to an external
   terminal or authorized scheduler after the client exits. Do not kill clients
   or assume atomic writes prevent all concurrent configuration changes.
4. Run `python3 /absolute/path/to/dotagents/update.py`. It fast-forwards and runs
   the updated installer, including a configuration preview. Preserve the output
   and exit status. Do not report successful authentication from exit status alone.
5. Restart the selected clients and verify. Report the old/new revisions, scope,
   preserved entries, and any verification still pending.

When the user requests a recurring job, establish the interval and maintenance
window, and use the same absolute update command under the installing user's
account. Supply noninteractive Git authentication and retain logs. Do not put
tokens in command arguments. The saved profile supplies destination paths; runtime
credentials still belong in each client's launch environment. The updater prevents
overlapping wrapper runs, but does not lock direct `install.sh` calls or clients.

## Stop and recovery conditions

- Dirty/untracked files, local commits, divergent branches, detached HEAD, missing
  upstream, or Git authentication failures: report and preserve the checkout.
  Do not auto-stash, reset, rebase, switch branches, or discard work.
- Installer conflicts or invalid configuration: preserve existing files and report
  the error. Fix the specific issue before rerunning. Git may already have advanced;
  rerunning still reapplies installation. Updates are not a cross-file transaction.
- `Keep existing` or `Keep modified` messages: report that those MCP entries remain
  locally controlled. Do not delete them to force adoption.
- Existing update lock: wait for the other updater. Remove the lock directory only
  after confirming no updater remains (for example, after a crashed process).
- Missing credentials, runtimes, or connectivity: finish independent checks and
  report the remaining setup; never invent credentials or claim live verification.

## Dependency maintenance and verification

Keycloak is pinned to a source revision and Infisical to a package version. The
updater does not upgrade these installations. When repository changes alter those
pins, review the accompanying setup instructions and perform the documented build
or package installation separately. Do not substitute an upstream `latest` version.
Credentials and OAuth sessions remain machine-local.

After restarting, confirm the `paradaux` plugin and its nine namespaced skills
are discovered in each selected client.
For MCP, inspect `codex mcp list` and Claude Code's `/mcp` panel as applicable, then
check authentication/reachability using a harmless read-only operation for each
configured service. Listing a server alone does not establish that it works.
Report unavailable client or service checks as pending. Do not exercise
administrative mutations merely to test connectivity.

## Plugin package maintenance

Use the native Claude/Codex plugin managers through `plugin_install.py`; do not
edit caches or registries directly. Keep `plugins/paradaux/plugin.json`,
`plugins/paradaux/.claude-plugin/plugin.json`, and the marketplace entry in
`.claude-plugin/marketplace.json` on the same version. MCP remains separately
managed. A conflicting `paradaux-local` source must be resolved explicitly;
installation never repoints it automatically. Uninstall retains the marketplace
registration. Do not use a development worktree for user installation or migration.
