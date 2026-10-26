#!/bin/bash
# 卸载 launchd 定时任务。
set -uo pipefail
LABEL="com.zhouy.research-radar"
DEST="$HOME/Library/LaunchAgents/$LABEL.plist"

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$DEST"
echo "已卸载 $LABEL（$DEST）"
