#!/usr/bin/env bash
set -euo pipefail

TASK="${*:-Terai task}"
ROOT="${TERAI_WORKSPACE:-/home/ZykLyj/yjdev}"
TAFS_SIDEBAR="$ROOT/tafs_sidebar"
TERAI_YE_SIDEBAR="$ROOT/terai_ye_sidebar"
MEETING_DIR="$TAFS_SIDEBAR/meeting_log"
TAFS="$ROOT/tafs"
TERAI_YE="$ROOT/terai_ye"

echo "# Terai context pack"
echo "task: $TASK"
echo "root: $ROOT"
echo

emit_if_exists() {
  local tag="$1"
  local path="$2"
  if [ -e "$path" ]; then
    echo "[$tag] $path"
  fi
}

task_lc="$(printf '%s' "$TASK" | tr '[:upper:]' '[:lower:]')"

echo "## Required"
emit_if_exists required "$TAFS_SIDEBAR/10-terai-onboarding-workflow.md"
emit_if_exists required "$TAFS_SIDEBAR/11-terai-current-facts.md"
emit_if_exists required "$TAFS_SIDEBAR/INDEX.md"
echo

echo "## Latest meetings"
if [ -d "$MEETING_DIR" ]; then
  find "$MEETING_DIR" -maxdepth 1 -type f -name '*_Terai.txt' | sort | tail -5 | while read -r f; do
    echo "[latest-meeting] $f"
  done
fi
echo

echo "## Current analysis"
emit_if_exists current "$TAFS_SIDEBAR/meeting_log/20260610_160214_Terai_analysis.md"
emit_if_exists current "$TAFS_SIDEBAR/meeting_log/20260610_terai_next_steps.md"
emit_if_exists current "$TERAI_YE_SIDEBAR/INDEX.md"
emit_if_exists current "$TERAI_YE_SIDEBAR/02-architecture-map.md"
emit_if_exists current "$TERAI_YE_SIDEBAR/05-tafs-comparison.md"
echo

echo "## Source anchors"
emit_if_exists source "$TAFS/cmd/tos-agentd/main.go"
emit_if_exists source "$TAFS/internal/httpapi/router.go"
emit_if_exists source "$TAFS/internal/worker/supervisor.go"
emit_if_exists source "$TAFS/internal/worker/child.go"
emit_if_exists source "$TAFS/internal/agent/agent.go"
emit_if_exists source "$TAFS/internal/plugin"
emit_if_exists source "$TAFS/internal/tools"
emit_if_exists source "$TERAI_YE/README.md"
emit_if_exists source "$TERAI_YE/src/router/index.ts"
emit_if_exists source "$TERAI_YE/src/api/index.ts"
emit_if_exists source "$TERAI_YE/package/terai-package/usr/local/terai/bin/terai-agent-shim"
echo

echo "## Routes"
case "$task_lc" in
  *model*|*模型*|*provider*|*llm*|*console*)
    emit_if_exists route "$TAFS_SIDEBAR/03-module-notes/backend-core.md"
    emit_if_exists route "$TAFS_SIDEBAR/03-module-notes/worker-agent-tools.md"
    ;;
esac
case "$task_lc" in
  *plugin*|*插件*|*skill*|*mcp*)
    emit_if_exists route "$TAFS_SIDEBAR/03-module-notes/plugin-system.md"
    emit_if_exists route "$TAFS_SIDEBAR/03-module-notes/worker-agent-tools.md"
    ;;
esac
case "$task_lc" in
  *chat*|*对话*|*agent*|*session*|*会话*)
    emit_if_exists route "$TAFS_SIDEBAR/09-chat-flow-mainline.md"
    emit_if_exists route "$TAFS_SIDEBAR/03-module-notes/worker-agent-tools.md"
    ;;
esac
case "$task_lc" in
  *document*|*文档*|*rag*|*知识库*|*向量*|*搜索*|*search*)
    emit_if_exists route "$TAFS_SIDEBAR/meeting_log/20260610_160214_Terai_analysis.md"
    emit_if_exists route "$TERAI_YE_SIDEBAR/03-module-notes/knowledge-and-skills.md"
    ;;
esac
case "$task_lc" in
  *frontend*|*前端*|*ui*|*vue*|*demo*|*ye*|*terai_ye*)
    emit_if_exists route "$TERAI_YE_SIDEBAR/03-module-notes/frontend-app.md"
    emit_if_exists route "$TERAI_YE_SIDEBAR/03-module-notes/packaging-runtime.md"
    emit_if_exists route "$TERAI_YE_SIDEBAR/03-module-notes/shim-backend.md"
    ;;
esac
case "$task_lc" in
  *packag*|*打包*|*install*|*安装*|*nginx*|*systemd*|*tos*)
    emit_if_exists route "$TERAI_YE_SIDEBAR/03-module-notes/packaging-runtime.md"
    emit_if_exists route "$TAFS_SIDEBAR/07-validation-and-risks.md"
    ;;
esac
echo

echo "## Next"
echo "Read [required], then latest meeting records when product direction is in scope, then current facts. Treat terai_ye as demo/reference and old analysis as historical unless 11-terai-current-facts.md still confirms it."
