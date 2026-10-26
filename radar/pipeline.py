"""Pipeline: fetch → merge → score → persist → render."""
from __future__ import annotations

import difflib
import json
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

from . import agent, dashboard, http, render, store
from .score import Matcher
from .sources import REGISTRY
from .util import (
    canonical_key, clean, norm_doi, norm_title, now, parse_date,
    strip_abstract_label, tidy_venue,
)

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "config.json"


def load_config(path: Path | None = None) -> dict:
    p = path or CONFIG_PATH
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _absorb(cur: dict, it: dict) -> None:
    """Fold a duplicate record `it` into `cur`, keeping the richest fields."""
    cur["sources_seen"] = sorted(set(cur.get("sources_seen", []) + [it.get("source", "")]))
    if len(it.get("abstract") or "") > len(cur.get("abstract") or ""):
        cur["abstract"] = it["abstract"]
    if (cur.get("venue", "").startswith("arXiv")) and not it.get("venue", "").startswith("arXiv"):
        cur["venue"] = it["venue"]
        cur["url"] = it["url"] or cur["url"]
        cur["kind"] = "paper"
    if not cur.get("authors") and it.get("authors"):
        cur["authors"] = it["authors"]
    cur_pub, it_pub = parse_date(cur.get("published")), parse_date(it.get("published"))
    if cur_pub and it_pub and it_pub < cur_pub:
        cur["published"] = it_pub
    if not cur.get("doi") and it.get("doi"):
        cur["doi"] = it["doi"]


def _merge(items: list[dict]) -> list[dict]:
    """Collapse the same work arriving from several sources into one record."""
    merged: dict[str, dict] = {}
    by_title: dict[str, str] = {}
    for it in items:
        it["doi"] = norm_doi(it.get("doi", ""))
        it["key"] = canonical_key(it)
        it["sources_seen"] = [it.get("source", "")]
        title_key = norm_title(it.get("title", ""))
        existing = merged.get(it["key"]) or (merged.get(by_title[title_key]) if len(title_key) > 25 and title_key in by_title else None)
        if existing is not None:
            _absorb(existing, it)
            continue
        merged[it["key"]] = it
        if len(title_key) > 25:
            by_title[title_key] = it["key"]

    # near-identical titles ("Toward/Towards …", preprint-vs-version) are the same work
    pool = [it for it in merged.values() if len(norm_title(it.get("title", ""))) >= 30]
    for i in range(len(pool)):
        a = pool[i]
        if a is None:
            continue
        ta = norm_title(a["title"])
        for j in range(i + 1, len(pool)):
            b = pool[j]
            if b is None or b["key"] not in merged or a["key"] not in merged:
                continue
            tb = norm_title(b["title"])
            if abs(len(ta) - len(tb)) > 8:
                continue
            if difflib.SequenceMatcher(None, ta, tb).ratio() >= 0.95:
                _absorb(a, b)
                merged.pop(b["key"], None)
                pool[j] = None

    out = []
    for it in merged.values():
        extra = dict(it.get("extra") or {})
        extra["sources_seen"] = it.get("sources_seen", [])
        it["extra"] = extra
        it["venue"] = tidy_venue(it.get("venue", ""))
        out.append(it)
    return out


def _notify(title: str, message: str) -> None:
    if sys.platform != "darwin":
        return
    try:
        script = (
            f'display notification {json.dumps(message, ensure_ascii=False)} '
            f'with title {json.dumps(title, ensure_ascii=False)}'
        )
        subprocess.run(["osascript", "-e", script], check=False, timeout=10,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def run(
    cfg: dict | None = None,
    *,
    lookback_hours: float | None = None,
    dry_run: bool = False,
    force: bool = False,
    backfill: bool = False,
    use_agent: bool = True,
    verbose: bool = True,
) -> dict:
    cfg = cfg or load_config()
    log = print if verbose else (lambda *a, **k: None)
    run_dt = now()
    run_date = run_dt.date()
    hours = lookback_hours if lookback_hours is not None else float(cfg["run"]["lookback_hours"])
    since_dt = run_dt - timedelta(hours=hours)
    since_date = since_dt.date()

    log(f"科研雷达 · {run_date.isoformat()} · 窗口自 {since_dt.strftime('%Y-%m-%d %H:%M')}")

    conn = store.connect()
    if dry_run:
        # preview only: never pollute dedupe state
        run_id = -1
        known = store.known_keys(conn)
    else:
        run_id = store.start_run(conn, run_dt.isoformat(timespec="seconds"))
        known = store.known_keys(conn)

    # ---- fetch -------------------------------------------------------------
    raw: list[dict] = []
    stats: dict[str, dict] = {}
    for name, fetcher in REGISTRY.items():
        scfg = (cfg.get("sources") or {}).get(name) or {}
        if not scfg.get("enabled", False):
            continue
        src_since = since_date
        lookback_days = int(scfg.get("lookback_days") or 0)
        if lookback_days:
            src_since = run_date - timedelta(days=lookback_days)
        if name == "openalex":
            src_since = run_date - timedelta(
                days=max(int(cfg["run"].get("openalex_lookback_days", 8)), lookback_days)
            )
        log(f"[{name}]")
        try:
            items = fetcher(scfg, src_since, log=log)
            stats[name] = {"fetched": len(items), "error": ""}
            raw.extend(items)
        except Exception as exc:  # a broken source must not kill the day
            stats[name] = {"fetched": 0, "error": f"{type(exc).__name__}: {exc}"}
            log(f"  ! {name} failed: {exc}")

    # ---- merge / score -----------------------------------------------------
    matcher = Matcher(cfg)
    items = _merge(raw)
    kept, dropped_excluded, dropped_low = [], 0, 0
    tier_of = {t["id"]: t.get("tier", "core") for t in cfg.get("topics", [])}
    thresholds = {
        "core": float(cfg["run"]["min_score"]),
        "adjacent": float(cfg["run"].get("min_score_adjacent", cfg["run"]["min_score"] * 1.8)),
    }
    min_news = float(cfg["run"].get("min_score_news", cfg["run"]["min_score"]))
    for it in items:
        if matcher.excluded(it):
            dropped_excluded += 1
            continue
        matcher.score(it, run_date)
        if it.get("kind") in ("news", "release"):
            threshold = min_news
        else:
            tier = min((tier_of.get(t, "core") for t in it["topics"]), key=lambda x: 0 if x == "core" else 1, default="core")
            threshold = thresholds.get(tier, thresholds["core"])
        if it["score"] < threshold:
            dropped_low += 1
            continue
        it["title"] = clean(it.get("title", ""), 300)
        it["abstract"] = strip_abstract_label(clean(it.get("abstract", ""), 1600))
        kept.append(it)

    kept.sort(key=lambda i: -i["score"])
    kept = kept[: int(cfg["run"].get("max_items_total", 45)) * 3]

    new_items = [it for it in kept if it["key"] not in known]
    seen_at = run_dt.isoformat(timespec="seconds")
    if backfill:
        # one-off historical pull: pretend each item was seen on its publication day
        for it in kept:
            pub = parse_date(it.get("published"))
            if pub and pub < run_date:
                it["_seen"] = f"{pub.isoformat()}T12:00:00"
    if dry_run:
        inserted, updated = 0, 0
    else:
        inserted, updated = store.upsert_items(conn, kept, seen_at)

    # ---- render ------------------------------------------------------------
    # a day can be rebuilt several times (manual re-runs, wake-from-sleep), so the
    # digest always shows everything first seen today rather than only this pass.
    if dry_run:
        today_items = new_items
    else:
        today_items = store.load_items(conn, run_date.isoformat() + "T00:00:00")

    # ---- optional LLM pass (same set the reader sees) ----------------------
    agent_cfg = agent.load_config()
    agent_cfg.setdefault("field", cfg.get("profile", {}).get("field_zh", ""))
    overview = ""
    if use_agent and agent.enabled(agent_cfg):
        try:
            got = agent.enrich(agent_cfg, conn, today_items or kept, run_date, log=log)
            overview = got.get("overview", "")
        except Exception as exc:
            log(f"  ! agent 失败（不影响日报）: {exc}")
    elif use_agent:
        log("  · agent 未配置或未启用，跳过点评")

    trends = render.topic_trends(conn, run_date, cfg)
    calendar = render.upcoming_events(cfg, run_date)
    text = render.digest(
        cfg=cfg,
        run_date=run_date,
        run_dt=run_dt,
        since_dt=since_dt,
        new_items=today_items,
        db_items=store.load_items(conn, (run_date - timedelta(days=30)).isoformat()),
        trends=trends,
        calendar=calendar,
        stats=stats,
        overview=overview,
        merge_info={
            "raw": len(raw),
            "unique": len(items),
            "excluded": dropped_excluded,
            "low_score": dropped_low,
            "kept": len(kept),
            "inserted": inserted,
            "updated": updated,
            "run_new": len(new_items),
        },
    )

    digest_path = ""
    if not dry_run:
        daily_dir = ROOT / cfg["output"]["daily_dir"]
        daily_dir.mkdir(parents=True, exist_ok=True)
        digest_path = str(daily_dir / f"{run_date.isoformat()}.md")
        Path(digest_path).write_text(text, encoding="utf-8")
        (ROOT / cfg["output"]["latest"]).write_text(text, encoding="utf-8")
        render.write_index(cfg, daily_dir)
        try:
            board = dashboard.build(cfg, conn)
            log(f"  看板 → {board}")
        except Exception as exc:  # the board must never break the daily digest
            log(f"  ! dashboard failed: {type(exc).__name__}: {exc}")
        store.prune(conn, int(cfg["output"].get("keep_days", 400)))
        if cfg.get("notify", {}).get("macos_notification") and new_items:
            top = new_items[0]
            _notify(
                f"科研雷达 {run_date}：{len(new_items)} 条新动态",
                f"{top['title'][:60]}",
            )

    if dry_run:
        print(text)
        return {
            "run_id": -1, "date": run_date.isoformat(), "fetched": len(raw),
            "unique": len(items), "kept": len(kept), "new": len(new_items),
            "digest": "", "stats": stats,
        }

    note = {"stats": stats, "merge": {
        "raw": len(raw), "unique": len(items), "excluded": dropped_excluded,
        "low_score": dropped_low, "kept": len(kept),
    }}
    store.finish_run(
        conn, run_id,
        finished=now().isoformat(timespec="seconds"),
        status="ok",
        fetched=len(raw),
        new_items=len(new_items),
        kept=len(kept),
        digest=digest_path,
        note=note,
    )

    summary = {
        "run_id": run_id,
        "date": run_date.isoformat(),
        "fetched": len(raw),
        "unique": len(items),
        "kept": len(kept),
        "new": len(new_items),
        "digest": digest_path,
        "stats": stats,
    }
    log(f"✓ 本轮新增 {len(new_items)} 条 / 候选 {len(kept)} 条 → {digest_path}")
    return summary


def explain(text: str, cfg: dict | None = None) -> None:
    cfg = cfg or load_config()
    m = Matcher(cfg)
    item = {"title": text, "abstract": "", "authors": "", "venue": "", "source": "arxiv"}
    m.score(item, now().date())
    print(f"score = {item['score']}")
    print("topics:", ", ".join(item["topics"]) or "(none)")
    names = (item.get("extra") or {}).get("topic_names", {})
    for tid in item["topics"]:
        kws = [x["kw"] for x in item["matched"] if x["topic"] == tid]
        print(f"  [{tid}] {names.get(tid, '')} :: " + " | ".join(kws))
