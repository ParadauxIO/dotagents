# Shared MCP setup

`servers.json` is the canonical MCP manifest for both agents. It captures the
union of the user-level Codex and Claude Code MCP configs. Tasklie replaces the
previous Tesks entry and uses its updated endpoint. All four are installed for
both agents unless `--agent claude` or `--agent codex` is selected.

| Server | Connection | Requirements on a new machine |
| --- | --- | --- |
| `mariadb-economy` | `http://10.111.71.145:8000/mcp` | Network/VPN access to this private address |
| `tasklie` | `https://app.taskl.ie/api/public/mcp` | `TASKLIE_MCP_TOKEN` environment variable |
| `keycloak` | Local Python launcher, Node.js MCP process | Node.js, Git, npm, pinned server build, local Keycloak credentials |
| `infisical` | Local Python launcher, Node.js MCP process | Node.js, npm, `@infisical/mcp`, local Universal Auth credentials |

## Install and update

Close the agents before updating their configuration files, then run:

```bash
bash install.sh --with-mcp --dry-run
bash install.sh --with-mcp
```

Requires Python 3.11+. This merges native user configs at `~/.claude.json` and
`~/.codex/config.toml`. It preserves unrelated settings and existing server entries,
including entries with the same name but a different definition. A `Keep existing`
message means your previous configuration remains in use; remove that server
manually if you want dotagents to manage it instead. Existing credentials are never
read into the repository or ownership state.

Rerun after pulling updates. Entries previously installed by dotagents are updated
or removed to match the manifest only if they have not been edited locally.
Before each changed config is replaced, an owner-only backup is saved next to it
with a `.dotagents-backup-<timestamp>` suffix. Backups may contain your previous
credentials: keep them local. Other settings in Codex TOML retain their formatting;
Claude JSON is reformatted only when a change is needed.

`CODEX_HOME` and `CLAUDE_CONFIG_DIR` are respected. Override full file paths with
`DOTAGENTS_CODEX_CONFIG` or `DOTAGENTS_CLAUDE_CONFIG` if needed. Paths must be absolute;
symlinked config files are refused rather than replaced. Ownership is recorded in
`${XDG_STATE_HOME:-~/.local/state}/dotagents/mcp.json` (override with
`DOTAGENTS_MCP_STATE`). Keep this state file for safe updates and uninstall.

Config writes use atomic replacement per file, not a transaction spanning both
agents. If a write fails, fix the reported configuration problem and rerun.
The installer does not start servers, install runtimes, or make authenticated
requests. Imported configuration is local-machine setup, not cloud provisioning.

## Tasklie authentication

When updating from Tesks, set `TASKLIE_MCP_TOKEN` using your current Tasklie token;
`TESKS_MCP_TOKEN` is no longer used. Rerun `bash install.sh --with-mcp` to replace
unchanged, dotagents-managed `tesks` entries with `tasklie`. Pre-existing or locally
modified `tesks` entries are preserved and must be removed manually if obsolete.

The token previously embedded in the local configs is intentionally not stored
in Git. Retrieve it from your existing local configuration or secret manager and
set `TASKLIE_MCP_TOKEN` in the environment that launches each agent. Supply the token
only, without `Bearer `. For an interactive Bash session without putting the token
in shell history:

```bash
read -r -s -p 'Tasklie MCP token: ' TASKLIE_MCP_TOKEN
printf '\n'
export TASKLIE_MCP_TOKEN
```

`mcp/.env.example` documents the variable; neither agent nor this installer
automatically loads that file. For desktop clients, arrange the variable in the
desktop launch environment. Codex uses `bearer_token_env_var`; Claude uses a
`${TASKLIE_MCP_TOKEN}` reference in its Authorization header.

## Keycloak setup

The portable launcher preserves your existing endpoint, `https://auth.paradaux.io`,
master-realm admin login, and the credential verification against the `minecraft`
realm. It invokes the same upstream revision as your previous local launcher:
[`M0-AR/keycloak-mcp-server`, `692b2a6`](https://github.com/M0-AR/keycloak-mcp-server/tree/692b2a62cad13ea3d8d1a43b3a00d867d1d2288e).

With Node.js, npm, and Git installed:

```bash
python3 mcp/keycloak.py --setup
python3 mcp/keycloak.py --configure
```

Setup fetches that exact commit, installs dependencies from its lockfile with
`npm ci --ignore-scripts`, and builds the server. It reuses an existing build at
`${XDG_DATA_HOME:-~/.local/share}/keycloak-mcp-server/<revision>/dist/index.js`.
The setup step downloads dependencies and explicitly runs the upstream build.
During the clean-build check on 2026-10-13, npm reported two dependency advisories
(one high, one low) for this pinned version. The repository preserves the version
from the original setup; it does not silently upgrade its dependencies. Review
`npm audit` in the installed revision directory before broadening its deployment.

Configure prompts for credentials in your terminal, verifies login and client-list
access, and writes an owner-only file to
`${XDG_CONFIG_HOME:-~/.config}/keycloak-mcp/credentials.json`. Credentials and OAuth
sessions are not transferred through Git. The launcher also reuses credentials
already at that path and finds Python/Node through `PATH` instead of hardcoded
machine paths. The server provides administrative tools; the read-only verification
request does not restrict the server's later permissions.

## Infisical setup

The launcher uses the existing local credential format and passes Universal Auth
credentials to the MCP process. It finds Node.js and npm through `PATH` and the MCP
package in npm's global install directory. Install the same package version as the
original local setup:

```bash
npm install -g @infisical/mcp@0.0.24
```

Reuse your existing `${XDG_CONFIG_HOME:-~/.config}/infisical-mcp/credentials.json`.
On a new machine, create that file locally with permissions `0600` and these keys,
replacing the placeholders with your machine identity's Universal Auth credentials:

```json
{
  "host": "https://secrets.paradaux.io",
  "clientId": "<client ID>",
  "clientSecret": "<client secret>"
}
```

Keep credentials outside the checkout. Grant the machine identity access to the
required projects in Infisical. Restart the agents after rotating credentials.
Existing unmanaged Infisical entries are preserved by the installer; remove them
manually if you want to switch to the shared launcher.

## Verify and uninstall

Restart both agents. Use `codex mcp list` and Claude Code's `/mcp` panel to check
discovery and authentication. Network reachability and credentials must be tested
on the destination machine; CI checks configuration generation and installation,
not your live services.

```bash
bash install.sh --with-mcp --uninstall --dry-run
bash install.sh --with-mcp --uninstall
```

Only unchanged entries installed by dotagents are removed. Pre-existing entries,
locally modified entries, backups, Keycloak builds, and credentials are retained.
Use the same path overrides as installation. Uninstall before moving the checkout,
since the Keycloak command points to its launcher inside this repository.

See the official [Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp)
and [Claude Code MCP configuration](https://code.claude.com/docs/en/mcp) documentation.
