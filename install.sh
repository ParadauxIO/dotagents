#!/usr/bin/env bash
# Link the canonical skills into each agent's personal skills directory.
# Bash 3.2 (shipped with macOS) treats empty arrays as unset under nounset.
set -eo pipefail

usage() {
  cat <<'EOF'
Usage: bash install.sh [--agent all|claude|codex] [--uninstall] [--dry-run]

Defaults to installing for both agents. Existing unrelated files are never replaced.
Environment: DOTAGENTS_CLAUDE_SKILLS_DIR, DOTAGENTS_CODEX_SKILLS_DIR
EOF
}

die() { printf 'dotagents: %s\n' "$*" >&2; exit 1; }
agent=all
uninstall=false
dry_run=false
while (($#)); do
  case "$1" in
    --agent)
      (($# >= 2)) || die '--agent requires all, claude, or codex'
      agent=$2; shift 2 ;;
    --uninstall) uninstall=true; shift ;;
    --dry-run) dry_run=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown argument: $1" ;;
  esac
done

root=$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
source_dir="$root/skills"
[[ -d "$source_dir" ]] || die "Missing skills directory: $source_dir"
targets=()
case "$agent" in
  all|claude) targets+=("${DOTAGENTS_CLAUDE_SKILLS_DIR:-${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills}") ;;
  codex) ;;
  *) die "Unknown agent: $agent" ;;
esac
if [[ "$agent" == all || "$agent" == codex ]]; then
  targets+=("${DOTAGENTS_CODEX_SKILLS_DIR:-$HOME/.agents/skills}")
fi

shopt -s nullglob
skills=()
if ! "$uninstall"; then
  for skill in "$source_dir"/*; do
    [[ -d "$skill" ]] || continue
    [[ -f "$skill/SKILL.md" ]] || die "Missing SKILL.md: $skill"
    name=${skill##*/}
    [[ "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ && ${#name} -le 64 ]] || die "Invalid skill directory name: $name"
    [[ "$name" != synced && "$name" != anthropic-skills ]] || die "Reserved skill name: $name"
    skills+=("$skill")
  done
fi

# Preflight every destination before making any changes.
for target in "${targets[@]}"; do
  [[ "$target" == /* ]] || die "Destination must be absolute: $target"
  [[ ! -e "$target" || -d "$target" ]] || die "Not a directory: $target"
  [[ ! -L "$target" || -d "$target" ]] || die "Broken destination symlink: $target"
  if ! "$uninstall"; then
    for skill in "${skills[@]}"; do
      dest="$target/${skill##*/}"
      if [[ -L "$dest" && "$(readlink "$dest")" == "$skill" ]]; then
        continue
      fi
      [[ ! -e "$dest" && ! -L "$dest" ]] || die "Conflict at $dest; move it yourself before installing."
    done
  fi
done

for target in "${targets[@]}"; do
  # Only remove exact links this checkout could have created, including stale links.
  for dest in "$target"/*; do
    [[ -L "$dest" ]] || continue
    expected="$source_dir/${dest##*/}"
    [[ "$(readlink "$dest")" == "$expected" ]] || continue
    if "$uninstall" || [[ ! -f "$expected/SKILL.md" ]]; then
      printf 'Remove %s\n' "$dest"
      if ! "$dry_run"; then rm -- "$dest"; fi
    fi
  done
  if ! "$uninstall"; then
    for skill in "${skills[@]}"; do
      dest="$target/${skill##*/}"
      [[ ! -L "$dest" ]] || continue
      printf 'Link %s -> %s\n' "$dest" "$skill"
      if ! "$dry_run"; then
        mkdir -p -- "$target"
        ln -s -- "$skill" "$dest"
      fi
    done
  fi
done
if "$uninstall"; then
  printf 'Uninstall complete; checkout and unrelated skills retained.\n'
else
  printf 'Install complete: %s skill(s), agent=%s.\n' "${#skills[@]}" "$agent"
fi
if "$dry_run"; then printf 'Dry run: no changes made.\n'; fi
