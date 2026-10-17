#!/usr/bin/env bash
# Install the paradaux plugin through each agent's native plugin manager.
set -eo pipefail
root=$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
exec python3 "$root/plugin_install.py" "$@"
