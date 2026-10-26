"""CLI: python3 -m radar {run,status,explain,interests}."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import agent, dashboard, interests, pipeline, render, store
from .util import now


def cmd_run(args) -> int:
    cfg = pipeline.load_config(Path(args.config) if args.config else None)
    summary = pipeline.run(
        cfg,
        lookback_hours=args.hours,
        dry_run=args.dry_run,
        force=args.force,
        backfill=args.backfill,
        verbose=not args.quiet,
    )
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def cmd_dashboard(args) -> int:
    cfg = pipeline.load_config()
    conn = store.connect()
    out = dashboard.build(cfg, conn, days=args.days)
    data = json.loads("{}")
    size = out.stat().st_size / 1024
    print(f"看板已生成：{out}（{size:.0f} KB）")
    print(f"直接打开：open {out}")
    return 0


def cmd_serve(args) -> int:
    import functools
    import http.server
    import socketserver
    import threading
    import webbrowser

    cfg = pipeline.load_config()
    conn = store.connect()
    out = dashboard.build(cfg, conn, days=args.days)
    root = str(Path(out).parent)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
    port = args.port
    try:
        httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), handler)
    except OSError as exc:
        print(f"端口 {port} 不可用：{exc}（换一个：--port 8790）")
        return 1
    url = f"http://127.0.0.1:{port}/dashboard.html"
    print(f"看板已启动：{url}")
    print("Ctrl+C 结束。阅读状态保存在这个浏览器里。")
    if not args.no_open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
    finally:
        httpd.server_close()
    return 0


def cmd_agent(args) -> int:
    cfg = pipeline.load_config()
    acfg = agent.load_config()
    acfg.setdefault("field", cfg.get("profile", {}).get("field_zh", ""))
    if not agent.enabled(acfg):
        print("agent 未启用或缺少 API key：")
        print(f"  1) 编辑 {agent.CONFIG_PATH}")
        print(f"  2) export {acfg.get('api_key_env', 'AGENT_API_KEY')}=<你的 key>")
        return 1
    conn = store.connect()
    today = now().date()
    import datetime as _dt

    since = today.isoformat() + "T00:00:00"
    rows = conn.execute(
        "SELECT * FROM items WHERE first_seen >= ? ORDER BY score DESC LIMIT 20", (since,)
    ).fetchall()
    if not rows:  # 今天还没跑过，就用最近 7 天的高分条目
        since = (today - _dt.timedelta(days=7)).isoformat()
        rows = conn.execute(
            "SELECT * FROM items WHERE COALESCE(NULLIF(published,''), first_seen) >= ? "
            "ORDER BY score DESC LIMIT 20",
            (since,),
        ).fetchall()
    items = [dict(r) for r in rows]
    if not items:
        print("库里没有可点评的条目，先跑 python3 -m radar run")
        return 1
    res = agent.enrich(acfg, conn, items, today, force=args.force)
    print("\n点评：" + (res.get("overview") or "（空）"))
    for k, v in list(res.get("items", {}).items())[:10]:
        print(f"  - {v}")
    if not args.no_build:
        out = dashboard.build(cfg, conn)
        print(f"\n看板已更新：{out}")
    return 0


def cmd_agent_test(args) -> int:
    return agent.self_test()


def cmd_status(args) -> int:
    cfg = pipeline.load_config()
    conn = store.connect()
    runs = store.recent_runs(conn, 8)
    total = conn.execute("SELECT COUNT(*) c FROM items").fetchone()["c"]
    last7 = conn.execute(
        "SELECT COUNT(*) c FROM items WHERE first_seen >= date('now','-7 day')"
    ).fetchone()["c"]
    print(f"条目总数 {total} · 近 7 天 {last7}")
    print(f"数据库 {store.DB_PATH}")
    print("")
    if not runs:
        print("还没有运行记录，先执行: python3 -m radar run")
        return 1
    print("| 开始时间 | 状态 | 抓取 | 新增 | 入库 | 日报 |")
    print("| --- | --- | --- | --- | --- | --- |")
    for r in runs:
        print(
            f"| {r['started'][:16]} | {r['status']} | {r['fetched']} | {r['new_items']} | "
            f"{r['kept']} | {Path(r['digest'] or '').name} |"
        )
    note = runs[0].get("note")
    if note:
        try:
            errs = {k: v for k, v in json.loads(note).get("stats", {}).items() if v.get("error")}
        except Exception:
            errs = {}
        if errs:
            print("\n数据源异常：")
            for k, v in errs.items():
                print(f"- {k}: {v['error']}")
    trends = render.topic_trends(conn, now().date(), cfg)
    names = {t["id"]: t.get("name", t["id"]) for t in cfg.get("topics", [])}
    print("\n近 7 天各主题条目数：")
    for tid, tr in sorted(trends.items(), key=lambda kv: -kv[1]["week"]):
        print(f"- {names.get(tid, tid)}: {tr['week']}（基线 {tr['baseline']}/周，比值 {tr['ratio']}）")
    return 0


def cmd_explain(args) -> int:
    pipeline.explain(args.text)
    return 0


def cmd_interests(args) -> int:
    cfg = pipeline.load_config()
    result = interests.scan(cfg, days=args.days, limit=args.limit)
    result["topic_names"] = {t["id"]: t.get("name", t["id"]) for t in cfg.get("topics", [])}
    print(interests.render_report(result))
    out = Path(store.DB_PATH).parent / "interest_suggestions.json"
    interests.save(result, out)
    print(f"\n已保存：{out}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="radar", description="科研热点自动追踪雷达")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="抓取并生成今日日报")
    p_run.add_argument("--hours", type=float, default=None, help="回看小时数（默认取配置）")
    p_run.add_argument("--dry-run", action="store_true", help="只打印，不写文件")
    p_run.add_argument("--force", action="store_true", help="忽略缓存重新抓取")
    p_run.add_argument(
        "--backfill", action="store_true",
        help="一次性补历史：按发表日期而不是今天记录 first_seen",
    )
    p_run.add_argument("--json", action="store_true", help="末尾输出 JSON 摘要")
    p_run.add_argument("--config", default=None)
    p_run.add_argument("--quiet", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_dash = sub.add_parser("dashboard", help="重新生成 HTML 看板")
    p_dash.add_argument("--days", type=int, default=120, help="看板里保留多少天")
    p_dash.set_defaults(func=cmd_dashboard)

    p_serve = sub.add_parser("serve", help="本地起服务并打开看板")
    p_serve.add_argument("--port", type=int, default=8788)
    p_serve.add_argument("--days", type=int, default=120)
    p_serve.add_argument("--no-open", action="store_true")
    p_serve.set_defaults(func=cmd_serve)

    p_agent = sub.add_parser("agent", help="只跑 agent 点评（可重复调用，省钱）")
    p_agent.add_argument("--force", action="store_true", help="忽略当天已有结果，重新生成")
    p_agent.add_argument("--no-build", action="store_true", help="不重建看板")
    p_agent.set_defaults(func=cmd_agent)

    p_at = sub.add_parser("agent-test", help="测试 agent API 是否可用")
    p_at.set_defaults(func=cmd_agent_test)

    p_status = sub.add_parser("status", help="查看运行历史与主题热度")
    p_status.set_defaults(func=cmd_status)

    p_explain = sub.add_parser("explain", help="诊断一段标题/摘要的相关度打分")
    p_explain.add_argument("text")
    p_explain.set_defaults(func=cmd_explain)

    p_int = sub.add_parser("interests", help="从 Codex 会话中统计你的关注点，给出配置建议")
    p_int.add_argument("--days", type=int, default=45)
    p_int.add_argument("--limit", type=int, default=30)
    p_int.set_defaults(func=cmd_interests)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
