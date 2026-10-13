#!/usr/bin/env python3
"""Local launcher and interactive credential setup for Keycloak MCP."""
import getpass
import json
import os
from pathlib import Path
import sys
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request

BASE = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'keycloak-mcp-server'
REVISION = '692b2a62cad13ea3d8d1a43b3a00d867d1d2288e'
ENTRY = BASE / REVISION / 'dist/index.js'
CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'keycloak-mcp/credentials.json'
URL = 'https://auth.paradaux.io'


def setup():
    """Build the exact upstream revision used by the original local installation."""
    if ENTRY.is_file():
        print('Pinned Keycloak MCP build is already installed.')
        return
    for command in ('git', 'npm', 'node'):
        if not shutil.which(command):
            raise SystemExit(f'{command} is required for --setup.')
    BASE.mkdir(parents=True, exist_ok=True)
    destination = BASE / REVISION
    if destination.exists():
        raise SystemExit('Incomplete build exists at ' + str(destination) + '; move it aside and retry.')
    with tempfile.TemporaryDirectory(prefix='.build-', dir=BASE) as temporary:
        checkout = Path(temporary) / 'source'
        subprocess.run(['git', 'init', str(checkout)], check=True)
        subprocess.run(['git', '-C', str(checkout), 'fetch', '--depth=1',
                        'https://github.com/M0-AR/keycloak-mcp-server.git', REVISION], check=True)
        subprocess.run(['git', '-C', str(checkout), 'checkout', '--detach', 'FETCH_HEAD'], check=True)
        subprocess.run(['npm', 'ci', '--ignore-scripts'], cwd=checkout, check=True)
        subprocess.run(['npm', 'run', 'build'], cwd=checkout, check=True)
        if not (checkout / 'dist/index.js').is_file():
            raise SystemExit('Keycloak build did not produce dist/index.js.')
        os.replace(checkout, destination)
    print('Pinned Keycloak MCP build installed. Run this launcher with --configure next.')


def configure():
    if not sys.stdin.isatty():
        raise SystemExit('Run --configure in an interactive terminal; credentials are never accepted as command-line arguments.')
    username = input('Keycloak master-realm admin username: ').strip()
    password = getpass.getpass('Keycloak admin password (hidden): ')
    if not username or not password:
        raise SystemExit('Username and password are required. No credentials saved.')
    payload = urllib.parse.urlencode({
        'client_id': 'admin-cli', 'grant_type': 'password',
        'username': username, 'password': password,
    }).encode()
    try:
        request = urllib.request.Request(URL + '/realms/master/protocol/openid-connect/token', data=payload)
        with urllib.request.urlopen(request, timeout=20) as response:
            token = json.load(response)['access_token']
        request = urllib.request.Request(URL + '/admin/realms/minecraft/clients',
                                        headers={'Authorization': 'Bearer ' + token})
        with urllib.request.urlopen(request, timeout=20) as response:
            clients = json.load(response)
        if not isinstance(clients, list):
            raise ValueError('Unexpected response')
    except urllib.error.HTTPError as error:
        raise SystemExit(f'Keycloak verification failed (HTTP {error.code}). No credentials saved.')
    except Exception:
        raise SystemExit('Could not verify Keycloak access. No credentials saved.')
    CONFIG.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(CONFIG.parent, 0o700)
    fd, temporary = tempfile.mkstemp(prefix='.credentials-', dir=CONFIG.parent)
    try:
        with os.fdopen(fd, 'w') as output:
            json.dump({'username': username, 'password': password}, output)
        os.replace(temporary, CONFIG)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print('Keycloak login and read-only client access verified. Credentials saved with owner-only access.')
    print('The keycloak MCP configuration is ready. Start a new Claude Code or Codex session to load it.')


def launch():
    try:
        if CONFIG.stat().st_mode & 0o077:
            raise SystemExit('Refusing credentials readable by other users; set file permissions to 0600.')
        credentials = json.loads(CONFIG.read_text())
        username, password = credentials['username'], credentials['password']
        if not username or not password:
            raise ValueError('Empty credential')
    except (OSError, ValueError, KeyError):
        raise SystemExit('Keycloak credentials are not configured. Run: python3 ' + str(Path(__file__).resolve()) + ' --configure')
    # Pass only the runtime environment needed by the server, not unrelated secrets.
    env = {key: os.environ[key] for key in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'NODE_EXTRA_CA_CERTS') if key in os.environ}
    env.update(KEYCLOAK_URL=URL, KEYCLOAK_ADMIN=username, KEYCLOAK_ADMIN_PASSWORD=password)
    node = shutil.which('node')
    if not node or not ENTRY.is_file():
        raise SystemExit('Install Node.js, then run this launcher with --setup first.')
    os.execve(node, [node, str(ENTRY)], env)


if __name__ == '__main__':
    if sys.argv[1:] == ['--setup']:
        setup()
    elif sys.argv[1:] == ['--configure']:
        configure()
    elif not sys.argv[1:]:
        launch()
    else:
        raise SystemExit('Usage: keycloak.py [--setup|--configure]')
