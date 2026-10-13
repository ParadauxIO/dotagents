# dotagents

A shared, globally installed toolkit for Claude Code and Codex. This Git repository
is the source of truth: author a skill once in `skills/`, and the installer links it
into each agent's native personal skills directory.

The repository contains **no skills, hooks, or agent prompts**. It includes shared
MCP setup for GitHub, MariaDB Economy, Tasklie, Keycloak, and Infisical. This is a Git-based
toolkit scaffold, not a marketplace plugin; neither agent's plugin manager is
required.

## Install

Requires Git, Bash, and Python 3.11+ on macOS, Linux, or WSL. Installation is per
user and applies across that user's local projects; it requires no `sudo`. Since this repository is
private, authenticate with GitHub first (for example, `gh auth login`).

```bash
gh repo clone paradauxio/dotagents "$HOME/.local/share/dotagents"
bash "$HOME/.local/share/dotagents/install.sh" --with-mcp
```

Alternatively, clone with an SSH key that has access to the repository:

```bash
git clone git@github.com:paradauxio/dotagents.git "$HOME/.local/share/dotagents"
bash "$HOME/.local/share/dotagents/install.sh" --with-mcp
```

Complete the [MCP credential and Keycloak setup](mcp/README.md) after installation.
Omit `--with-mcp` for skills only (which needs only Bash).

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
bash install.sh --dry-run
bash install.sh --agent claude
bash install.sh --agent codex
```

For nonstandard installations, set `DOTAGENTS_CLAUDE_SKILLS_DIR` and/or
`DOTAGENTS_CODEX_SKILLS_DIR` to absolute destination paths. These overrides select
where links are written; they do not configure an agent to discover a new path.

## Update

```bash
git -C "$HOME/.local/share/dotagents" pull --ff-only
bash "$HOME/.local/share/dotagents/install.sh" --with-mcp
```

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

## Add skills later

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
