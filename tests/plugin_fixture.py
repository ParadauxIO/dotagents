"""Local CLI stand-ins: tests never contact services or real agent configuration."""
import os
from pathlib import Path
import shutil

SOURCE = Path(__file__).resolve().parents[1]


def copy_package(destination):
    for name in ('install.sh', 'plugin_install.py'):
        shutil.copyfile(SOURCE / name, destination / name)
    shutil.copytree(SOURCE / 'plugins', destination / 'plugins')
    shutil.copytree(SOURCE / '.claude-plugin', destination / '.claude-plugin')


def fake_clients(base, env):
    bindir = base / 'bin'
    bindir.mkdir()
    script = '''#!/usr/bin/env python3
import json, os, pathlib, shutil, sys
agent=pathlib.Path(sys.argv[0]).name
root=pathlib.Path(os.environ['CLAUDE_CONFIG_DIR' if agent=='claude' else 'CODEX_HOME'])
state=root/'fake.json'
data=json.loads(state.read_text()) if state.exists() else {}
a=sys.argv[1:]
if os.environ.get('FAIL_PLUGIN') == agent and a[:2] == ['plugin','add']:
    sys.exit(1)
if a[:3] == ['plugin','marketplace','list']:
    entries=[]
    if 'source' in data:
        entries=[{'name':'paradaux-local','source':'directory','path':data['source'],
                  'marketplaceSource':{'sourceType':'local','source':data['source']}}]
    print(json.dumps({'marketplaces':entries} if agent=='codex' else entries))
    sys.exit()
if a[:2] == ['plugin','list']:
    print(json.dumps([{'id':'paradaux@paradaux-local','scope':'user'}] if data.get('installed') else []))
    sys.exit()
root.mkdir(parents=True,exist_ok=True)
if a[:3] == ['plugin','marketplace','add']:
    data['source']=a[3]
elif a[1] in ('add','install','update'):
    data['installed']=True
    shutil.copytree(pathlib.Path(data['source'])/'plugins/paradaux',root/'cache',dirs_exist_ok=True)
elif a[1] in ('remove','uninstall'):
    data['installed']=False
    shutil.rmtree(root/'cache',ignore_errors=True)
else:
    sys.exit('unexpected command '+repr(a))
state.write_text(json.dumps(data))
'''
    for name in ('claude', 'codex'):
        path = bindir / name
        path.write_text(script)
        path.chmod(0o755)
    env['PATH'] = str(bindir) + os.pathsep + env['PATH']
