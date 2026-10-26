#!/usr/bin/env python3
"""Verify the pipeline locally, or a deployed GitHub Pages board.

    python3 scripts/verify.py --local
    python3 scripts/verify.py --url https://<user>.github.io/research-radar/

Exit code 0 = all checks pass. Prints one line per check.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TZ = timezone(timedelta(hours=8))
ok_all = True


def check(name: str, cond: bool, detail: str = "") -> bool:
    global ok_all
    print(f"{'PASS' if cond else 'FAIL'}  {name}{('  — ' + detail) if detail else ''}")
    ok_all = ok_all and cond
    return cond


def local() -> None:
    cfg = ROOT / "config" / "config.json"
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
        check("config/config.json 可解析", True, f"{len(data.get('topics', []))} 个主题")
        check("主题数 >= 5", len(data.get("topics", [])) >= 5)
    except Exception as exc:
        check("config/config.json 可解析", False, str(exc))
        return

    db = ROOT / "state" / "radar.sqlite3"
    check("SQLite 存在", db.exists(), str(db))
    if db.exists():
        conn = sqlite3.connect(str(db))
        n_items = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        n_runs = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        check("条目 > 0", n_items > 0, f"{n_items} 条")
        check("运行记录 > 0", n_runs > 0, f"{n_runs} 次")
        n_notes = conn.execute("SELECT COUNT(*) FROM agent_notes").fetchone()[0]
        print(f"INFO  agent 点评：{n_notes} 条（0 表示今天还没生成）")

    board = ROOT / "dashboard.html"
    index = ROOT / "index.html"
    check("dashboard.html 存在", board.exists())
    check("index.html 存在（Pages 入口）", index.exists())
    if board.exists():
        html = board.read_text(encoding="utf-8", errors="replace")
        check("看板内嵌数据", "const DATA" in html)
        m = re.search(r'"generated":"([0-9-]{10})', html)
        today = datetime.now(TZ).date()
        if m:
            gen = date.fromisoformat(m.group(1))
            check("看板是今天生成的", gen == today, f"generated={gen}")
        check("看板里有条目", bool(re.search(r'"items":\[\{"k"', html)))
    if board.exists() and index.exists():
        check(
            "index.html 与 dashboard.html 一致",
            board.read_bytes() == index.read_bytes(),
        )

    if (ROOT / ".git").exists():
        print("INFO  已有 .git，deploy.py 会复用并推送")
    else:
        print("INFO  还没有 .git，deploy.py 会自动 git init")


def fetch(url: str, timeout: int = 30) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "research-radar-verify"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")[:300]
    except Exception as exc:
        return 0, str(exc)


def remote(base: str) -> None:
    base = base.rstrip("/") + "/"
    status, html = fetch(base)
    check(f"{base} 可访问", status == 200, f"HTTP {status}")
    if status != 200:
        print("提示：首次开启 Pages 需要 1–3 分钟；确认 Settings → Pages 的 Source 是 main / (root)")
        print(f"      {html[:200]}")
        return
    check("页面是科研雷达看板", "科研雷达" in html and "const DATA" in html)

    status2, _ = fetch(base + "dashboard.html")
    check(f"{base}dashboard.html 可访问", status2 == 200, f"HTTP {status2}")

    m = re.search(r'"generated":"([0-9-]{10})', html)
    if m:
        gen = date.fromisoformat(m.group(1))
        today = datetime.now(TZ).date()
        check("看板日期是今天或昨天", (today - gen).days <= 1, f"generated={gen}，今天={today}")
        m2 = re.search(r'"days":\[(\{.*?\})\]', html)
        if m2:
            print(f"INFO  历史天数数据已嵌入")
    else:
        check("看板内含 generated 字段", False)

    m3 = re.search(r'"items":\[(.*?)\],"trends"', html)
    if m3:
        n = m3.group(1).count('"k":')
        check("条目数 > 0", n > 0, f"{n} 条")
    check("有今日点评（需要 AGENT_API_KEY）", "今日点评" in html, "没有也不影响主流程")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--url", default="")
    args = ap.parse_args()
    if not args.local and not args.url:
        args.local = True
    if args.local:
        print("== 本地检查 ==")
        local()
    if args.url:
        print("\n== 线上检查 ==")
        remote(args.url)
    print("\n结果：" + ("全部通过" if ok_all else "有失败项"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
