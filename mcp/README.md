# Shared MCP setup

`servers.json` is the canonical MCP manifest for both agents. It captures the
union of the user-level Codex and Claude Code MCP configs. Tasklie replaces the
previous Tesks entry and uses its updated endpoint. All seven are installed for
both agents unless `--agent claude` or `--agent codex` is selected.

| Server | Connection | Requirements on a new machine |
| --- | --- | --- |
| `discord` | `http://localhost:8085/mcp` | Separately hosted SaseQ/discord-mcp server with a Discord bot token; setup pending |
| `github` | `https://api.githubcopilot.com/mcp/` | `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable |
| `mariadb-economy` | `http://10.111.71.145:8000/mcp` | Network/VPN access to this private address |
| `tasklie` | `https://app.taskl.ie/api/public/mcp` | `TASKLIE_MCP_TOKEN` environment variable |
| `keycloak` | Local Python launcher, Node.js MCP process | Node.js, Git, npm, pinned server build, local Keycloak credentials |
| `infisical` | Local Python launcher, Node.js MCP process | Node.js, npm, `@infisical/mcp`, local Universal Auth credentials |
| `playwright` | Local Node.js MCP process via `npx` | Node.js 18+, npm, Chrome and its system dependencies; runs headless |

Paseo tools are configured separately in the local Paseo daemon, as described
below; they are not an entry in `servers.json`.

## Paseo setup

With Paseo installed, enable **Settings → your host → Agents → Enable Paseo
tools**. Alternatively, merge these fields into `~/.paseo/config.json`, preserving
the rest of your configuration:

```json
{
  "daemon": {
    "mcp": {
      "enabled": true,
      "injectIntoAgents": true
    }
  }
}
```

Run `paseo reload`, then start a new agent or reload an existing agent. Paseo
supplies its tools to agents it launches through the provider's native tool
interface or MCP. This does not configure standalone clients launched outside
Paseo. The dotagents installer does not edit Paseo's daemon configuration.

Verify discovery in the refreshed agent with a read-only Paseo tool such as
`list_workspaces`. Reloading the daemon alone does not refresh an existing
agent's tool catalog. See the official [Paseo MCP reference](https://paseo.sh/docs/mcp)
for provider-specific tool policies and the full catalog.

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

For repeatable updates, use the [saved installation updater](../README.md#update)
and follow the [agent maintenance procedure](../MAINTENANCE.md).
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

## Discord setup (pending)

The `discord` entry targets the default local HTTP endpoint of
[SaseQ/discord-mcp](https://github.com/SaseQ/discord-mcp). It will be unavailable
until you deploy the server. The installer only adds the client connection.
If you deploy elsewhere, change the URL in `servers.json` before installation.

For a local Docker deployment, create a Discord bot and invite it to your guild
with the permissions and intents required by the upstream setup instructions.
Supply its token to the server, not the agent configuration:

```bash
read -r -s -p 'Discord bot token: ' DISCORD_TOKEN
printf '\n'
export DISCORD_TOKEN
docker run -d -i --name discord-mcp --restart unless-stopped \
  -p 127.0.0.1:8085:8085 \
  -e SPRING_PROFILES_ACTIVE=http -e DISCORD_TOKEN \
  saseq/discord-mcp:latest
unset DISCORD_TOKEN
```

Optionally pass `DISCORD_GUILD_ID` to the container for a default guild. The image
uses upstream `latest`. Keep tokens outside Git. This example binds the service
to loopback; remote hosting needs its own access controls.

After deployment, check `http://localhost:8085/actuator/health`, restart the agents,
and verify with a read-only server-information request. Live verification remains
pending until deployment.

## GitHub authentication

GitHub uses the [official remote MCP server](https://github.com/github/github-mcp-server)
with personal access token authentication; no local server or Docker is required.
Create a GitHub personal access token with access to the repositories and permissions
needed for your intended tools, then set it in the environment that launches each
agent. For an interactive Bash session without putting the token in shell history:

```bash
read -r -s -p 'GitHub personal access token: ' GITHUB_PERSONAL_ACCESS_TOKEN
printf '\n'
export GITHUB_PERSONAL_ACCESS_TOKEN
bash install.sh --with-mcp
```

Restart the agents from that environment. Codex uses `bearer_token_env_var`;
Claude uses `${GITHUB_PERSONAL_ACCESS_TOKEN}` in its Authorization header. The
installer stores only the variable reference, never the token. `mcp/.env.example`
documents the variable but is not loaded automatically. For desktop clients, set
the variable in the desktop launch environment. A GitHub CLI login alone does not
set this variable.

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

## Playwright setup

The shared entry runs `npx -y @playwright/mcp@latest --headless` for both agents.
The explicit `--headless` flag lets it launch a browser on machines without a
display server or desktop session. See the official
[Playwright MCP documentation](https://github.com/microsoft/playwright-mcp).

Install Node.js 18+ and npm, and make `npx` available in each agent's launch
environment. The first launch downloads the MCP package, so it needs npm registry
access. This entry follows upstream `latest`, rather than pinning a package version.
Chrome (the default browser) and its Linux system dependencies must also be
installed; the dotagents installer does not provision them. If Chrome is missing:

```bash
npx -y playwright install chrome
```

Browser installation may require administrator privileges for system packages.
After applying the shared configuration and restarting the agents, verify with a
Playwright navigation to `about:blank` and a browser snapshot. No API token is
required.

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
