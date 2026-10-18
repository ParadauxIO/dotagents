# dotagents

Personal engineering workflows packaged as the **paradaux** plugin for Claude Code
and Codex. Author each skill once under `plugins/paradaux/skills/`; native plugin
loading supplies the `paradaux:` namespace. Skill folder and frontmatter names stay
short, such as `create-pr`, rather than containing a literal colon.

The plugin contains seven skills and no hooks or bundled MCP servers. Optional
shared MCP setup for Discord, GitHub, MariaDB Economy, Tasklie, Keycloak, Infisical,
and headless Playwright remains independently managed by `mcp/install.py`.
For agents launched by Paseo, see [Paseo tool setup](mcp/README.md#paseo-setup).

## Install

Requires Git, Bash, Python 3.11+, and each selected agent's CLI with native local
plugin marketplace support. The default installs for both agents. This private
repository requires GitHub authentication (for example, `gh auth login`).

```bash
gh repo clone ParadauxIO/dotagents "$HOME/.local/share/dotagents"
python3 "$HOME/.local/share/dotagents/update.py" --install --with-mcp
```

Keep this permanent checkout: the local marketplace and MCP launchers reference it.
The installer registers it as `paradaux-local` and installs
`paradaux@paradaux-local` through the native managers. It does not publish a public
marketplace. Close selected clients before installation/updates, then restart them.
Complete [MCP credential and runtime setup](mcp/README.md) if using `--with-mcp`.
Omit that flag for the skills-only plugin.

```bash
python3 update.py --install --dry-run
python3 update.py --install --agent claude
python3 update.py --install --agent codex
```

Dry runs describe actions without invoking native plugin managers; they do not
verify CLI capabilities, registration conflicts, or credentials. Actual installs
preflight selected clients and reject `paradaux-local` registrations pointing at a
different checkout. Resolve those registrations explicitly rather than overwriting
another installation. A partial failure can be retried with the same command.

`CLAUDE_CONFIG_DIR` and `CODEX_HOME` select the native plugin homes. The updater
records them with the selected agent, MCP choice, and configuration paths in the
ignored `.dotagents-install.json` (version 2). MCP path overrides still apply only
to MCP installation, not native plugin settings. Native commands manage their own
settings and caches; dotagents does not rewrite plugin registries by hand.

## Use the skills

| Skill | Use it for |
| --- | --- |
| [paradaux:scratchpad](plugins/paradaux/skills/scratchpad/SKILL.md) | Keep local scratch scripts, notes, and temporary artifacts in `.context/` instead of RAM-backed `/tmp`. |
| [paradaux:start-work](plugins/paradaux/skills/start-work/SKILL.md) | Begin from a description or named Tasklie/GitHub ticket, gather context, define success, and proceed within the requested scope. |
| [paradaux:verify-webapp](plugins/paradaux/skills/verify-webapp/SKILL.md) | Exercise a changed user journey with Playwright and report observable assertions and evidence. |
| [paradaux:resolve-pr](plugins/paradaux/skills/resolve-pr/SKILL.md) | Fix actionable PR feedback and CI failures, tracking validation against the current commit. |
| [paradaux:systematic-debugging](plugins/paradaux/skills/systematic-debugging/SKILL.md) | Diagnose bugs, flaky tests, performance regressions, and cross-service failures with controlled experiments and verified repairs. |
| [paradaux:debug-auth](plugins/paradaux/skills/debug-auth/SKILL.md) | Trace Keycloak login, session, and permission failures, including Infisical configuration mismatches. |
| [paradaux:create-pr](plugins/paradaux/skills/create-pr/SKILL.md) | Create a PR with Why, How, Diagram, and Screenshots sections, attaching rendered diagrams and real screenshots with `gh`. |

In Claude Code, invoke `/paradaux:start-work PAR-123` or
`/paradaux:create-pr`. In Codex, select the namespaced skill from the skill picker
or ask to use `paradaux:start-work` with your request. Confirm discovery after
restarting each client; cached sessions do not gain newly installed skills.

Examples: "Start work on PAR-123", "Fix filters resetting after refresh", "Verify
the signup flow", or "Create a PR with a flow diagram and before/after screenshots".
The skills consult each project's own commands and configuration and contain no
credentials or fixed application targets.

PR images require native `gh --attach` support (introduced in 2.99.0), a supported
GitHub host, and repository upload access. Diagrams use a local renderer such as
Mermaid CLI; screenshots use available Playwright tools or project browser tests.
Missing dependencies are reported with prepared artifacts retained for retry.

## Update and migration

```bash
python3 "$HOME/.local/share/dotagents/update.py" --dry-run
python3 "$HOME/.local/share/dotagents/update.py"
```

Updates reuse the saved version-2 settings, require a clean tracking checkout,
fast-forward Git, preview installation, and refresh the native plugin. The updater
does not stash, reset, or overwrite divergent work. If installation fails after
Git advances, fix the problem and rerun; installation runs even with no new commits.
No recurring updates are scheduled. See [MAINTENANCE.md](MAINTENANCE.md).

**Migrating from standalone skills:** with clients closed, first update the
permanent checkout using `git pull --ff-only`, then rerun
`python3 update.py --install` with your original `--agent`, `--with-mcp`, and path
overrides, plus the intended `CODEX_HOME`/`CLAUDE_CONFIG_DIR` if nonstandard. Version-1
profiles require this explicit registration because they did not record plugin
homes. After each agent's plugin installation succeeds, the installer removes only
exact symlinks pointing at this checkout's old `skills/<link-name>` paths, including
stale `dotagents-*` and unprefixed links. Ordinary files and links from another
checkout are preserved. `DOTAGENTS_CLAUDE_SKILLS_DIR` and
`DOTAGENTS_CODEX_SKILLS_DIR` now identify legacy cleanup directories only.

The plugin source is `plugins/paradaux/`. Claude's current local-folder installation
reads it directly; Codex refreshes its cached package during installation. Always
rerun the updater and restart clients after changes. For versioned releases, bump
both plugin manifests and the marketplace entry together.

## Uninstall

```bash
bash install.sh --uninstall --with-mcp
```

Use the same agent, plugin-home, legacy-path, and MCP overrides as installation.
This removes the user-scoped plugin through native managers and exact old skill
links. With `--with-mcp`, it also removes only unchanged MCP entries owned by
this checkout. The checkout, unrelated plugins/configuration, and local marketplace
registration remain. Remove `.dotagents-install.json` afterward to prevent a later
update from reinstalling. Uninstall before moving/deleting the permanent checkout.
Native plugin settings are not transactional across clients; report partial failures
and retry rather than modifying caches manually.

## Development

Create `plugins/paradaux/skills/<skill-name>/SKILL.md` with matching `name` and a
precise `description` in YAML frontmatter. Use lowercase letters, digits, and
single hyphens, at most 64 characters. Keep scripts, references, and assets within
the skill folder. Keep both agents' instructions compatible; use the `paradaux:`
namespace when referring to sibling skills. The installer validates basic package
identity and skill names; agent discovery and behavioral quality need client checks.

```bash
bash -n install.sh
shellcheck install.sh
python3 -m unittest discover -s tests -v
```

Tests use temporary homes, local Git remotes, and fake native CLIs. MCP tests call
the independent MCP installer. No real configuration, secrets, or network is needed.
CI runs the suite on Linux/macOS and ShellCheck on Linux. Native client smoke tests
should also use isolated temporary homes without credentials.

These workflows are not measured productivity guarantees. Trial them against
representative tasks in both agents, tracking task success, human correction time,
rework, runtime, and appropriate activation.

Packaging follows [Claude plugins](https://code.claude.com/docs/en/plugins) and
[OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins).

The systematic debugging workflow takes inspiration from [Superpowers](https://github.com/obra/superpowers/blob/main/skills/systematic-debugging/SKILL.md), with independently written guidance for telemetry, intermittent failures, incident mitigation, and agent/tool workflows.
