"""Exercise updates against local Git remotes without network or real agent configs."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from plugin_fixture import copy_package, fake_clients

SOURCE = Path(__file__).resolve().parents[1]


class UpdateTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="dotagents update ")
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.remote = self.base / "upstream"
        self.repo = self.base / "installed checkout"
        self.home = self.base / "home"
        self.home.mkdir()
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("DOTAGENTS_", "GIT_", "XDG_"))
                    and key not in ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "BASH_ENV")}
        self.env.update(HOME=str(self.home), GIT_CONFIG_NOSYSTEM="1",
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_AUTHOR_NAME="Test",
                        GIT_AUTHOR_EMAIL="test@example.com", GIT_COMMITTER_NAME="Test",
                        GIT_COMMITTER_EMAIL="test@example.com")
        self.env.update(CODEX_HOME=str(self.home / "codex"), CLAUDE_CONFIG_DIR=str(self.home / "claude"))
        fake_clients(self.base, self.env)
        self.git(self.base, "init", "--initial-branch=main", str(self.remote))
        copy_package(self.remote)
        for name in ("update.py", ".gitignore"):
            shutil.copyfile(SOURCE / name, self.remote / name)
        shutil.copytree(SOURCE / "mcp", self.remote / "mcp")

        self.add_skill("dotagents-old")
        self.commit(self.remote)
        self.git(self.base, "clone", str(self.remote), str(self.repo))

    def git(self, cwd, *args):
        return subprocess.check_output(["git", "-C", str(cwd), *args],
                                       env=self.env, text=True, stderr=subprocess.PIPE).strip()

    def commit(self, cwd):
        self.git(cwd, "add", ".")
        self.git(cwd, "commit", "-m", "Test change")

    def add_skill(self, name):
        directory = self.remote / "plugins/paradaux/skills" / name
        directory.mkdir()
        (directory / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Test skill.\n---\nTest.\n")

    def run_update(self, *args, success=True):
        result = subprocess.run([sys.executable, str(self.repo / "update.py"), *args],
                                env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_remembers_scope_paths_and_updates_skills(self):
        custom = self.base / "custom codex"
        self.env["CODEX_HOME"] = str(custom)
        self.run_update("--install", "--agent", "codex")
        self.env["CODEX_HOME"] = str(self.home / "wrong")
        self.assertEqual(self.git(self.repo, "status", "--porcelain"), "")
        self.add_skill("new-skill")
        self.commit(self.remote)
        before = self.git(self.repo, "rev-parse", "HEAD")
        self.run_update("--dry-run")
        self.assertEqual(before, self.git(self.repo, "rev-parse", "HEAD"))
        self.assertFalse((custom / "cache/skills/new-skill").exists())
        self.run_update()
        self.assertTrue((custom / "cache/skills/new-skill/SKILL.md").exists())
        self.assertFalse((self.home / "wrong").exists())
        self.assertFalse((self.home / "claude").exists())
        self.run_update()

    def test_mcp_settings_and_ownership_survive_environment_changes(self):
        config = self.base / "custom config.toml"
        state = self.base / "ownership.json"
        self.env.update(DOTAGENTS_CODEX_CONFIG=str(config), DOTAGENTS_MCP_STATE=str(state))
        self.run_update("--install", "--agent", "codex", "--with-mcp")
        del self.env["DOTAGENTS_CODEX_CONFIG"]
        del self.env["DOTAGENTS_MCP_STATE"]
        manifest = self.remote / "mcp/servers.json"
        data = json.loads(manifest.read_text())
        data["github"]["url"] = "https://example.com/updated"
        manifest.write_text(json.dumps(data))
        self.commit(self.remote)
        self.run_update()
        self.assertIn("https://example.com/updated", config.read_text())
        self.assertTrue(state.exists())
        self.assertFalse((self.home / ".codex").exists())
        self.assertEqual((self.repo / ".dotagents-install.json").stat().st_mode & 0o777, 0o600)

    def test_missing_profile_and_install_preview(self):
        self.assertIn("No saved installation", self.run_update(success=False))
        self.run_update("--install", "--dry-run")
        self.assertFalse((self.repo / ".dotagents-install.json").exists())
        self.assertEqual(list(self.home.iterdir()), [])

    def test_invalid_profile_is_reported_without_traceback(self):
        (self.repo / ".dotagents-install.json").write_text("[]")
        output = self.run_update(success=False)
        self.assertIn("Invalid or legacy installation profile", output)
        self.assertNotIn("Traceback", output)

    def test_dirty_detached_ahead_diverged_and_missing_upstream(self):
        self.run_update("--install")
        original = self.git(self.repo, "rev-parse", "HEAD")
        loose = self.repo / "local.txt"
        loose.write_text("preserve")
        self.assertIn("local changes", self.run_update(success=False))
        self.assertEqual(loose.read_text(), "preserve")
        loose.unlink()
        self.git(self.repo, "checkout", "--detach")
        self.assertIn("Detached HEAD", self.run_update(success=False))
        self.git(self.repo, "checkout", "main")
        loose.write_text("local commit")
        self.commit(self.repo)
        self.assertIn("local commits", self.run_update(success=False))
        self.add_skill("dotagents-new")
        self.commit(self.remote)
        self.assertIn("diverged", self.run_update(success=False))
        self.assertNotEqual(self.git(self.repo, "rev-parse", "HEAD"), original)
        self.git(self.repo, "branch", "--unset-upstream")
        self.run_update(success=False)
        self.assertEqual(loose.read_text(), "local commit")

    def test_retries_installation_after_git_advanced(self):
        self.run_update("--install", "--agent", "codex")
        self.add_skill("new-skill")
        self.commit(self.remote)
        self.env["FAIL_PLUGIN"] = "codex"
        self.run_update(success=False)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"),
                         self.git(self.remote, "rev-parse", "HEAD"))
        del self.env["FAIL_PLUGIN"]
        self.run_update()
        self.assertTrue((self.home / "codex/cache/skills/new-skill/SKILL.md").exists())

    def test_legacy_profile_requires_explicit_migration(self):
        self.run_update("--install", "--agent", "codex")
        path = self.repo / ".dotagents-install.json"
        data = json.loads(path.read_text())
        data["version"] = 1
        path.write_text(json.dumps(data))
        self.assertIn("legacy installation profile", self.run_update(success=False))
        self.run_update("--install", "--agent", "codex")
        self.assertEqual(json.loads(path.read_text())["version"], 2)

    def test_lock_and_update_options(self):
        lock = self.repo / ".dotagents-update.lock"
        lock.mkdir()
        self.assertIn("Another updater", self.run_update("--install", success=False))
        self.assertTrue(lock.is_dir())
        lock.rmdir()
        self.assertIn("Use --install", self.run_update("--agent", "codex", success=False))


if __name__ == "__main__":
    unittest.main()
