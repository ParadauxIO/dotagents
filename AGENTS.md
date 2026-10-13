# Working with dotagents

For installation, updates, or recurring maintenance, read [MAINTENANCE.md](MAINTENANCE.md)
and follow the saved installation workflow in [README.md](README.md). Use the
permanent installation checkout, not a development worktree, for user updates.

For repository changes, validate with `python3 -m unittest discover -s tests -v`
and `bash -n install.sh`; run `shellcheck install.sh` when available. Tests must
use temporary homes and local Git remotes, not real agent configuration or secrets.
