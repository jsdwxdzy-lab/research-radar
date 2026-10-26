"""Small helpers: dates, text normalisation, canonical ids."""
from __future__ import annotations

import hashlib
import html
import re
from datetime import date, datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo

    TZ = ZoneInfo("Asia/Shanghai")
except Exception:  # pragma: no cover - very old python
    TZ = timezone(timedelta(hours=8))

WEEKDAYS_ZH = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def now() -> datetime:
    return datetime.now(TZ)


def today() -> date:
    return now().date()


def strip_html(text: str) -> str:
    if not text:
        return ""
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return _WS_RE.sub(" ", text).strip()


def clean(text: str, limit: int | None = None) -> str:
    text = strip_html(text or "")
    if limit and len(text) > limit:
        cut = text[:limit]
        # keep the sentence boundary if it is close by
        dot = cut.rfind(". ")
        if dot > limit * 0.55:
            cut = cut[: dot + 1]
        else:
            cut = cut.rstrip() + "…"
        text = cut
    return text


_ABS_LABEL_RE = re.compile(r"^\s*(abstract|summary|graphical abstract)[:：.\-\s]+", re.I)


def strip_abstract_label(text: str) -> str:
    return _ABS_LABEL_RE.sub("", text or "", count=1).strip()


def norm_title(title: str) -> str:
    t = (title or "").lower()
    t = t.replace("&", " and ")
    return _ALNUM_RE.sub("", t)


def short_hash(value: str, size: int = 14) -> str:
    return hashlib.sha1(value.encode("utf-8", "replace")).hexdigest()[:size]


def norm_doi(doi: str) -> str:
    if not doi:
        return ""
    d = doi.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    d = d.replace("doi:", "").strip()
    return d


def norm_arxiv(ident: str) -> str:
    if not ident:
        return ""
    a = ident.strip().lower()
    a = re.sub(r"^https?://arxiv\.org/(abs|pdf)/", "", a)
    a = re.sub(r"v\d+$", "", a)
    return a


def canonical_key(item: dict) -> str:
    """Stable identity across sources so the same work is not reported twice."""
    doi = norm_doi(item.get("doi", ""))
    if doi.startswith("10.48550/arxiv."):
        return "arxiv:" + norm_arxiv(doi.split("arxiv.", 1)[1])
    if doi:
        return "doi:" + doi
    ax = norm_arxiv(item.get("arxiv_id", ""))
    if ax:
        return "arxiv:" + ax
    if item.get("source") == "github":
        return "gh:" + (item.get("source_id") or norm_title(item.get("title", "")))
    return "t:" + short_hash(norm_title(item.get("title", "")))


def parse_date(value) -> date | None:
    if not value:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    s = str(value).strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    m = re.match(r"^(\d{4})/(\d{2})/(\d{2})", s)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M %z",
        "%d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
    ):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", s)
    if m:
        months = {n: i for i, n in enumerate(
            ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
        mon = months.get(m.group(2).lower()[:3])
        if mon:
            try:
                return date(int(m.group(3)), mon, int(m.group(1)))
            except ValueError:
                pass
    return None


def iso(d: date | None) -> str:
    return d.isoformat() if d else ""


def days_between(a: date, b: date) -> int:
    return (b - a).days


def keyword_regex(keyword: str) -> re.Pattern:
    """Word-ish boundary match so 'mace' does not fire inside 'grimace'."""
    parts = [re.escape(p) for p in keyword.split()]
    body = r"[\s\-]+".join(parts)
    return re.compile(r"(?<![a-z0-9])" + body + r"(?![a-z0-9])", re.IGNORECASE)


def next_occurrence(month: int, day: int, today_: date) -> date:
    year = today_.year
    try:
        candidate = date(year, month, day)
    except ValueError:
        candidate = date(year, month, 28)
    if candidate < today_:
        year += 1
        try:
            candidate = date(year, month, day)
        except ValueError:
            candidate = date(year, month, 28)
    return candidate


VENUE_MAP = {
    "arxiv (cornell university)": "arXiv",
    "arxiv.org": "arXiv",
    "hal": "HAL",
    "chemrxiv": "ChemRxiv",
    "research square": "Research Square",
}


def tidy_venue(venue: str) -> str:
    """Collapse publisher-ish venue strings into something scannable."""
    v = (venue or "").strip()
    if not v:
        return ""
    low = v.lower()
    for key, label in VENUE_MAP.items():
        if low == key:
            return label
    if low.startswith("arxiv"):
        return "arXiv"
    v = re.sub(r"\s*\((?:cornell|elsevier|wiley|springer)[^)]*\)$", "", v, flags=re.I)
    v = _WS_RE.sub(" ", v).strip(" ,;")
    return v[:80]
