"""Check native config installation with disposable homes and no network access."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mcp_installer", ROOT / "mcp/install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class MCPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotagents mcp ")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name).resolve()
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(("DOTAGENTS_", "XDG_"))
                    and k not in ("HOME", "CODEX_HOME", "CLAUDE_CONFIG_DIR", "BASH_ENV")}
        self.env["HOME"] = str(self.home)
        self.claude = self.home / ".claude.json"
        self.codex = self.home / ".codex/config.toml"
        self.state = self.home / ".local/state/dotagents/mcp.json"

    def run_install(self, *args, success=True):
        result = subprocess.run([sys.executable, str(ROOT / "mcp/install.py"), *args],
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def test_both_native_configs_and_repeat_install(self):
        self.run_install()
        claude = json.loads(self.claude.read_text())["mcpServers"]
        codex = tomllib.loads(self.codex.read_text())["mcp_servers"]
        self.assertEqual(set(claude), {"discord", "github", "mariadb-economy", "tasklie", "keycloak", "infisical", "playwright"})
        self.assertEqual(set(claude), set(codex))
        self.assertEqual(claude["github"], {
            "type": "http", "url": "https://api.githubcopilot.com/mcp/",
            "headers": {"Authorization": "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"}})
        self.assertEqual(codex["github"], {
            "url": "https://api.githubcopilot.com/mcp/",
            "bearer_token_env_var": "GITHUB_PERSONAL_ACCESS_TOKEN"})
        self.assertEqual(claude["tasklie"]["headers"]["Authorization"], "Bearer ${TASKLIE_MCP_TOKEN}")
        self.assertEqual(codex["tasklie"]["bearer_token_env_var"], "TASKLIE_MCP_TOKEN")
        self.assertEqual(codex["keycloak"]["args"], [str(ROOT / "mcp/keycloak.py")])
        before = [p.read_text() for p in (self.claude, self.codex, self.state)]
        self.run_install()
        self.assertEqual(before, [p.read_text() for p in (self.claude, self.codex, self.state)])
        for path in (self.claude, self.codex, self.state):
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_existing_servers_and_settings_preserved_with_backups(self):
        previous = {"projects": {"/example": {"trusted": True}}, "mcpServers": {
            "tasklie": {"type": "http", "url": "https://local.example/mcp",
                      "headers": {"Authorization": "test-only-secret"}}}}
        self.claude.write_text(json.dumps(previous))
        self.codex.parent.mkdir()
        original = '# keep comment\nmodel = "test-model"\n[mcp_servers.tasklie]\nurl = "https://local.example/mcp"\n'
        self.codex.write_text(original)
        self.run_install()
        self.assertEqual(json.loads(self.claude.read_text())["projects"], previous["projects"])
        self.assertEqual(json.loads(self.claude.read_text())["mcpServers"]["tasklie"], previous["mcpServers"]["tasklie"])
        self.assertTrue(self.codex.read_text().startswith(original))
        self.assertNotIn("test-only-secret", self.state.read_text())
        backups = list(self.home.rglob("*.dotagents-backup-*"))
        self.assertEqual(len(backups), 2)
        for backup in backups:
            self.assertEqual(backup.stat().st_mode & 0o777, 0o600)
        self.run_install("--uninstall")
        self.assertEqual(json.loads(self.claude.read_text()), previous)
        self.assertEqual(tomllib.loads(self.codex.read_text()), tomllib.loads(original))

    def test_dry_run_and_agent_selection(self):
        self.run_install("--dry-run")
        self.assertEqual(list(self.home.iterdir()), [])
        self.run_install("--agent", "codex")
        self.assertFalse(self.claude.exists())
        self.assertTrue(self.codex.exists())
        before = self.codex.read_text()
        self.run_install("--uninstall", "--dry-run")
        self.assertEqual(self.codex.read_text(), before)

    def test_uninstall_preserves_modified_entries(self):
        self.run_install()
        data = json.loads(self.claude.read_text())
        data["mcpServers"]["tasklie"]["url"] = "https://changed.example/mcp"
        self.claude.write_text(json.dumps(data))
        self.codex.write_text(self.codex.read_text().replace(
            "https://app.taskl.ie/api/public/mcp", "https://changed.example/mcp"))
        self.run_install("--uninstall")
        self.run_install("--uninstall")
        self.assertEqual(set(json.loads(self.claude.read_text())["mcpServers"]), {"tasklie"})
        self.assertEqual(set(tomllib.loads(self.codex.read_text())["mcp_servers"]), {"tasklie"})

    def test_manifest_update_removes_stale_owned_entries(self):
        for agent, merge, parse in (("codex", installer.merge_codex, tomllib.loads),
                                    ("claude", installer.merge_claude, json.loads)):
            text, owned = merge("", installer.render(agent), {})
            desired = installer.render(agent)
            del desired["mariadb-economy"]
            desired["tasklie"]["url"] = "https://new.example/mcp"
            updated, _ = merge(text, desired, owned)
            servers = parse(updated)["mcp_servers" if agent == "codex" else "mcpServers"]
            self.assertEqual(servers, desired)

    def test_tasklie_migration_removes_managed_tesks(self):
        for agent, merge, parse in (("codex", installer.merge_codex, tomllib.loads),
                                    ("claude", installer.merge_claude, json.loads)):
            desired = installer.render(agent)
            old = dict(desired)
            old["tesks"] = dict(old.pop("tasklie"))
            old["tesks"]["url"] = "https://tesks.dev.paradaux.io/mcp"
            if agent == "codex":
                old["tesks"]["bearer_token_env_var"] = "TESKS_MCP_TOKEN"
            else:
                old["tesks"]["headers"] = {"Authorization": "Bearer ${TESKS_MCP_TOKEN}"}
            text, owned = merge("", old, {})
            updated, new_owned = merge(text, desired, owned)
            servers = parse(updated)["mcp_servers" if agent == "codex" else "mcpServers"]
            self.assertEqual(servers, desired)
            self.assertNotIn("tesks", new_owned)
            self.assertEqual(servers["tasklie"]["url"], "https://app.taskl.ie/api/public/mcp")

    def test_invalid_config_preflight_preserves_other_file(self):
        self.codex.parent.mkdir()
        self.codex.write_text("invalid TOML [")
        self.run_install(success=False)
        self.assertFalse(self.claude.exists())
        self.assertFalse(self.state.exists())

    def test_custom_config_paths(self):
        self.env["DOTAGENTS_CLAUDE_CONFIG"] = str(self.home / "claude-custom.json")
        self.env["DOTAGENTS_CODEX_CONFIG"] = str(self.home / "codex-custom.toml")
        self.run_install()
        self.assertFalse(self.claude.exists())
        self.assertFalse(self.codex.exists())
        self.assertTrue((self.home / "claude-custom.json").exists())

    def test_symlink_config_is_not_replaced(self):
        real = self.home / "real.json"
        real.write_text("{}")
        self.claude.symlink_to(real)
        self.run_install(success=False)
        self.assertTrue(self.claude.is_symlink())
        self.assertEqual(real.read_text(), "{}")

    def test_agent_home_overrides(self):
        self.env["CLAUDE_CONFIG_DIR"] = str(self.home / "claude-profile")
        self.env["CODEX_HOME"] = str(self.home / "codex-profile")
        self.run_install()
        self.assertTrue((self.home / "claude-profile/.claude.json").exists())
        self.assertTrue((self.home / "codex-profile/config.toml").exists())
        self.assertFalse(self.claude.exists())
        self.assertFalse(self.codex.exists())

    def test_infisical_launcher_uses_local_credentials_and_filters_environment(self):
        spec = importlib.util.spec_from_file_location("infisical_launcher", ROOT / "mcp/infisical.py")
        launcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(launcher)
        config = self.home / "credentials.json"
        config.write_text(json.dumps({"host": "https://secrets.example", "clientId": "test-id",
                                      "clientSecret": "test-secret"}))
        config.chmod(0o600)
        entry = self.home / "@infisical/mcp/dist/index.js"
        entry.parent.mkdir(parents=True)
        entry.touch()
        with patch.object(launcher, "CONFIG", config), \
                patch.object(launcher.shutil, "which", side_effect=lambda name: "/fake/" + name), \
                patch.object(launcher.subprocess, "run", return_value=subprocess.CompletedProcess(
                    [], 0, stdout=str(self.home) + "\n")), \
                patch.dict(os.environ, {"UNRELATED_SECRET": "must-not-forward"}), \
                patch.object(launcher.os, "execve") as execute:
            launcher.launch()
            command, argv, env = execute.call_args.args
            self.assertEqual(command, "/fake/node")
            self.assertEqual(argv, [command, str(entry)])
            self.assertEqual(env["INFISICAL_HOST_URL"], "https://secrets.example")
            self.assertEqual(env["INFISICAL_AUTH_METHOD"], "universal-auth")
            self.assertEqual(env["INFISICAL_UNIVERSAL_AUTH_CLIENT_ID"], "test-id")
            self.assertEqual(env["INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET"], "test-secret")
            self.assertNotIn("UNRELATED_SECRET", env)
            config.chmod(0o644)
            with self.assertRaises(SystemExit):
                launcher.launch()

    def test_keycloak_launcher_uses_local_credentials_and_filters_environment(self):
        spec = importlib.util.spec_from_file_location("keycloak_launcher", ROOT / "mcp/keycloak.py")
        launcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(launcher)
        config = self.home / "credentials.json"
        config.write_text(json.dumps({"username": "test-user", "password": "test-password"}))
        config.chmod(0o600)
        entry = self.home / "index.js"
        entry.touch()
        with patch.object(launcher, "CONFIG", config), patch.object(launcher, "ENTRY", entry), \
                patch.object(launcher.shutil, "which", return_value="/fake/node"), \
                patch.dict(os.environ, {"UNRELATED_SECRET": "must-not-forward"}), \
                patch.object(launcher.os, "execve") as execute:
            launcher.launch()
            command, argv, env = execute.call_args.args
            self.assertEqual(command, "/fake/node")
            self.assertEqual(argv, [command, str(entry)])
            self.assertEqual(env["KEYCLOAK_ADMIN_PASSWORD"], "test-password")
            self.assertNotIn("UNRELATED_SECRET", env)
            config.chmod(0o644)
            with self.assertRaises(SystemExit):
                launcher.launch()


if __name__ == "__main__":
    unittest.main()
