"""OpenAlex full-text-ish topical search (works + preprints + conference papers)."""
from __future__ import annotations

import urllib.parse
from datetime import date

from ..http import fetch_json
from ..util import clean, parse_date

API = "https://api.openalex.org/works"
SELECT = (
    "id,doi,display_name,publication_date,type,primary_location,authorships,"
    "abstract_inverted_index,cited_by_count,is_retracted"
)


def _abstract(inverted: dict | None) -> str:
    if not inverted:
        return ""
    positions: list[tuple[int, str]] = []
    for word, idxs in inverted.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return clean(" ".join(w for _, w in positions))


def fetch(cfg: dict, since: date, log=print) -> list[dict]:
    out: list[dict] = []
    per_page = int(cfg.get("per_page", 25))
    ttl = int(cfg.get("cache_ttl", 3600 * 8))
    api_key = (cfg.get("api_key") or "").strip()
    for query in cfg.get("queries", []):
        filters = [
            f"title_and_abstract.search:{query}",
            f"from_publication_date:{since.isoformat()}",
            "is_retracted:false",
        ]
        params = {
            "filter": ",".join(filters),
            "per_page": per_page,
            "sort": "publication_date:desc",
            "select": SELECT,
        }
        if api_key:
            params["api_key"] = api_key
        else:
            params["mailto"] = cfg.get("mailto", "research-radar@example.com")
        url = API + "?" + urllib.parse.urlencode(params)
        try:
            data = fetch_json(url, ttl=ttl, min_interval=0.35)
        except Exception as exc:
            log(f"  ! openalex '{query[:40]}': {exc}")
            continue
        kept = 0
        for row in data.get("results") or []:
            title = clean(row.get("display_name", ""))
            if not title:
                continue
            loc = row.get("primary_location") or {}
            src = (loc.get("source") or {}) if isinstance(loc, dict) else {}
            venue = clean(src.get("display_name", "") or "")
            doi = row.get("doi") or ""
            authors = []
            corresponding = []
            for person in (row.get("authorships") or [])[:12]:
                name = clean((person.get("author") or {}).get("display_name", ""), 60)
                if not name:
                    continue
                authors.append(name)
                if person.get("is_corresponding"):
                    corresponding.append(name)
            kind = "paper"
            if row.get("type") in ("preprint", "posted-content"):
                kind = "preprint"
            out.append(
                {
                    "source": "openalex",
                    "source_id": row.get("id", ""),
                    "kind": kind,
                    "title": title,
                    "abstract": _abstract(row.get("abstract_inverted_index")),
                    "authors": "; ".join(a for a in authors if a),
                    "venue": venue,
                    "url": loc.get("landing_page_url") or doi or row.get("id", ""),
                    "published": parse_date(row.get("publication_date")),
                    "doi": doi,
                    "arxiv_id": "",
                    "extra": {
                        "type": row.get("type", ""),
                        "query": query,
                        "corresponding": corresponding,
                    },
                }
            )
            kept += 1
        log(f"  · openalex '{query[:44]}': {kept}")
    return out
