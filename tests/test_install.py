"""Exercise the real Bash installer without touching the user's agent directories."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotagents tests ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "checkout with spaces"
        self.repo.mkdir()
        self.skills = self.repo / "skills"
        self.skills.mkdir()
        shutil.copyfile(Path(__file__).resolve().parents[1] / "install.sh",
                        self.repo / "install.sh")
        self.home = self.base / "home"
        self.home.mkdir()
        self.claude = self.home / ".claude/skills"
        self.codex = self.home / ".agents/skills"
        self.env = {key: value for key, value in os.environ.items()
                    if key not in ("CLAUDE_CONFIG_DIR", "BASH_ENV")
                    and not key.startswith("DOTAGENTS_")}
        self.env["HOME"] = str(self.home)

    def run_installer(self, *args, success=True):
        result = subprocess.run(["bash", str(self.repo / "install.sh"), *args],
                                cwd=self.base, env=self.env, text=True,
                                capture_output=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def add_skill(self, name="dotagents-example"):
        skill = self.skills / name
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Temporary test fixture.\n---\nTest.\n")
        return skill

    def test_empty_install_and_uninstall(self):
        self.assertIn("0 skill(s)", self.run_installer().stdout)
        self.run_installer("--uninstall")
        self.assertEqual(list(self.home.iterdir()), [])

    def test_both_agents_repeat_install_and_live_edits(self):
        skill = self.add_skill()
        self.run_installer()
        for target in (self.claude, self.codex):
            link = target / skill.name
            self.assertTrue(link.is_symlink())
            self.assertEqual(os.readlink(link), str(skill))
        self.run_installer()
        (skill / "SKILL.md").write_text("Updated content")
        self.assertEqual((self.codex / skill.name / "SKILL.md").read_text(),
                         "Updated content")

    def test_selective_install_and_uninstall(self):
        skill = self.add_skill()
        self.run_installer("--agent", "codex")
        self.assertFalse(self.claude.exists())
        self.run_installer("--agent", "claude")
        self.run_installer("--uninstall", "--agent", "claude")
        self.assertFalse((self.claude / skill.name).is_symlink())
        self.assertTrue((self.codex / skill.name).is_symlink())

    def test_conflicts_preflight_both_agents(self):
        skill = self.add_skill()
        self.codex.mkdir(parents=True)
        conflict = self.codex / skill.name
        for kind in ("file", "directory", "broken-link", "directory-link"):
            with self.subTest(kind=kind):
                if kind == "file":
                    conflict.write_text("keep me")
                elif kind == "directory":
                    conflict.mkdir()
                else:
                    conflict.symlink_to(self.base / "missing" if kind == "broken-link"
                                        else self.home, target_is_directory=True)
                self.assertIn("Conflict", self.run_installer(success=False).stderr)
                self.assertFalse(self.claude.exists())
                self.assertTrue(os.path.lexists(conflict))
                if kind == "directory":
                    conflict.rmdir()
                else:
                    conflict.unlink()

    def test_dry_run_install_uninstall_and_prune(self):
        skill = self.add_skill()
        self.run_installer("--dry-run")
        self.assertEqual(list(self.home.iterdir()), [])
        self.run_installer()
        self.run_installer("--uninstall", "--dry-run")
        self.assertTrue((self.claude / skill.name).is_symlink())
        shutil.rmtree(skill)
        self.run_installer("--dry-run")
        self.assertTrue((self.codex / skill.name).is_symlink())

    def test_update_prunes_deleted_skills_and_adds_new(self):
        old = self.add_skill("dotagents-old")
        self.run_installer()
        shutil.rmtree(old)
        new = self.add_skill("dotagents-new")
        self.run_installer()
        for target in (self.claude, self.codex):
            self.assertFalse(os.path.lexists(target / old.name))
            self.assertEqual((target / new.name).resolve(), new)

    def test_uninstall_preserves_unrelated_and_replaced_entries(self):
        skill = self.add_skill()
        self.run_installer()
        unrelated = self.claude / "unrelated"
        unrelated.symlink_to(self.home, target_is_directory=True)
        replaced = self.claude / skill.name
        replaced.unlink()
        replaced.mkdir()
        shutil.rmtree(skill)
        self.run_installer("--uninstall")
        self.run_installer("--uninstall")
        self.assertTrue(unrelated.is_symlink())
        self.assertTrue(replaced.is_dir())
        self.assertFalse(os.path.lexists(self.codex / skill.name))
        self.assertTrue(self.repo.exists())

    def test_custom_destinations(self):
        skill = self.add_skill()
        custom_claude = self.base / "custom claude/skills"
        custom_codex = self.base / "custom codex/skills"
        self.env["DOTAGENTS_CLAUDE_SKILLS_DIR"] = str(custom_claude)
        self.env["DOTAGENTS_CODEX_SKILLS_DIR"] = str(custom_codex)
        self.run_installer()
        self.assertTrue((custom_claude / skill.name).is_symlink())
        self.assertTrue((custom_codex / skill.name).is_symlink())
        self.assertEqual(list(self.home.iterdir()), [])
        self.run_installer("--uninstall")
        self.assertFalse(os.path.lexists(custom_codex / skill.name))

    def test_claude_config_dir(self):
        skill = self.add_skill()
        config = self.base / "claude profile"
        self.env["CLAUDE_CONFIG_DIR"] = str(config)
        self.run_installer("--agent", "claude")
        self.assertEqual((config / "skills" / skill.name).resolve(), skill)

    def test_invalid_arguments_and_destinations(self):
        for args in (("--agent",), ("--agent", "other"), ("--unknown",)):
            self.run_installer(*args, success=False)
        self.env["DOTAGENTS_CODEX_SKILLS_DIR"] = "relative/path"
        self.run_installer(success=False)
        self.assertEqual(list(self.home.iterdir()), [])
        self.env["DOTAGENTS_CODEX_SKILLS_DIR"] = str(self.base / "file")
        (self.base / "file").write_text("keep")
        self.run_installer(success=False)

    def test_invalid_skill_rejected_before_changes(self):
        self.add_skill("valid")
        for name in ("Uppercase", "synced", "anthropic-skills", "a--b", "a" * 65):
            with self.subTest(name=name):
                skill = self.add_skill(name)
                self.run_installer(success=False)
                self.assertEqual(list(self.home.iterdir()), [])
                shutil.rmtree(skill)
        (self.skills / "missing-manifest").mkdir()
        self.run_installer(success=False)
        self.assertEqual(list(self.home.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
