#!/usr/bin/env bash
set -euo pipefail

OS_ROOT="/home/ZykLyj/yjdev/personal-agent-os"
MANAGED_ROOT="$OS_ROOT/skills"
COMPAT_PARENT="/home/ZykLyj/.agents"
COMPAT_PATH="$COMPAT_PARENT/skills"
EXPECTED_LINK="../yjdev/personal-agent-os/skills"

usage() {
  cat <<'USAGE'
Usage:
  manage-skills.sh verify
  manage-skills.sh status
  manage-skills.sh relink

Commands:
  verify  Check compatibility symlink and managed skill layout.
  status  Show Git status for managed skills.
  relink  Recreate /home/ZykLyj/.agents/skills if it is missing or a symlink.
USAGE
}

verify_symlink() {
  if [[ ! -L "$COMPAT_PATH" ]]; then
    printf 'ERROR: %s is not a symlink\n' "$COMPAT_PATH" >&2
    return 1
  fi

  local actual
  actual="$(readlink "$COMPAT_PATH")"
  if [[ "$actual" != "$EXPECTED_LINK" ]]; then
    printf 'ERROR: %s points to %s, expected %s\n' "$COMPAT_PATH" "$actual" "$EXPECTED_LINK" >&2
    return 1
  fi

  if [[ "$(realpath "$COMPAT_PATH")" != "$(realpath "$MANAGED_ROOT")" ]]; then
    printf 'ERROR: %s does not resolve to %s\n' "$COMPAT_PATH" "$MANAGED_ROOT" >&2
    return 1
  fi
}

verify_skills() {
  local missing=0
  local found=0
  local skill

  shopt -s nullglob
  for skill in "$MANAGED_ROOT"/*; do
    [[ -d "$skill" ]] || continue
    [[ "$(basename "$skill")" == "README.md" ]] && continue
    found=1
    if [[ ! -f "$skill/SKILL.md" ]]; then
      printf 'ERROR: missing SKILL.md in %s\n' "$skill" >&2
      missing=1
    fi
  done
  shopt -u nullglob

  if [[ "$found" -eq 0 ]]; then
    printf 'ERROR: no managed skills found in %s\n' "$MANAGED_ROOT" >&2
    return 1
  fi

  return "$missing"
}

verify() {
  verify_symlink
  verify_skills
  printf 'OK: managed skills symlink and layout are valid\n'
}

status() {
  git -C "$OS_ROOT" status --short -- README.md skills scripts/manage-skills.sh
}

relink() {
  mkdir -p "$COMPAT_PARENT"

  if [[ -e "$COMPAT_PATH" && ! -L "$COMPAT_PATH" ]]; then
    printf 'ERROR: %s exists and is not a symlink; refusing to replace it\n' "$COMPAT_PATH" >&2
    return 1
  fi

  rm -f "$COMPAT_PATH"
  ln -s "$EXPECTED_LINK" "$COMPAT_PATH"
  verify
}

case "${1:-verify}" in
  verify)
    verify
    ;;
  status)
    status
    ;;
  relink)
    relink
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
