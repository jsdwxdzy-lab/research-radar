#!/usr/bin/env python3
"""One-shot: pull 2024–2025 papers by watch_authors into the radar board.

Usage:
  python3 -B scripts/backfill_watch_authors.py --dry-run
  python3 -B scripts/backfill_watch_authors.py
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from radar import annotate, dashboard, pipeline, store
from radar.score import Matcher, eligible
from radar.util import clean, now, parse_date

SELECT = (
    "id,doi,display_name,publication_date,type,primary_location,authorships,"
    "abstract_inverted_index,cited_by_count,is_retracted"
)
CORE_AUTHORS = {
    "Graeme M. Day",
    "David J. Wales",
    "Noa Marom",
    "Angelos Michaelides",
    "Alexandre Tkatchenko",
    "Kim E. Jelfs",
    "Claire S. Adjiman",
    "Volker L. Deringer",
    "Michele Ceriotti",
    "Gabor Csanyi",
    "Shyue Ping Ong",
    "O. Anatole von Lilienfeld",
    "Bartomeu Monserrat",
    "Erin R. Johnson",
    "Jack D. Evans",
}


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "research-radar-watch-backfill"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.loads(response.read())


def _abstract(inverted: dict | None) -> str:
    if not inverted:
        return ""
    positions: list[tuple[int, str]] = []
    for word, idxs in inverted.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return clean(" ".join(w for _, w in positions))


def resolve_author_id(name: str, mailto: str) -> str | None:
    params = urllib.parse.urlencode({"search": name, "per_page": 5, "mailto": mailto})
    data = _get("https://api.openalex.org/authors?" + params)
    target = name.lower().replace(".", "")
    best = None
    best_score = -1
    for row in data.get("results") or []:
        display = (row.get("display_name") or "").lower().replace(".", "")
        score = int(row.get("works_count") or 0)
        parts = target.split()
        if parts and parts[0] in display and parts[-1] in display:
            score += 100000
        if score > best_score:
            best_score = score
            best = row
    if not best:
        return None
    return str(best.get("id") or "").replace("https://openalex.org/", "") or None


def fetch_author_works(author_id: str, mailto: str, per_page: int) -> list[dict]:
    filt = (
        f"authorships.author.id:{author_id},"
        "from_publication_date:2024-01-01,"
        "to_publication_date:2025-12-31,"
        "is_retracted:false"
    )
    params = urllib.parse.urlencode(
        {
            "filter": filt,
            "per_page": per_page,
            "sort": "cited_by_count:desc",
            "select": SELECT,
            "mailto": mailto,
        }
    )
    data = _get("https://api.openalex.org/works?" + params)
    out: list[dict] = []
    for row in data.get("results") or []:
        title = clean(row.get("display_name", ""))
        if not title:
            continue
        loc = row.get("primary_location") or {}
        src = (loc.get("source") or {}) if isinstance(loc, dict) else {}
        venue = clean(src.get("display_name", "") or "")
        doi = (row.get("doi") or "").replace("https://doi.org/", "")
        authors = []
        for person in (row.get("authorships") or [])[:12]:
            person_name = clean((person.get("author") or {}).get("display_name", ""), 60)
            if person_name:
                authors.append(person_name)
        kind = "preprint" if row.get("type") in ("preprint", "posted-content") else "paper"
        published = parse_date(row.get("publication_date"))
        out.append(
            {
                "source": "openalex",
                "source_id": row.get("id", ""),
                "kind": kind,
                "title": title,
                "abstract": _abstract(row.get("abstract_inverted_index")),
                "authors": "; ".join(authors),
                "venue": venue,
                "url": f"https://doi.org/{doi}" if doi else (row.get("id") or ""),
                "published": published,
                "doi": doi,
                "arxiv_id": "",
                "extra": {
                    "cited_by_count": row.get("cited_by_count") or 0,
                    "openalex": row.get("id", ""),
                    "watch_backfill": True,
                },
            }
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--per-author", type=int, default=2)
    parser.add_argument("--max-total", type=int, default=24)
    args = parser.parse_args()

    cfg = pipeline.load_config()
    mailto = ((cfg.get("sources") or {}).get("openalex") or {}).get(
        "mailto", "research-radar@example.com"
    )
    core = [a for a in cfg.get("watch_authors", []) if a in CORE_AUTHORS]
    rest = [a for a in cfg.get("watch_authors", []) if a not in CORE_AUTHORS]

    matcher = Matcher(cfg)
    run_date = now().date()
    candidates: list[dict] = []

    def harvest(name: str, quota: int) -> None:
        if len(candidates) >= args.max_total:
            return
        try:
            author_id = resolve_author_id(name, mailto)
            time.sleep(0.4)
            if not author_id:
                print(f"! no OpenAlex id for {name}")
                return
            works = fetch_author_works(author_id, mailto, max(quota * 4, 8))
            time.sleep(0.4)
        except Exception as exc:
            print(f"! {name}: {exc}")
            return
        kept = 0
        for item in works:
            if kept >= quota or len(candidates) >= args.max_total:
                break
            matcher.score(item, run_date)
            if matcher.excluded(item):
                continue
            hits = (item.get("extra") or {}).get("author_hits") or []
            score = float(item.get("score") or 0)
            # Watched-author hits may keep a soft floor; others still need normal eligibility.
            if hits:
                if score < 1.5:
                    continue
            elif not eligible(cfg, item):
                continue
            item["title"] = clean(item.get("title", ""), 300)
            candidates.append(item)
            kept += 1
            print(f"  + {name}: {item.get('published')}  {item['title'][:88]}")
        print(f"· {name}: kept {kept}")

    for name in core:
        harvest(name, args.per_author)
    for name in rest:
        harvest(name, 1)

    merged = pipeline._merge(candidates)  # noqa: SLF001
    print(f"selected {len(merged)} unique papers")
    if args.dry_run or not merged:
        return 0

    conn = store.connect()
    known = store.known_keys(conn)
    fresh = [it for it in merged if it["key"] not in known]
    for it in merged:
        matcher.score(it, run_date)
    seen_at = now().isoformat(timespec="seconds")
    inserted, updated = store.upsert_items(conn, merged, seen_at)
    try:
        annotate.run(cfg, conn, log=print)
    except Exception as exc:
        print(f"! annotate: {exc}")
    out = dashboard.build(cfg, conn)
    today_n = conn.execute(
        "SELECT COUNT(*) FROM items WHERE first_seen >= ?",
        (run_date.isoformat(),),
    ).fetchone()[0]
    print(
        f"upserted insert={inserted} update={updated} new_keys={len(fresh)} "
        f"today_first_seen={today_n} -> {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
