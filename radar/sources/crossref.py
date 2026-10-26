"""Crossref journal watch: newest items per ISSN (no API key needed)."""
from __future__ import annotations

import urllib.parse
from datetime import date

from ..http import fetch_json
from ..util import clean, parse_date

API = "https://api.crossref.org/journals/{issn}/works"
SELECT = "DOI,title,author,container-title,created,published,abstract,URL,type,subject"


def _row_to_item(row: dict, journal_name: str) -> dict | None:
    title = clean((row.get("title") or [""])[0])
    if not title:
        return None
    authors = []
    for a in (row.get("author") or [])[:12]:
        name = " ".join(p for p in [a.get("given", ""), a.get("family", "")] if p).strip()
        if name:
            authors.append(name)
    published = None
    for field in ("published", "created"):
        parts = ((row.get(field) or {}).get("date-parts") or [[None]])[0]
        if parts and parts[0]:
            try:
                published = date(int(parts[0]), int(parts[1] or 1), int(parts[2] or 1))
                break
            except (ValueError, IndexError):
                continue
    venue = (row.get("container-title") or [journal_name])[0] or journal_name
    doi = row.get("DOI", "")
    return {
        "source": "crossref",
        "source_id": doi,
        "kind": "paper",
        "title": title,
        "abstract": clean(row.get("abstract", "")),
        "authors": "; ".join(authors),
        "venue": clean(venue),
        "url": row.get("URL") or (f"https://doi.org/{doi}" if doi else ""),
        "published": published,
        "doi": doi,
        "arxiv_id": "",
        "extra": {"type": row.get("type", ""), "journal": journal_name},
    }


def fetch(cfg: dict, since: date, log=print) -> list[dict]:
    out: list[dict] = []
    issns = cfg.get("issns", {})
    rows = int(cfg.get("rows_per_journal", 20))
    ttl = int(cfg.get("cache_ttl", 3600 * 6))
    for issn, name in issns.items():
        params = {
            "rows": rows,
            "filter": f"from-created-date:{since.isoformat()}",
            "select": SELECT,
            "sort": "created",
            "order": "desc",
            "mailto": cfg.get("mailto", "research-radar@example.com"),
        }
        url = API.format(issn=issn) + "?" + urllib.parse.urlencode(params)
        try:
            data = fetch_json(url, ttl=ttl, min_interval=0.4)
        except Exception as exc:
            log(f"  ! crossref {name}: {exc}")
            continue
        items = (data.get("message") or {}).get("items") or []
        kept = 0
        for row in items:
            item = _row_to_item(row, name)
            if not item:
                continue
            if item["published"] and item["published"] < since:
                continue
            out.append(item)
            kept += 1
        log(f"  · crossref {name}: {kept}")
    return out
