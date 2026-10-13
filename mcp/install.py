#!/usr/bin/env python3
"""Merge the shared MCP manifest into native user configs without copying secrets."""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile

if sys.version_info < (3, 11):
    raise SystemExit("MCP installation requires Python 3.11 or newer.")
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def render(agent):
    manifest = json.loads((ROOT / "mcp/servers.json").read_text())
    servers = {}
    for name, spec in manifest.items():
        spec = deepcopy(spec)
        transport = spec.pop("type")
        token = spec.pop("bearer_token_env_var", None)
        if "args" in spec:
            spec["args"] = [arg.replace("${DOTAGENTS_ROOT}", str(ROOT))
                            for arg in spec["args"]]
        if agent == "claude":
            spec["type"] = transport
            if token:
                spec["headers"] = {"Authorization": "Bearer ${" + token + "}"}
        elif token:
            spec["bearer_token_env_var"] = token
        servers[name] = spec
    return servers


def toml_block(name, spec):
    # This manifest uses only strings and lists of strings, whose JSON encoding
    # is also valid TOML. Parsing the final document below catches table conflicts.
    lines = [f"# BEGIN dotagents MCP {name}",
             f"[mcp_servers.{json.dumps(name)}]"]
    for key, value in spec.items():
        if not (isinstance(value, str) or
                isinstance(value, list) and all(isinstance(v, str) for v in value)):
            raise ValueError(f"Unsupported manifest value: {name}.{key}")
        lines.append(f"{key} = {json.dumps(value, ensure_ascii=False)}")
    lines.append(f"# END dotagents MCP {name}\n")
    return "\n".join(lines)


def merge_codex(text, desired, owned):
    result = text
    retained = {}
    for name, block in owned.items():
        if result.count(block) == 1:
            result = result.replace(block, "", 1)
        else:
            print(f"Keep modified Codex entry: {name}")
            retained[name] = block
    current = tomllib.loads(result).get("mcp_servers", {})
    for name, spec in desired.items():
        if name in current:
            print(f"Keep existing Codex entry: {name}")
            continue
        block = toml_block(name, spec)
        result = result.rstrip() + "\n\n" + block
        retained[name] = block
        print(f"Configure Codex: {name}")
    parsed = tomllib.loads(result)
    for name, block in retained.items():
        if name in desired and result.count(block) == 1:
            if parsed.get("mcp_servers", {}).get(name) != desired[name]:
                raise ValueError(f"Cannot safely merge Codex entry: {name}")
    return result, retained


def merge_claude(text, desired, owned):
    data = json.loads(text) if text else {}
    servers = data.setdefault("mcpServers", {})
    retained = {}
    for name, spec in owned.items():
        if servers.get(name) == spec:
            del servers[name]
        elif name in servers:
            print(f"Keep modified Claude entry: {name}")
            retained[name] = spec
    for name, spec in desired.items():
        if name in servers:
            print(f"Keep existing Claude entry: {name}")
            continue
        servers[name] = spec
        retained[name] = spec
        print(f"Configure Claude: {name}")
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n", retained


def read(path):
    if path.is_symlink():
        raise ValueError(f"Refusing to replace a symlinked config: {path}")
    return path.read_text() if path.exists() else ""


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".dotagents-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as output:
            output.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=("all", "claude", "codex"), default="all")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()
    home = Path.home()
    claude_home = Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude"))
    claude_default = claude_home / ".claude.json" if "CLAUDE_CONFIG_DIR" in os.environ else home / ".claude.json"
    configs = {
        "claude": Path(os.environ.get("DOTAGENTS_CLAUDE_CONFIG", claude_default)),
        "codex": Path(os.environ.get("DOTAGENTS_CODEX_CONFIG",
                      Path(os.environ.get("CODEX_HOME", home / ".codex")) / "config.toml")),
    }
    state_path = Path(os.environ.get("DOTAGENTS_MCP_STATE",
                      Path(os.environ.get("XDG_STATE_HOME", home / ".local/state")) /
                      "dotagents/mcp.json"))
    paths = list(configs.values()) + [state_path]
    if any(not path.is_absolute() for path in paths):
        raise ValueError("Config and state paths must be absolute.")
    if len({path.resolve() for path in paths}) != len(paths):
        raise ValueError("Config and state paths must be different.")
    state_text = read(state_path)
    state = json.loads(state_text) if state_text else {}
    changes = []
    for agent, path in configs.items():
        if args.agent not in ("all", agent):
            continue
        original = read(path)
        owned = state.get(str(path), {})
        desired = {} if args.uninstall else render(agent)
        if not desired and not owned:
            continue
        merge = merge_claude if agent == "claude" else merge_codex
        updated, state[str(path)] = merge(original, desired, owned)
        # Avoid reformatting a user's file when no semantic change is needed.
        parse = json.loads if agent == "claude" else tomllib.loads
        original_data = parse(original or "{}") if agent == "claude" else parse(original)
        if original_data == parse(updated):
            updated = original
        changes.append((path, original, updated))
    if args.dry_run:
        print("MCP dry run: no files written.")
        return
    # Detect concurrent agent writes before touching any configuration.
    for path, original, _ in changes + [(state_path, state_text, "")]:
        if read(path) != original:
            raise ValueError(f"Config changed during installation; retry with agents closed: {path}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    for path, original, updated in changes:
        if original == updated:
            continue
        if path.exists():
            backup = path.with_name(path.name + ".dotagents-backup-" + stamp)
            atomic_write(backup, original)
            print(f"Backup: {backup}")
        atomic_write(path, updated)
        # Persist ownership after each config, so a later write failure does not
        # lose track of a successfully installed server.
        saved = json.loads(read(state_path) or "{}")
        saved[str(path)] = state[str(path)]
        atomic_write(state_path, json.dumps(saved, indent=2) + "\n")
    print("MCP configuration complete. Existing unmanaged entries were preserved.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, TypeError, KeyError) as error:
        # Parser exceptions can include user config values; don't print them.
        print(f"MCP installation stopped ({type(error).__name__}). Check config syntax, "
              "absolute paths, permissions, and close running agents before retrying.", file=sys.stderr)
        sys.exit(1)
