"""RSS / RSS-1.0 / Atom news feeds (Nature journals, ScienceDaily).

Parsing is namespace-agnostic on purpose: Nature serves RSS 1.0 (RDF), ScienceDaily
serves RSS 2.0 and some feeds serve Atom — one parser has to handle all three.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date

from ..http import fetch_text
from ..util import clean, parse_date

DATE_TAGS = {"pubdate", "date", "published", "updated", "modified", "created"}
SUMMARY_TAGS = {"description", "summary", "content", "encoded"}


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _text(el, names: set) -> str:
    for ch in list(el):
        if _local(ch.tag) in names and (ch.text or "").strip():
            return ch.text.strip()
    return ""


def _link(el) -> str:
    fallback = ""
    for ch in list(el):
        if _local(ch.tag) != "link":
            continue
        href = ch.get("href")
        if href:
            rel = (ch.get("rel") or "alternate").lower()
            if rel == "alternate":
                return href.strip()
            fallback = fallback or href.strip()
        elif (ch.text or "").strip():
            return ch.text.strip()
    return fallback


def _parse(xml: str, feed_name: str) -> list[dict]:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return []

    entries = [el for el in root.iter() if _local(el.tag) == "item"]
    if not entries:
        entries = [el for el in root.iter() if _local(el.tag) == "entry"]

    out: list[dict] = []
    for e in entries:
        title = clean(_text(e, {"title"}))
        link = _link(e)
        if not title or not link:
            continue
        published = None
        for ch in list(e):
            if _local(ch.tag) in DATE_TAGS and (ch.text or "").strip():
                published = parse_date(ch.text.strip())
                if published:
                    break
        out.append(
            {
                "source": "rss",
                "source_id": link,
                "kind": "news",
                "title": title,
                "abstract": clean(_text(e, SUMMARY_TAGS)),
                "authors": "",
                "venue": feed_name,
                "url": link,
                "published": published,
                "doi": "",
                "arxiv_id": "",
                "extra": {"feed": feed_name},
            }
        )
    return out


def fetch(cfg: dict, since: date, log=print) -> list[dict]:
    out: list[dict] = []
    ttl = int(cfg.get("cache_ttl", 3600 * 4))
    for feed in cfg.get("feeds", []):
        url, name = feed["url"], feed.get("name", feed["url"])
        try:
            xml = fetch_text(url, ttl=ttl, min_interval=0.5)
        except Exception as exc:
            log(f"  ! rss {name}: {exc}")
            continue
        items = _parse(xml, name)
        # undated items cannot be judged fresh, so they are dropped
        kept = [i for i in items if i["published"] is not None and i["published"] >= since]
        out.extend(kept)
        log(f"  · rss {name}: {len(kept)}/{len(items)}")
    return out
