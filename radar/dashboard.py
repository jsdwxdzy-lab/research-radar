"""Single-file HTML dashboard: today's board, section filters, history, reading state."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from . import render, store
from .util import now

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = Path(__file__).resolve().parent / "web" / "dashboard.html"
HUE = {
    "csp": 255,
    "crystal-gen": 300,
    "gen-model": 320,
    "vision-gen": 280,
    "gen-math": 40,
    "mlip": 190,
    "ai4s": 215,
}


def _kw(matched: list) -> list[str]:
    out = []
    for m in matched:
        kw = m.get("kw")
        if kw and kw not in out:
            out.append(kw)
    return out


def _row(r) -> dict:
    try:
        topics = json.loads(r["topics"] or "[]")
    except Exception:
        topics = []
    try:
        matched = json.loads(r["matched"] or "[]")
    except Exception:
        matched = []
    try:
        extra = json.loads(r["extra"] or "{}")
    except Exception:
        extra = {}
    authors = [a.strip() for a in (r["authors"] or "").split(";") if a.strip()]
    return {
        "k": r["key"],
        "t": r["title"],
        "a": r["abstract"] or "",
        "au": authors[:10],
        "v": r["venue"] or "",
        "u": r["url"] or "",
        "p": r["published"] or "",
        "d": (r["first_seen"] or "")[:10],
        "s": round(float(r["score"] or 0), 1),
        "tp": topics,
        "kw": _kw(matched)[:12],
        "src": [s for s in (r["sources"] or "").split(",") if s],
        "kind": r["kind"] or "paper",
        "ax": r["arxiv_id"] or "",
        "doi": r["doi"] or "",
        "who": extra.get("author_hits") or [],
        "tz": "",
        "az": "",
        "rv": "",
        "tr": extra.get("trust") or "",
        "tw": extra.get("trust_why") or "",
    }


def collect(cfg: dict, conn, days: int = 120) -> dict:
    today = now().date()
    since = (today - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT * FROM items WHERE first_seen >= ? ORDER BY first_seen DESC, score DESC",
        (since,),
    ).fetchall()
    items = [_row(r) for r in rows]

    counts: dict[str, int] = {}
    for it in items:
        counts[it["d"]] = counts.get(it["d"], 0) + 1
    day_list = [{"d": d, "n": n} for d, n in sorted(counts.items(), reverse=True)]

    # trend counts by publication day (clamped to today) so backfilled history
    # produces a real curve instead of one spike on the day we fetched it
    trend: dict[str, dict[str, int]] = {}
    tstart = (today - timedelta(days=27)).isoformat()
    today_s = today.isoformat()
    for it in items:
        day = it["p"] or it["d"]
        if day > today_s:
            day = today_s
        if day < tstart:
            continue
        for tp in it["tp"]:
            trend.setdefault(tp, {})
            trend[tp][day] = trend[tp].get(day, 0) + 1

    topics = [
        {
            "id": t["id"],
            "name": t.get("name", t["id"]),
            "short": render.SHORT.get(t["id"], t["id"]),
            "tier": t.get("tier", "core"),
            "hue": HUE.get(t["id"], 210),
        }
        for t in cfg.get("topics", [])
    ]

    events = [
        {
            "n": e["name"],
            "d": e["next"].isoformat(),
            "in": e["in_days"],
            "u": e.get("url", ""),
            "note": e.get("note", ""),
        }
        for e in render.upcoming_events(cfg, today)
    ]

    health = []
    run = None
    runs = store.recent_runs(conn, 1)
    if runs:
        run = runs[0]
        try:
            stats = json.loads(run.get("note") or "{}").get("stats", {})
        except Exception:
            stats = {}
        for name, st in stats.items():
            health.append(
                {"src": name, "n": st.get("fetched", 0), "err": (st.get("error") or "")[:120]}
            )

    notes = store.load_agent_notes(conn, today.isoformat())
    translated = store.load_annotation_map(conn)
    for it in items:
        it["why"] = notes["items"].get(it["k"], "")
        ann = translated.get(it["k"]) or {}
        it["tz"] = ann.get("title_zh") or ""
        it["az"] = ann.get("abstract_zh") or ""
        it["rv"] = ann.get("review") or ""
    overview = notes["overview"]

    return {
        "overview": overview,
        "generated": now().strftime("%Y-%m-%d %H:%M"),
        "today": today.isoformat(),
        "field": cfg.get("profile", {}).get("field_zh", ""),
        "owner": cfg.get("profile", {}).get("owner", ""),
        "topics": topics,
        "days": day_list,
        "items": items,
        "trends": trend,
        "events": events,
        "health": health,
        "run": {
            "started": (run or {}).get("started", "")[:16],
            "status": (run or {}).get("status", ""),
            "fetched": (run or {}).get("fetched", 0),
            "new": (run or {}).get("new_items", 0),
            "kept": (run or {}).get("kept", 0),
        },
    }


def build(cfg: dict, conn, out: Path | None = None, days: int = 120) -> Path:
    data = collect(cfg, conn, days=days)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/null", payload)
    target = out or (ROOT / "dashboard.html")
    target.write_text(html, encoding="utf-8")
    # GitHub Pages serves index.html at the folder root
    if target.name == "dashboard.html":
        (target.parent / "index.html").write_text(html, encoding="utf-8")
    return target
