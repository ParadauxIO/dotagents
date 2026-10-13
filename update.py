#!/usr/bin/env python3
"""Install with remembered settings, or fast-forward and reapply that installation."""

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
PROFILE = ROOT / ".dotagents-install.json"
LOCK = ROOT / ".dotagents-update.lock"
PATH_KEYS = {"DOTAGENTS_CLAUDE_SKILLS_DIR", "DOTAGENTS_CODEX_SKILLS_DIR",
             "DOTAGENTS_CLAUDE_CONFIG", "DOTAGENTS_CODEX_CONFIG", "DOTAGENTS_MCP_STATE"}


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def settings(agent, with_mcp):
    home = Path.home()
    claude = Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude"))
    defaults = {
        "DOTAGENTS_CLAUDE_SKILLS_DIR": claude / "skills",
        "DOTAGENTS_CODEX_SKILLS_DIR": home / ".agents/skills",
        "DOTAGENTS_CLAUDE_CONFIG": claude / ".claude.json" if "CLAUDE_CONFIG_DIR" in os.environ else home / ".claude.json",
        "DOTAGENTS_CODEX_CONFIG": Path(os.environ.get("CODEX_HOME", home / ".codex")) / "config.toml",
        "DOTAGENTS_MCP_STATE": Path(os.environ.get("XDG_STATE_HOME", home / ".local/state")) / "dotagents/mcp.json",
    }
    paths = {key: str(Path(os.environ.get(key, value))) for key, value in defaults.items()}
    if any(not Path(value).is_absolute() for value in paths.values()):
        raise ValueError("Installation paths must be absolute.")
    return {"version": 1, "agent": agent, "with_mcp": with_mcp, "paths": paths}


def read_profile():
    if not PROFILE.exists():
        raise ValueError("No saved installation. Run update.py --install with your original options and path overrides first.")
    profile = json.loads(PROFILE.read_text())
    if (not isinstance(profile, dict)
            or profile.get("version") != 1 or profile.get("agent") not in ("all", "claude", "codex")
            or type(profile.get("with_mcp")) is not bool
            or not isinstance(profile.get("paths"), dict)
            or set(profile["paths"]) != PATH_KEYS
            or any(not isinstance(value, str) or not Path(value).is_absolute()
                   for value in profile["paths"].values())):
        raise ValueError("Invalid installation profile; rerun update.py --install with the intended settings.")
    return profile


def install(profile, dry_run=False):
    command = ["bash", str(ROOT / "install.sh"), "--agent", profile["agent"]]
    if profile["with_mcp"]:
        command.append("--with-mcp")
    if dry_run:
        command.append("--dry-run")
    subprocess.run(command, env={**os.environ, **profile["paths"]}, check=True)


def save(profile):
    fd, name = tempfile.mkstemp(prefix=".dotagents-profile-", dir=ROOT)
    try:
        with os.fdopen(fd, "w") as output:
            json.dump(profile, output, indent=2)
            output.write("\n")
        os.replace(name, PROFILE)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def locked():
    try:
        LOCK.mkdir()
    except FileExistsError:
        raise ValueError(f"Another updater may be running. If none is running, remove {LOCK} and retry.") from None
    try:
        yield
    finally:
        LOCK.rmdir()


def update(profile, dry_run):
    if git("status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Checkout has local changes or untracked files. Preserve and resolve them before updating.")
    if not git("branch", "--show-current"):
        raise ValueError("Detached HEAD; switch to the intended tracking branch first.")
    upstream = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    remote = git("config", "--get", f"branch.{git('branch', '--show-current')}.remote")
    subprocess.run(["git", "-C", str(ROOT), "fetch", remote], check=True)
    ahead, behind = map(int, git("rev-list", "--left-right", "--count", "HEAD...@{upstream}").split())
    if ahead:
        raise ValueError("Checkout has local commits or has diverged. Resolve the branch manually; no reset or rebase was attempted.")
    before = git("rev-parse", "HEAD")
    target = git("rev-parse", "@{upstream}")
    print(f"{upstream}: {behind} new commit(s); {before} -> {target}", flush=True)
    if dry_run:
        print("Preview only: fetched Git metadata; checkout and installed configuration unchanged.")
        return
    subprocess.run(["git", "-C", str(ROOT), "merge", "--ff-only", target], check=True)
    # Execute the newly fetched installer. Always reapply, even after a previous
    # installation failure when Git was already advanced.
    install(profile, dry_run=True)
    install(profile)
    print("Update complete. Restart selected agents and verify skills and MCP connections.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true", help="install and save settings for future updates")
    parser.add_argument("--agent", choices=("all", "claude", "codex"))
    parser.add_argument("--with-mcp", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.install and (args.agent or args.with_mcp):
        parser.error("Use --install to change saved installation settings.")
    with locked():
        if args.install:
            profile = settings(args.agent or "all", args.with_mcp)
            install(profile, args.dry_run)
            if not args.dry_run:
                save(profile)
                print("Installation settings saved locally for update.py.")
        else:
            update(read_profile(), args.dry_run)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"dotagents update stopped: {error}", file=sys.stderr)
        sys.exit(1)
