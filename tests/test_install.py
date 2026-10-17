"""Exercise native plugin installation orchestration with disposable client homes."""
import json
import os
from pathlib import Path
import subprocess
import shutil
import tempfile
import unittest

from plugin_fixture import SOURCE, copy_package, fake_clients


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='dotagents plugins ')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / 'checkout'
        self.repo.mkdir()
        copy_package(self.repo)
        self.home = self.base / 'home'
        self.home.mkdir()
        self.env = {k:v for k,v in os.environ.items() if not k.startswith('DOTAGENTS_')
                    and k not in ('BASH_ENV','CODEX_HOME','CLAUDE_CONFIG_DIR')}
        self.env.update(HOME=str(self.home), CODEX_HOME=str(self.home/'codex'),
                        CLAUDE_CONFIG_DIR=str(self.home/'claude'))
        fake_clients(self.base,self.env)

    def install(self,*args,success=True):
        r=subprocess.run(['bash',str(self.repo/'install.sh'),*args],env=self.env,
                         text=True,capture_output=True)
        self.assertEqual(r.returncode == 0,success,r.stdout+r.stderr)
        return r.stdout+r.stderr

    def legacy(self,agent,name='dotagents-create-pr'):
        directory=self.home/('claude/skills' if agent=='claude' else '.agents/skills')
        directory.mkdir(parents=True,exist_ok=True)
        link=directory/name
        link.symlink_to(self.repo/'skills'/name)
        return link

    def test_install_refresh_and_uninstall_both_agents(self):
        links=[self.legacy(a) for a in ('claude','codex')]
        self.install()
        self.assertTrue(all(not p.is_symlink() for p in links))
        for agent in ('claude','codex'):
            self.assertTrue((self.home/agent/'cache/skills/create-pr/SKILL.md').exists())
        source=self.repo/'plugins/paradaux/skills/create-pr/SKILL.md'
        source.write_text(source.read_text()+'\nRefreshed\n')
        self.install()
        for agent in ('claude','codex'):
            self.assertIn('Refreshed',(self.home/agent/'cache/skills/create-pr/SKILL.md').read_text())
        self.install('--uninstall')
        self.install('--uninstall')
        for agent in ('claude','codex'):
            self.assertFalse((self.home/agent/'cache').exists())

    def test_dry_run_does_not_create_client_homes_or_remove_links(self):
        self.install('--dry-run')
        self.assertEqual(list(self.home.iterdir()),[])
        link=self.legacy('claude')
        self.install('--uninstall','--dry-run')
        self.assertTrue(link.is_symlink())

    def test_selective_custom_legacy_migration_preserves_unrelated(self):
        old=self.base/'custom skills';old.mkdir()
        self.env['DOTAGENTS_CODEX_SKILLS_DIR']=str(old)
        owned=old/'start-work';owned.symlink_to(self.repo/'skills/start-work')
        other=old/'other';other.symlink_to(self.base/'missing')
        regular=old/'create-pr';regular.write_text('user content')
        self.install('--agent','codex')
        self.assertFalse(owned.is_symlink())
        self.assertTrue(other.is_symlink())
        self.assertEqual(regular.read_text(),'user content')
        self.assertFalse((self.home/'claude').exists())

    def test_marketplace_conflict_preflight_preserves_links(self):
        link=self.legacy('claude')
        config=self.home/'codex';config.mkdir()
        (config/'fake.json').write_text(json.dumps({'source':str(self.base/'other')}))
        self.assertIn('Conflict',self.install(success=False))
        self.assertTrue(link.is_symlink())
        self.assertFalse((self.home/'claude/cache').exists())

    def test_failed_install_keeps_legacy_links_and_retry_works(self):
        link=self.legacy('codex')
        self.env['FAIL_PLUGIN']='codex'
        self.install('--agent','codex',success=False)
        self.assertTrue(link.is_symlink())
        del self.env['FAIL_PLUGIN']
        self.install('--agent','codex')
        self.assertFalse(link.is_symlink())

    def test_invalid_package_fails_before_changes(self):
        (self.repo/'plugins/paradaux/skills/create-pr/SKILL.md').write_text('bad')
        self.assertIn('name must match',self.install(success=False))
        self.assertEqual(list(self.home.iterdir()),[])

    def test_invalid_options_and_paths(self):
        self.install('--agent','unknown',success=False)
        self.env['CODEX_HOME']='relative'
        self.install('--agent','codex',success=False)

    def test_mcp_preflight_and_install_remain_independent(self):
        shutil.copytree(SOURCE / 'mcp', self.repo / 'mcp')
        config = self.base / 'mcp.json'
        config.write_text('invalid json')
        self.env['DOTAGENTS_CLAUDE_CONFIG'] = str(config)
        link = self.legacy('claude')
        self.install('--agent', 'claude', '--with-mcp', success=False)
        self.assertTrue(link.is_symlink())
        self.assertFalse((self.home / 'claude/cache').exists())
        config.write_text('{}')
        self.install('--agent', 'claude', '--with-mcp')
        self.assertIn('github', json.loads(config.read_text())['mcpServers'])
        self.assertFalse(link.is_symlink())
        self.install('--agent', 'claude', '--with-mcp', '--uninstall')
        self.assertNotIn('github', json.loads(config.read_text()).get('mcpServers', {}))
