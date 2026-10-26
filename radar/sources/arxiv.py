"""arXiv Atom API: newest submissions per category."""
from __future__ import annotations

import urllib.parse
import xml.etree.ElementTree as ET
from datetime import date

from ..http import fetch_text
from ..util import clean, norm_arxiv, parse_date

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}
API = "https://export.arxiv.org/api/query"


def _query(category: str, max_results: int) -> str:
    params = {
        "search_query": f"cat:{category}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    return API + "?" + urllib.parse.urlencode(params)


def fetch(cfg: dict, since: date, log=print) -> list[dict]:
    out: list[dict] = []
    cats = cfg.get("categories", [])
    n = int(cfg.get("max_results_per_category", 60))
    ttl = int(cfg.get("cache_ttl", 3600 * 3))
    for cat in cats:
        url = _query(cat, n)
        try:
            xml = fetch_text(url, ttl=ttl, min_interval=3.2)
        except Exception as exc:
            log(f"  ! arxiv {cat}: {exc}")
            continue
        try:
            root = ET.fromstring(xml)
        except ET.ParseError as exc:
            log(f"  ! arxiv {cat} parse: {exc}")
            continue
        kept = 0
        for entry in root.findall("atom:entry", NS):
            published = parse_date(entry.findtext("atom:published", default="", namespaces=NS))
            if published is None or published < since:
                continue
            raw_id = entry.findtext("atom:id", default="", namespaces=NS)
            ax = norm_arxiv(raw_id)
            title = clean(entry.findtext("atom:title", default="", namespaces=NS))
            summary = clean(entry.findtext("atom:summary", default="", namespaces=NS))
            authors = [
                clean(a.findtext("atom:name", default="", namespaces=NS), 60)
                for a in entry.findall("atom:author", NS)
            ]
            primary = entry.find("arxiv:primary_category", NS)
            category = primary.get("term") if primary is not None else cat
            out.append(
                {
                    "source": "arxiv",
                    "source_id": ax,
                    "kind": "preprint",
                    "title": title,
                    "abstract": summary,
                    "authors": "; ".join(a for a in authors if a),
                    "venue": "arXiv " + (category or cat),
                    "url": f"https://arxiv.org/abs/{ax}",
                    "published": published,
                    "doi": clean(entry.findtext("arxiv:doi", default="", namespaces=NS)),
                    "arxiv_id": ax,
                    "extra": {"category": category},
                }
            )
            kept += 1
        log(f"  · arxiv {cat}: {kept} since {since}")
    return out
