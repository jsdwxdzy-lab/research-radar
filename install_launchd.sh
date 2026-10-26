#!/bin/bash
# 安装 launchd 定时任务：每天 07:40 跑一次（Mac 睡眠时会顺延到唤醒后）。
# 用法：bash install_launchd.sh [小时] [分钟]
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOUR="${1:-7}"
MIN="${2:-40}"
LABEL="com.zhouy.research-radar"
DEST="$HOME/Library/LaunchAgents/$LABEL.plist"

chmod +x "$DIR/run_daily.sh" 2>/dev/null || true
mkdir -p "$HOME/Library/LaunchAgents" "$DIR/logs"

cat >"$DEST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$DIR/run_daily.sh</string>
  </array>
  <key>WorkingDirectory</key><string>$DIR</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>$HOUR</integer>
    <key>Minute</key><integer>$MIN</integer>
  </dict>
  <key>RunAtLoad</key><false/>
  <key>ProcessType</key><string>Background</string>
  <key>Nice</key><integer>5</integer>
  <key>StandardOutPath</key><string>$DIR/logs/launchd.out.log</string>
  <key>StandardErrorPath</key><string>$DIR/logs/launchd.err.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$DEST"
launchctl enable "gui/$(id -u)/$LABEL"

echo "已安装：$DEST"
echo "计划时间：每天 ${HOUR}:$(printf '%02d' "$MIN")"
echo
launchctl print "gui/$(id -u)/$LABEL" 2>/dev/null | sed -n '1,12p' || true
echo
echo "立刻试跑一次： launchctl kickstart -k gui/$(id -u)/$LABEL"
echo "查看状态：     launchctl print gui/$(id -u)/$LABEL | grep -A2 -i 'last exit'"
