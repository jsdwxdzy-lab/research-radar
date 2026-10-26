"""Markdown digest rendering."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from .store import topic_counts
from .util import WEEKDAYS_ZH, clean, next_occurrence

ROOT = Path(__file__).resolve().parent.parent

SHORT = {
    "csp": "CSP",
    "crystal-gen": "生成设计",
    "mlip": "MLIP",
    "property": "性质筛选",
    "defect": "缺陷无序",
    "ai4s": "AI4S",
}


def _tags(item: dict) -> str:
    return " ".join(f"`{SHORT.get(t, t)}`" for t in (item.get("topics") or [])[:4])


def _matched_line(item: dict, limit: int = 5) -> str:
    kws, seen = [], set()
    for m in item.get("matched") or []:
        kw = m.get("kw")
        if kw and kw not in seen:
            seen.add(kw)
            kws.append(kw)
    if not kws:
        return ""
    more = f" 等 {len(kws)} 个" if len(kws) > limit else ""
    return "命中：" + "、".join(kws[:limit]) + more


def _fmt_item(item: dict, max_abs: int = 0, note: str = "") -> str:
    title = clean(item.get("title", ""), 300)
    url = item.get("url") or (f"https://doi.org/{item['doi']}" if item.get("doi") else "")
    head = f"- **[{title}]({url})**" if url else f"- **{title}**"
    meta = []
    if item.get("venue"):
        meta.append(f"*{clean(item['venue'], 46)}*")
    if item.get("published"):
        meta.append(str(item["published"]))
    extra = item.get("extra") or {}
    for name in extra.get("author_hits") or []:
        meta.append(f"👤{name}")
    if item.get("arxiv_id"):
        meta.append(f"[PDF](https://arxiv.org/pdf/{item['arxiv_id']})")
    n_src = len(extra.get("sources_seen") or [])
    if n_src > 1:
        meta.append(f"多源×{n_src}")
    if note:
        meta.append(note)
    lines = [head]
    second = []
    if _tags(item):
        second.append(_tags(item))
    if meta:
        second.append(" · ".join(meta))
    if second:
        lines.append("  " + " · ".join(second))
    hits = _matched_line(item)
    if hits and max_abs:
        lines.append(f"  <sub>{hits}</sub>")
    why = (item.get("extra") or {}).get("why") or item.get("why") or ""
    if why and max_abs:
        lines.append(f"  <sub>💡 {why}</sub>")
    abstract = clean(item.get("abstract", ""), max_abs) if max_abs else ""
    if abstract:
        lines.append(f"  > {abstract}")
    return "\n".join(lines)


def _fmt_compact(item: dict) -> str:
    title = clean(item.get("title", ""), 220)
    url = item.get("url") or (f"https://doi.org/{item['doi']}" if item.get("doi") else "")
    label = f"[{title}]({url})" if url else title
    bits = []
    if item.get("venue"):
        bits.append(f"*{clean(item['venue'], 36)}*")
    if item.get("published"):
        bits.append(str(item["published"]))
    meta = f" — {' · '.join(bits)}" if bits else ""
    return f"- {label}{meta}"


def topic_trends(conn, run_date: date, cfg: dict) -> dict:
    week_start = (run_date - timedelta(days=6)).isoformat()
    tomorrow = (run_date + timedelta(days=1)).isoformat()
    base_start = (run_date - timedelta(days=27)).isoformat()
    cur = topic_counts(conn, week_start, tomorrow)
    prev = topic_counts(conn, base_start, week_start)
    row = conn.execute("SELECT MIN(first_seen) m FROM items").fetchone()
    span_days = 0
    if row and row["m"]:
        try:
            span_days = (run_date - date.fromisoformat(str(row["m"])[:10])).days
        except ValueError:
            span_days = 0
    out = {}
    for tid in [t["id"] for t in cfg.get("topics", [])]:
        c = cur.get(tid, 0)
        baseline = prev.get(tid, 0) / 3.0
        ratio = (c + 0.5) / (baseline + 0.5) if baseline or c else 0.0
        out[tid] = {
            "week": c,
            "baseline": round(baseline, 1),
            "ratio": round(ratio, 2),
            "span_days": span_days,
        }
    return out


def upcoming_events(cfg: dict, run_date: date) -> list[dict]:
    path = ROOT / cfg.get("calendar_file", "config/events.json")
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    window = int(data.get("window_days", 120))
    events = []
    for ev in data.get("events", []):
        try:
            nxt = next_occurrence(int(ev["month"]), int(ev.get("day", 15)), run_date)
        except Exception:
            continue
        delta = (nxt - run_date).days
        if 0 <= delta <= window:
            events.append({**ev, "next": nxt, "in_days": delta})
    events.sort(key=lambda e: e["in_days"])
    return events


def _trend_label(tr: dict | None) -> str:
    if not tr or tr["week"] == 0 or tr.get("span_days", 0) < 7:
        return ""
    ratio = tr.get("ratio") or 0
    if tr["baseline"] == 0:
        return " · 新增关注"
    if ratio >= 1.5:
        return f" · 升温 ↑{ratio:.1f}×"
    if ratio <= 0.6:
        return f" · 回落 ↓{ratio:.1f}×"
    return " · 持平"


def digest(
    *,
    cfg: dict,
    run_date: date,
    run_dt,
    since_dt,
    new_items: list[dict],
    db_items: list[dict],
    trends: dict,
    calendar: list[dict],
    stats: dict,
    merge_info: dict,
    overview: str = "",
) -> str:
    rcfg = cfg["run"]
    top_n = min(6, len(new_items))
    top = new_items[:top_n]

    def bucket(item: dict) -> str:
        if item.get("kind") == "release":
            return "release"
        if item.get("kind") == "news":
            return "news"
        return item["topics"][0] if item.get("topics") else "other"

    for it in new_items:
        it["_bucket"] = bucket(it)

    top_keys = {it["key"] for it in top}
    rest = [it for it in new_items if it["key"] not in top_keys]

    by_topic: dict[str, list[dict]] = {}
    releases, news, watch = [], [], []
    for it in rest:
        b = it["_bucket"]
        if b == "release":
            releases.append(it)
        elif b == "news":
            news.append(it)
        else:
            by_topic.setdefault(b, []).append(it)
        if (it.get("extra") or {}).get("author_hits"):
            watch.append(it)
    for it in top:
        if (it.get("extra") or {}).get("author_hits"):
            watch.append(it)

    topic_names = {t["id"]: t.get("name", t["id"]) for t in cfg.get("topics", [])}
    L: list[str] = []
    L.append(f"# 科研雷达 · {run_date.isoformat()}（{WEEKDAYS_ZH[run_date.weekday()]}）")
    L.append("")
    L.append(
        f"> 领域：{cfg['profile'].get('field_zh', '')}  "
        f"\n> 自动生成 {run_dt.strftime('%H:%M')} · 抓取窗口 {since_dt.strftime('%m-%d %H:%M')} → 现在 · "
        f"候选 {merge_info['unique']} → 本轮入库 {merge_info['kept']} → 今日累计 **{len(new_items)}**"
        f"（本次 +{merge_info.get('run_new', 0)}） · "
        f"来源 {'/'.join(k for k in stats if not stats[k].get('error'))}"
    )
    L.append("")

    # --- 速览 ---------------------------------------------------------------
    L.append("## 今日速览")
    L.append("")
    if not new_items:
        L.append("- 窗口内没有达到相关度阈值的新条目。可以考虑提高 `lookback_hours`，或补充主题关键词。")
    else:
        hottest = max(
            ((tid, (tr.get('week') or 0)) for tid, tr in trends.items()),
            key=lambda kv: kv[1],
            default=("", 0),
        )
        if top:
            L.append(f"- **最高相关度**：{clean(top[0]['title'], 90)}（{top[0]['score']:.1f}）")
        if hottest[1]:
            L.append(f"- **本周条目最多**：{topic_names.get(hottest[0], hottest[0])}（{hottest[1]} 篇）")
        has_history = any(tr.get("span_days", 0) >= 7 for tr in trends.values())
        rising = [
            tid for tid, tr in trends.items()
            if has_history and tr.get("ratio", 0) >= 1.5 and tr.get("week", 0) >= 2
        ]
        if rising:
            L.append("- **升温主题**：" + "、".join(topic_names.get(t, t) for t in rising))
        cnt = {}
        for it in new_items:
            cnt[it["_bucket"]] = cnt.get(it["_bucket"], 0) + 1
        parts = [f"{topic_names.get(k, k)} {v}" for k, v in sorted(cnt.items(), key=lambda kv: -kv[1])
                 if k not in ("release", "news")]
        if releases:
            parts.append(f"工具发布 {len(releases)}")
        if news:
            parts.append(f"新闻 {len(news)}")
        L.append("- **构成**：" + " · ".join(parts))
    L.append("")

    # --- 今日点评（LLM，可选）------------------------------------------------
    if overview:
        L.append("## 今日点评")
        L.append("")
        L.append(f"> {overview}")
        L.append("")

    # --- 最值得看 -----------------------------------------------------------
    L.append("## 今日最值得看")
    L.append("")
    if top:
        for i, it in enumerate(top, 1):
            lines = _fmt_item(it, max_abs=int(rcfg.get("max_abstract_chars", 320)))
            lines = lines.replace("- **", f"{i}. **", 1)
            lines = lines.replace("\n  ", "\n   ")
            L.append(lines)
            L.append("")
    else:
        L.append("_（今日无）_")
        L.append("")

    # --- 分主题 -------------------------------------------------------------
    L.append("## 按主题展开")
    L.append("")
    any_topic = False
    for topic in cfg.get("topics", []):
        tid = topic["id"]
        items = by_topic.get(tid) or []
        if not items:
            continue
        any_topic = True
        tr = trends.get(tid)
        head = f"### {topic.get('name', tid)}{_trend_label(tr)}"
        L.append(head)
        L.append("")
        for it in items[: int(rcfg.get("per_topic", 6))]:
            L.append(_fmt_item(it, max_abs=200))
            L.append("")
    if not any_topic:
        L.append("_（今日无）_")
        L.append("")

    # --- 工具发布 -----------------------------------------------------------
    L.append("## 工具与模型发布")
    L.append("")
    if releases:
        for it in releases[:8]:
            L.append(_fmt_compact(it))
    else:
        L.append("_（窗口内没有关注工具的版本发布）_")
    L.append("")

    # --- 新闻 ---------------------------------------------------------------
    L.append("## 领域新闻")
    L.append("")
    if news:
        for it in news[:8]:
            L.append(_fmt_compact(it))
    else:
        L.append("_（窗口内没有命中关注主题的新闻）_")
    L.append("")

    # --- 课题组 -------------------------------------------------------------
    if watch:
        L.append("## 关注课题组的新作")
        L.append("")
        seen = set()
        for it in watch[:8]:
            if it["key"] in seen:
                continue
            seen.add(it["key"])
            who = ", ".join((it.get("extra") or {}).get("author_hits") or [])
            L.append(_fmt_compact(it) + f"（{who}）")
        L.append("")

    # --- 会议 ---------------------------------------------------------------
    if calendar:
        L.append("## 会议与活动（未来 120 天，日期以官网为准）")
        L.append("")
        for ev in calendar[:8]:
            L.append(
                f"- **{ev['next'].strftime('%m-%d')}**（{ev['in_days']} 天后）"
                f"[{ev['name']}]({ev.get('url', '')}) — {ev.get('note', '')}"
            )
        L.append("")

    # --- 健康 ---------------------------------------------------------------
    L.append("## 运行健康")
    L.append("")
    L.append("| 数据源 | 抓取 | 状态 |")
    L.append("| --- | --- | --- |")
    for name, st in stats.items():
        status = "ok" if not st.get("error") else st["error"][:70]
        L.append(f"| {name} | {st.get('fetched', 0)} | {status} |")
    L.append("")
    L.append(
        f"> 原始 {merge_info['raw']} → 去重 {merge_info['unique']} → 剔除标题噪声 {merge_info['excluded']} "
        f"→ 低相关度 {merge_info['low_score']} → 入库 {merge_info['kept']}。"
    )
    L.append("")
    L.append(
        "<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · "
        "重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>"
    )
    L.append("")
    return "\n".join(L)


def write_index(cfg: dict, daily_dir: Path) -> None:
    files = sorted(daily_dir.glob("*.md"), reverse=True)
    lines = ["# 科研雷达 · 历史日报", ""]
    for i, f in enumerate(files):
        if f.name == "index.md":
            continue
        if i > 120:
            break
        lines.append(f"- [{f.stem}]({f.name})")
    (daily_dir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
