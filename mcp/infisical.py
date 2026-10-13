#!/usr/bin/env python3
"""Launch the installed Infisical MCP with private Universal Auth credentials."""
import json
import os
from pathlib import Path
import shutil
import subprocess

CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'infisical-mcp/credentials.json'


def launch():
    try:
        if CONFIG.stat().st_mode & 0o077:
            raise SystemExit('Refusing credentials readable by other users; set file permissions to 0600.')
        credentials = json.loads(CONFIG.read_text())
        host, client_id, secret = (credentials[key] for key in ('host', 'clientId', 'clientSecret'))
        if not all(isinstance(value, str) and value.strip() for value in (host, client_id, secret)):
            raise ValueError('Missing credential')
    except (OSError, ValueError, KeyError, TypeError):
        raise SystemExit('Configure Infisical credentials at ' + str(CONFIG) + '; see mcp/README.md.')
    node, npm = shutil.which('node'), shutil.which('npm')
    if not node or not npm:
        raise SystemExit('Node.js and npm are required for Infisical MCP.')
    result = subprocess.run([npm, 'root', '-g'], capture_output=True, text=True, check=True)
    entry = Path(result.stdout.strip()) / '@infisical/mcp/dist/index.js'
    if not entry.is_file():
        raise SystemExit('Install the MCP package: npm install -g @infisical/mcp@0.0.24')
    env = {key: os.environ[key] for key in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'NODE_EXTRA_CA_CERTS') if key in os.environ}
    env.update(INFISICAL_HOST_URL=host, INFISICAL_AUTH_METHOD='universal-auth',
               INFISICAL_UNIVERSAL_AUTH_CLIENT_ID=client_id,
               INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET=secret)
    os.execve(node, [node, str(entry)], env)


if __name__ == '__main__':
    launch()
