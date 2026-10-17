#!/usr/bin/env python3
"""Install the local skill plugin; preserve unrelated plugins and legacy files."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
MARKET = 'paradaux-local'
PLUGIN = f'paradaux@{MARKET}'


def run(args, *, capture=False):
    result = subprocess.run(args, check=True, text=True,
                            stdout=subprocess.PIPE if capture else None)
    return json.loads(result.stdout) if capture else None


def validate():
    package = ROOT / 'plugins/paradaux'
    manifests = [json.loads((package / p).read_text()) for p in
                 ('plugin.json', '.claude-plugin/plugin.json')]
    catalog = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
    entry = catalog['plugins'][0]
    if (catalog['name'] != MARKET or len(catalog['plugins']) != 1
            or entry['name'] != 'paradaux' or entry['source'] != './plugins/paradaux'
            or any(m['name'] != 'paradaux' or m['version'] != entry['version'] for m in manifests)):
        raise ValueError('Plugin manifests and marketplace identity/version must agree.')
    for skill in (package / 'skills').iterdir():
        if not skill.is_dir():
            continue
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', skill.name) or len(skill.name) > 64:
            raise ValueError(f'Invalid skill name: {skill.name}')
        content = (skill / 'SKILL.md').read_text()
        if not re.search(r'^name: ' + re.escape(skill.name) + r'\s*$', content, re.M):
            raise ValueError(f'Skill name must match directory: {skill}')


def locations(agent):
    home = Path.home()
    if agent == 'claude':
        config = Path(os.environ.get('CLAUDE_CONFIG_DIR', home / '.claude'))
        legacy = Path(os.environ.get('DOTAGENTS_CLAUDE_SKILLS_DIR', config / 'skills'))
    else:
        config = Path(os.environ.get('CODEX_HOME', home / '.codex'))
        legacy = Path(os.environ.get('DOTAGENTS_CODEX_SKILLS_DIR', home / '.agents/skills'))
    for path in (config, legacy):
        if not path.is_absolute() or (path.exists() and not path.is_dir()):
            raise ValueError(f'Expected absolute directory: {path}')
    return config, legacy


def marketplace(agent, config):
    if not config.exists():
        return None
    data = run([agent, 'plugin', 'marketplace', 'list', '--json'], capture=True)
    entries = data['marketplaces'] if agent == 'codex' else data
    found = [entry for entry in entries if entry['name'] == MARKET]
    if not found:
        return None
    entry = found[0]
    if agent == 'codex':
        source = entry.get('marketplaceSource', {})
        path = source.get('source') if source.get('sourceType') == 'local' else None
    else:
        path = entry.get('path') if entry.get('source') == 'directory' else None
    if not path or Path(path).resolve() != ROOT:
        raise ValueError(f'Conflict: {agent} marketplace {MARKET} belongs to another source.')
    return entry


def legacy_links(directory):
    if not directory.exists():
        return []
    # Match the old installer's exact link convention, including broken links.
    return [p for p in directory.iterdir() if p.is_symlink()
            and os.readlink(p) == str(ROOT / 'skills' / p.name)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', choices=['all', 'claude', 'codex'], default='all')
    parser.add_argument('--with-mcp', action='store_true')
    parser.add_argument('--uninstall', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    agents = ['claude', 'codex'] if args.agent == 'all' else [args.agent]
    validate()
    if args.with_mcp and not args.dry_run:
        command = [sys.executable, str(ROOT / 'mcp/install.py'),
                   '--agent', args.agent, '--dry-run']
        if args.uninstall:
            command.append('--uninstall')
        # Detect invalid MCP files before a native CLI can change its own config.
        subprocess.run(command, check=True, stdout=subprocess.PIPE)
    plans = []
    # Preflight all selected clients before any installation or link removal.
    for agent in agents:
        config, legacy = locations(agent)
        if not args.dry_run and not shutil.which(agent):
            raise ValueError(f'{agent} CLI is required; install a version with native plugin commands.')
        current = marketplace(agent, config) if not args.dry_run else None
        plans.append((agent, config, legacy_links(legacy), current))
    for agent, config, links, current in plans:
        print(f'{"Uninstall" if args.uninstall else "Install/refresh"} {PLUGIN} for {agent}', flush=True)
        if not args.dry_run:
            if args.uninstall:
                if current:
                    # Native managers own caches and settings. Leave the marketplace
                    # registered so we never remove other manually added entries.
                    if agent == 'claude':
                        installed = run([agent, 'plugin', 'list', '--json'], capture=True)
                        if any(p['id'] == PLUGIN and p.get('scope') == 'user' for p in installed):
                            run([agent, 'plugin', 'uninstall', PLUGIN, '--scope', 'user'])
                    else:
                        run([agent, 'plugin', 'remove', PLUGIN])
            else:
                config.mkdir(parents=True, exist_ok=True)
                if not current:
                    run([agent, 'plugin', 'marketplace', 'add', str(ROOT)])
                if agent == 'claude':
                    installed = run([agent, 'plugin', 'list', '--json'], capture=True)
                    exists = any(p['id'] == PLUGIN and p.get('scope') == 'user' for p in installed)
                    run([agent, 'plugin', 'update' if exists else 'install', PLUGIN, '--scope', 'user'])
                else:
                    run([agent, 'plugin', 'add', PLUGIN])
        for link in links:
            print(f'Remove legacy link {link}', flush=True)
            if not args.dry_run:
                link.unlink()
    if args.with_mcp:
        command = [sys.executable, str(ROOT / 'mcp/install.py'), '--agent', args.agent]
        for flag in ('uninstall', 'dry_run'):
            if getattr(args, flag):
                command.append('--' + flag.replace('_', '-'))
        subprocess.run(command, check=True)
    print('Dry run: no changes made; native CLI/source checks deferred.' if args.dry_run
          else 'Complete. Restart selected clients to reload plugins. Marketplace registrations retained.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, IndexError, subprocess.CalledProcessError) as error:
        print(f'dotagents: {error}', file=sys.stderr)
        sys.exit(1)
