#!/usr/bin/env bash
set -euo pipefail

ROOT="${TERRA_BACKEND_ROOT:-/home/ZykLyj/yjdev/TerraOpenclawSetupBackend}"
WORKSPACE="$(dirname "$ROOT")"
DISCOVER=0
TASK=()
declare -A SEEN=()

usage() {
  cat <<'USAGE'
Usage:
  context-pack.sh [--discover] "<task summary>"
  context-pack.sh --help

Prints a Terra/OpenClaw onboarding context pack.

Sections:
  [required]  Mandatory context every Terra task must read.
  [linked]    Candidate files linked from project entry docs.
  [route]     Task-keyword routes; starting hypotheses, not a fact boundary.
  [discover]  Broader docs inventory for unfamiliar topics or new docs.

Environment:
  TERRA_BACKEND_ROOT  Override TerraOpenclawSetupBackend root.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --discover)
      DISCOVER=1
      shift
      ;;
    --)
      shift
      TASK+=("$@")
      break
      ;;
    *)
      TASK+=("$1")
      shift
      ;;
  esac
done

TASK_TEXT="${TASK[*]:-}"

canonical_path() {
  realpath -m "$1"
}

emit_path() {
  local label="$1"
  local path="$2"
  local canonical

  canonical="$(canonical_path "$path")"
  if [[ -n "${SEEN["$label:$canonical"]+x}" ]]; then
    return
  fi
  SEEN["$label:$canonical"]=1

  if [[ -e "$canonical" ]]; then
    printf '[%s] %s\n' "$label" "$canonical"
  else
    printf '[missing:%s] %s\n' "$label" "$canonical"
  fi
}

emit_glob() {
  local label="$1"
  local pattern="$2"
  local found=0

  shopt -s nullglob
  for path in $pattern; do
    emit_path "$label" "$path"
    found=1
  done
  shopt -u nullglob

  if [[ "$found" -eq 0 ]]; then
    printf '[missing:%s] %s\n' "$label" "$pattern"
  fi
}

is_path_like() {
  local raw="$1"

  [[ "$raw" == *"://"* ]] && return 1
  [[ "$raw" == mailto:* || "$raw" == "#"* || -z "$raw" ]] && return 1

  case "$raw" in
    /*|./*|../*|~/*|*/*|*.md|*.go|*.sh|*.yaml|*.yml|*.json|*.template|AGENTS.md)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

resolve_candidate() {
  local source_file="$1"
  local raw="$2"
  local source_dir candidate stripped canonical

  stripped="${raw%%#*}"
  stripped="${stripped%%\?*}"
  stripped="${stripped%\"}"
  stripped="${stripped#\"}"
  stripped="${stripped%\'}"
  stripped="${stripped#\'}"
  stripped="${stripped%>}"
  stripped="${stripped#<}"
  stripped="${stripped%/}"

  is_path_like "$stripped" || return 0

  source_dir="$(dirname "$source_file")"
  if [[ "$stripped" = /* ]]; then
    [[ -e "$(canonical_path "$stripped")" ]] && emit_path linked "$stripped"
    return 0
  fi

  for candidate in "$source_dir/$stripped" "$ROOT/$stripped" "$WORKSPACE/$stripped"; do
    canonical="$(canonical_path "$candidate")"
    if [[ -e "$canonical" ]]; then
      emit_path linked "$candidate"
      return 0
    fi
  done
}

emit_linked_candidates() {
  local source_file="$1"

  [[ -f "$source_file" ]] || return 0

  while IFS= read -r raw; do
    resolve_candidate "$source_file" "$raw"
  done < <({
    grep -oE '\]\([^)]+' "$source_file" | sed 's/^](//' || true
    grep -oE '`[^`]+`' "$source_file" | sed 's/^`//;s/`$//' || true
  } | sort -u)
}

echo "# Terra onboarding context pack"
printf 'task: %s\n' "${TASK_TEXT:-<not provided>}"
printf 'root: %s\n\n' "$ROOT"

echo "## Required"
emit_path required "$ROOT/AGENTS.md"
emit_glob required "$ROOT/docs/ai-collaboration/*.md"
emit_path required "$ROOT/docs/AI-ONBOARDING.md"
emit_path required "$ROOT/docs/INDEX.md"
emit_path required "$ROOT/docs/agents/usage.md"
emit_path required "$ROOT/docs/agents/domain.md"

echo
echo "## Linked candidates"
emit_linked_candidates "$ROOT/docs/AI-ONBOARDING.md"
emit_linked_candidates "$ROOT/docs/INDEX.md"
emit_linked_candidates "$ROOT/docs/agents/domain.md"

task_lc="$(printf '%s' "$TASK_TEXT" | tr '[:upper:]' '[:lower:]')"

echo
echo "## Routes"

case "$task_lc" in
  *provider*|*model*|*模型*|*厂商*|*verify*|*openclaw.json*)
    emit_path route "$ROOT/docs/modelconfig/implementation/claude/00-README.md"
    emit_path route "$ROOT/docs/modelconfig/implementation/claude/01-requirements.md"
    emit_path route "$ROOT/docs/modelconfig/implementation/claude/02-data-model.md"
    emit_path route "$ROOT/docs/modelconfig/implementation/claude/03-api-surface.md"
    emit_path route "$ROOT/docs/modelconfig/implementation/claude/05-edge-cases.md"
    emit_path route "$ROOT/docs/adr/0001-builtin-provider-custom-models.md"
    ;;
esac

case "$task_lc" in
  *restore*|*reset*|*snapshot*|*快照*|*回滚*)
    emit_path route "$ROOT/docs/restoreFromSyncToAsync/initial_plan.md"
    emit_path route "$ROOT/docs/troubleshooting.md"
    emit_path route "$ROOT/docs/ai-context.md"
    emit_path route "$ROOT/service/snapshot.go"
    emit_path route "$ROOT/handler/snapshot.go"
    emit_path route "$ROOT/model/snapshot.go"
    ;;
esac

case "$task_lc" in
  *packag*|*deb*|*install*|*nginx*|*migrat*|*打包*|*安装*|*迁移*)
    PKG="$WORKSPACE/terraclaw_worktrees/accumulateWithoutAppAndDirChange"
    emit_path route "$PKG/docs/ci-handoff.md"
    emit_path route "$PKG/build_root/usr/local/openclaw/scripts/install.sh"
    emit_glob route "$PKG/templates/*nginx*.template"
    emit_path route "$PKG/scripts/migrate-terraclaw-backup.sh"
    ;;
esac

case "$task_lc" in
  *"control ui"*|*gateway*|*上游*|*入口*|*前缀*)
    O="$WORKSPACE/openclaw"
    emit_path route "$O/.ai-context.md"
    emit_path route "$O/NAS2/INDEX.md"
    emit_path route "$O/NAS2/troubleshooting/issues.md"
    emit_path route "$O/config/gateway-config.md"
    ;;
esac

case "$task_lc" in
  *log*|*日志*|*observability*|*request_id*)
    PKG="$WORKSPACE/terraclaw_worktrees/accumulateWithoutAppAndDirChange"
    emit_path route "$ROOT/docs/logging-observability/README.md"
    emit_path route "$ROOT/scripts/logs/README.md"
    emit_path route "$PKG/build_root/usr/local/openclaw/bin/logs/README.md"
    ;;
esac

if [[ "$DISCOVER" -eq 1 ]]; then
  echo
  echo "## Discover"
  while IFS= read -r path; do
    emit_path discover "$path"
  done < <(find "$ROOT/docs" -type f -name '*.md' -print 2>/dev/null | sort)

  emit_path discover "$WORKSPACE/openclaw/.ai-context.md"
  emit_path discover "$WORKSPACE/openclaw/INDEX.md"
  emit_path discover "$WORKSPACE/openclaw/NAS2/INDEX.md"
  emit_path discover "$WORKSPACE/terraclaw_worktrees/accumulateWithoutAppAndDirChange/README.md"
  emit_path discover "$WORKSPACE/terraclaw_worktrees/accumulateWithoutAppAndDirChange/docs/ci-handoff.md"
  emit_path discover "$WORKSPACE/tai-backend/README.md"
fi

echo
echo "## Next"
echo "Read required files first, inspect linked candidates and routes, then follow source/tests/scripts discovered from those files."
