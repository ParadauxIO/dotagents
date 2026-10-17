# dotagents

A shared, globally installed toolkit for Claude Code and Codex. This Git repository
is the source of truth: author a skill once in `skills/`, and the installer links it
into each agent's native personal skills directory.

The repository ships four shared engineering skills and no hooks. It includes shared
MCP setup for Discord, GitHub, MariaDB Economy, Tasklie, Keycloak, Infisical, and headless
Playwright. This is a Git-based
toolkit, not a marketplace plugin; neither agent's plugin manager is
required.

For agents launched by Paseo, see [Paseo tool setup](mcp/README.md#paseo-setup).

## Install

Requires Git, Bash, and Python 3.11+ on macOS, Linux, or WSL. Installation is per
user and applies across that user's local projects; it requires no `sudo`. Since this repository is
private, authenticate with GitHub first (for example, `gh auth login`).

```bash
gh repo clone paradauxio/dotagents "$HOME/.local/share/dotagents"
python3 "$HOME/.local/share/dotagents/update.py" --install --with-mcp
```

Alternatively, clone with an SSH key that has access to the repository:

```bash
git clone git@github.com:paradauxio/dotagents.git "$HOME/.local/share/dotagents"
python3 "$HOME/.local/share/dotagents/update.py" --install --with-mcp
```

Complete the [MCP credential and Keycloak setup](mcp/README.md) after installation.
Omit `--with-mcp` for skills only. The update wrapper requires Python; direct
`bash install.sh` remains available for Bash-only skill installation, but does not
save update settings.

Keep the checkout at that location: installed skills are symlinks to it. Once
skills have been added, start a new agent session to confirm discovery.

| Agent | Default installation directory |
| --- | --- |
| Claude Code | `~/.claude/skills/` (or `$CLAUDE_CONFIG_DIR/skills`) |
| Codex | `~/.agents/skills/` |

Both agents support symlinked skill directories. See the official
[Codex skill documentation](https://learn.chatgpt.com/docs/build-skills) and
[Claude Code skill documentation](https://code.claude.com/docs/en/skills).
These are local user installations; they do not provision remote/cloud sessions.

```bash
# Preview changes, or install for just one agent.
python3 update.py --install --dry-run
python3 update.py --install --agent claude
python3 update.py --install --agent codex
```

For nonstandard installations, set `DOTAGENTS_CLAUDE_SKILLS_DIR` and/or
`DOTAGENTS_CODEX_SKILLS_DIR` to absolute destination paths. These overrides select
where links are written; they do not configure an agent to discover a new path.

## Update

Close the selected agents before applying MCP updates; restart them afterward.
The initial `update.py --install` saves your selected agent, MCP choice, and resolved
skill/configuration/ownership paths in the checkout's ignored, owner-only
`.dotagents-install.json`. Updates reuse those settings even in a different shell.
Keep the profile and MCP ownership state local; neither contains credentials.
One checkout stores one installation recipe. Use separate checkouts for separate
profiles. To change the recipe, rerun `--install` with all intended options and
path overrides; it does not uninstall the previous destinations.

```bash
python3 "$HOME/.local/share/dotagents/update.py" --dry-run
python3 "$HOME/.local/share/dotagents/update.py"
```

The preview fetches Git metadata and reports incoming commits without changing the
checkout or agent configuration. The update requires a clean checkout and a tracking
branch with no local commits, fast-forwards to the fetched revision, previews the
installer, and reapplies it. It does not stash, reset, rebase, or overwrite conflicts.
If installation fails after Git advances, fix the reported problem and rerun the
same update command. The command reapplies installation even with no new commits.

For an existing installation made with `install.sh`, first pull this version with
`git pull --ff-only`, then run `python3 update.py --install` with your original
`--agent`, `--with-mcp`, and path overrides to save its settings. Direct calls to
`install.sh` do not change the saved recipe. After uninstalling, remove
`.dotagents-install.json` to prevent accidentally reinstalling through the updater.

Nothing schedules updates by default. See [agent maintenance instructions](MAINTENANCE.md)
for automatic execution, stop conditions, dependency upgrades, and verification.

Existing skill edits are visible through their links. Rerunning the installer
adds new skills and removes stale links for deleted or renamed skills. It is safe
to rerun: an existing correct link is retained, and conflicting files, directories,
or unrelated links cause an error before installation changes begin. Resolve
conflicts manually; there is deliberately no overwrite flag.

## Uninstall

```bash
bash "$HOME/.local/share/dotagents/install.sh" --with-mcp --uninstall
```

For MCP, this removes only unchanged entries installed by dotagents; see
[MCP setup](mcp/README.md) for ownership and backup behavior. For skills, it removes
only links pointing to this checkout's skill directories, including
links whose source was deleted. Your checkout, other skills, agent settings, and
destination directories are retained. `--agent` and `--dry-run` also work with
`--uninstall`. Use the same destination overrides as installation, if any.
Uninstall before moving or deleting the checkout; reinstall from its new location.

## Included skills

| Skill | Use it for |
| --- | --- |
| [dotagents-verify-webapp](skills/dotagents-verify-webapp/SKILL.md) | Exercise a changed user journey with Playwright and report observable assertions and evidence. |
| [dotagents-resolve-pr](skills/dotagents-resolve-pr/SKILL.md) | Fix actionable PR feedback and CI failures, tracking validation against the current commit. |
| [dotagents-debug-auth](skills/dotagents-debug-auth/SKILL.md) | Trace Keycloak login, session, and permission failures, including Infisical configuration mismatches. |
| [dotagents-create-pr](skills/dotagents-create-pr/SKILL.md) | Create a PR with Why, How, Diagram, and Screenshots sections, attaching rendered diagrams and real screenshots with `gh`. |

Examples: "Verify the updated signup flow", "Resolve the failing checks on PR
123", "Diagnose why staging login succeeds but the API returns 403", or "Create a
PR for this branch with a flow diagram and before/after screenshots".
The skills use tools available in the current agent session and consult each
project's own commands and configuration. They contain no credentials or fixed
application targets. They do not install tool runtimes or grant access to services.

PR image attachments require a `gh` CLI with native `--attach` support (introduced
in 2.99.0), a supported GitHub host, and upload access to the repository. The PR
skill checks capability before publishing. Diagrams use an available local
renderer such as Mermaid CLI; screenshots use the project's browser setup or
Playwright tools. Missing dependencies are reported with prepared artifacts kept
for retry.

These are initial workflows, not measured productivity guarantees. Trial them on
representative tasks in each agent, comparing human correction time, task success,
rework, runtime, and whether the skill activates appropriately. Installer tests
check packaging and links; they do not establish skill effectiveness.

## Add skills

Create `skills/<skill-name>/SKILL.md` with YAML frontmatter containing `name` and
`description`, followed by instructions. Use the same value for the folder and
frontmatter name. Names should use lowercase letters, numbers, and single hyphens,
at most 64 characters; `synced` and `anthropic-skills` are reserved. Keep optional
scripts, references, and assets inside that skill directory. Use instructions
compatible with both agents, and prefix names with `dotagents-` to avoid collisions.

Run `bash install.sh` after adding or renaming a skill. No generated copies or
agent-specific versions need to be maintained. The installer checks directory
names and the presence of `SKILL.md`; it does not validate the content of skills.

## Development and CI

```bash
bash -n install.sh
shellcheck install.sh
python3 -m unittest discover -s tests -v
```

Python 3.11+ is required for MCP installation and testing; ShellCheck is a
development dependency only. GitHub Actions runs
installer integration tests on Linux and macOS, plus ShellCheck on Linux, on pushes
and pull requests. Tests use disposable checkouts and temporary homes; no installed
agent or API key is needed. They cover empty installs, both agents, repeat installs,
conflicts, updates, dry runs, custom paths, and selective uninstall. Agent discovery
itself should be checked in each client when adding real skills.
Updater tests use local Git remotes to cover saved settings, fast-forward updates,
checkout protection, and recovery after an installation failure.
