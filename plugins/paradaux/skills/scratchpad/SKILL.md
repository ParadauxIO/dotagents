---
name: scratchpad
description: Use the project's .context/ directory for local scratch scripts, notes, intermediate files, and other temporary task artifacts whenever work needs scratch storage.
---

# Scratchpad

Use `.context/` at the current project or worktree root as the local scratchpad.
Create it as needed and put one-off scripts, notes, command output, downloads,
screenshots, and intermediate files there. Use descriptive filenames or task
subdirectories to avoid overwriting existing work.

Avoid `/tmp` for scratch storage: it is RAM-backed in this environment, so large
or accumulated artifacts consume memory. When a tool needs a temporary directory,
point its temporary-directory option or command-scoped `TMPDIR` at an absolute
path under `.context/` instead of relying on its `/tmp` default.

Keep scratch artifacts out of commits. Respect existing ignore rules; if
`.context/` is not ignored in a Git repository, add it to the repository's local
exclude file (`git rev-parse --git-path info/exclude`). Preserve existing scratch
files and remove only artifacts created for the current task when cleanup is
needed. Deliverable source files and reusable project scripts belong in their
normal project locations.
