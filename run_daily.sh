#!/bin/bash
# 每日抓取入口：launchd 调用，也可手动执行。
# 用法：./run_daily.sh [--hours 48] [--dry-run] [--quiet]
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR" || exit 1
mkdir -p logs state daily

PY=/usr/bin/python3
[ -x "$PY" ] || PY="$(command -v python3)"
LOG="logs/run-$(date +%Y-%m-%d).log"

{
  echo "=== $(date '+%F %T') 开始"
  "$PY" -B -m radar run "$@"
  rc=$?
  echo "=== $(date '+%F %T') 结束 exit=$rc"
} >>"$LOG" 2>&1

rc=$?
if [ "$rc" -ne 0 ]; then
  echo "运行失败（exit=$rc），日志：$LOG" >&2
  tail -n 20 "$LOG" >&2
  exit "$rc"
fi

tail -n 3 "$LOG"
