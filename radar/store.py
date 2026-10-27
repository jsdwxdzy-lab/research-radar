"""SQLite persistence: dedupe across runs, keep history for trends."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "state" / "radar.sqlite3"
ANNOTATION_VERSION = 2

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    key TEXT PRIMARY KEY,
    kind TEXT,
    source TEXT,
    sources TEXT,
    source_id TEXT,
    doi TEXT,
    arxiv_id TEXT,
    title TEXT,
    abstract TEXT,
    authors TEXT,
    venue TEXT,
    url TEXT,
    published TEXT,
    first_seen TEXT,
    last_seen TEXT,
    score REAL,
    topics TEXT,
    matched TEXT,
    extra TEXT
);
CREATE INDEX IF NOT EXISTS idx_items_first_seen ON items(first_seen);
CREATE INDEX IF NOT EXISTS idx_items_published ON items(published);

CREATE TABLE IF NOT EXISTS agent_notes (
    key TEXT PRIMARY KEY,
    day TEXT,
    kind TEXT,
    text TEXT,
    model TEXT,
    created TEXT
);
CREATE INDEX IF NOT EXISTS idx_agent_day ON agent_notes(day);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started TEXT,
    finished TEXT,
    status TEXT,
    fetched INTEGER,
    new_items INTEGER,
    kept INTEGER,
    digest TEXT,
    note TEXT
);
CREATE TABLE IF NOT EXISTS annotations (
    key TEXT PRIMARY KEY,
    title_zh TEXT,
    abstract_zh TEXT,
    review TEXT,
    model TEXT,
    created TEXT
);
CREATE TABLE IF NOT EXISTS annotation_inputs (
    key TEXT PRIMARY KEY,
    source_hash TEXT NOT NULL,
    version INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS translations (
    key TEXT PRIMARY KEY,
    title_zh TEXT NOT NULL,
    abstract_zh TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    model TEXT NOT NULL,
    created TEXT NOT NULL
);
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _merge_sources(old: str, new: str) -> str:
    parts = [p for p in (old or "").split(",") if p]
    for p in (new or "").split(","):
        if p and p not in parts:
            parts.append(p)
    return ",".join(parts)


def upsert_items(conn: sqlite3.Connection, items: list[dict], seen_at: str) -> tuple[int, int]:
    """Insert new items; refresh last_seen / score for known ones."""
    inserted = updated = 0
    for it in items:
        row = conn.execute("SELECT key, sources, score FROM items WHERE key=?", (it["key"],)).fetchone()
        seen = it.get("_seen") or seen_at
        if row is None:
            conn.execute(
                """INSERT INTO items (key, kind, source, sources, source_id, doi, arxiv_id, title,
                       abstract, authors, venue, url, published, first_seen, last_seen, score,
                       topics, matched, extra)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    it["key"], it.get("kind", ""), it.get("source", ""), it.get("source", ""),
                    it.get("source_id", ""), it.get("doi", ""), it.get("arxiv_id", ""),
                    it.get("title", ""), it.get("abstract", ""), it.get("authors", ""),
                    it.get("venue", ""), it.get("url", ""), it.get("published", ""),
                    seen, seen, float(it.get("score", 0)),
                    json.dumps(it.get("topics", []), ensure_ascii=False),
                    json.dumps(it.get("matched", []), ensure_ascii=False),
                    json.dumps(it.get("extra", {}), ensure_ascii=False),
                ),
            )
            inserted += 1
        else:
            conn.execute(
                """UPDATE items SET last_seen=?, score=MAX(score,?), sources=?,
                       url=CASE WHEN url='' THEN ? ELSE url END,
                       venue=CASE WHEN venue='' THEN ? ELSE venue END,
                       abstract=CASE WHEN length(abstract) < length(?) THEN ? ELSE abstract END
                   WHERE key=?""",
                (
                    seen_at, float(it.get("score", 0)),
                    _merge_sources(row["sources"], it.get("source", "")),
                    it.get("url", ""), it.get("venue", ""),
                    it.get("abstract", ""), it.get("abstract", ""),
                    it["key"],
                ),
            )
            updated += 1
    conn.commit()
    return inserted, updated


def load_items(conn: sqlite3.Connection, first_seen_after: str) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM items WHERE first_seen >= ? ORDER BY score DESC", (first_seen_after,)
    ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        for f in ("topics", "matched", "extra"):
            try:
                d[f] = json.loads(d[f] or "[]" if f != "extra" else d[f] or "{}")
            except Exception:
                d[f] = [] if f != "extra" else {}
        out.append(d)
    return out


def topic_counts(conn: sqlite3.Connection, since: str, until: str) -> dict:
    """How many items per topic were first seen in a window (for trend arrows)."""
    # trend windows follow publication date (falling back to when we first saw it)
    rows = conn.execute(
        "SELECT topics FROM items "
        "WHERE COALESCE(NULLIF(published,''), first_seen) >= ? "
        "  AND COALESCE(NULLIF(published,''), first_seen) < ?",
        (since, until),
    ).fetchall()
    counts: dict[str, int] = {}
    for r in rows:
        try:
            for t in json.loads(r["topics"] or "[]"):
                counts[t] = counts.get(t, 0) + 1
        except Exception:
            continue
    return counts


def known_keys(conn: sqlite3.Connection) -> set[str]:
    return {r["key"] for r in conn.execute("SELECT key FROM items").fetchall()}


def start_run(conn: sqlite3.Connection, started: str) -> int:
    cur = conn.execute("INSERT INTO runs (started, status) VALUES (?, 'running')", (started,))
    conn.commit()
    return int(cur.lastrowid)


def finish_run(conn: sqlite3.Connection, run_id: int, **fields) -> None:
    conn.execute(
        """UPDATE runs SET finished=?, status=?, fetched=?, new_items=?, kept=?, digest=?, note=?
           WHERE id=?""",
        (
            fields.get("finished"), fields.get("status", "ok"), fields.get("fetched", 0),
            fields.get("new_items", 0), fields.get("kept", 0), fields.get("digest", ""),
            json.dumps(fields.get("note", {}), ensure_ascii=False), run_id,
        ),
    )
    conn.commit()


def recent_runs(conn: sqlite3.Connection, limit: int = 10) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,))]


def annotation_source_hash(item: dict) -> str:
    fields = [item.get(name) or "" for name in ("title", "abstract", "authors", "venue")]
    return hashlib.sha256(json.dumps(fields, ensure_ascii=False).encode("utf-8")).hexdigest()


def pending_annotations(conn: sqlite3.Connection, limit: int) -> list[dict]:
    if int(limit) <= 0:
        return []
    rows = conn.execute(
        """SELECT i.*, a.title_zh AS cached_title, a.abstract_zh AS cached_abstract,
                  a.review AS cached_review, m.source_hash AS cached_hash,
                  m.version AS cached_version
           FROM items i
           LEFT JOIN annotations a ON a.key=i.key
           LEFT JOIN annotation_inputs m ON m.key=i.key
           WHERE i.first_seen >= date('now','-120 day')
           ORDER BY (a.key IS NOT NULL), i.first_seen DESC, i.score DESC"""
    )
    pending = []
    for row in rows:
        item = dict(row)
        cached = {name: item.pop("cached_" + name) for name in
                  ("title", "abstract", "review", "hash", "version")}
        complete = (bool((cached["title"] or "").strip())
                    and bool((cached["review"] or "").strip())
                    and (not (item.get("abstract") or "").strip()
                         or bool((cached["abstract"] or "").strip())))
        if (not complete or cached["version"] != ANNOTATION_VERSION
                or cached["hash"] != annotation_source_hash(item)):
            pending.append(item)
            if len(pending) >= int(limit):
                break
    return pending


def save_annotations(conn: sqlite3.Connection, rows: list[dict], model: str) -> None:
    from .util import now as _now

    created = _now().isoformat(timespec="seconds")
    with conn:
        conn.executemany(
            """INSERT INTO annotations (key, title_zh, abstract_zh, review, model, created)
               VALUES (?,?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET
               title_zh=excluded.title_zh, abstract_zh=excluded.abstract_zh,
               review=excluded.review, model=excluded.model, created=excluded.created""",
            [(r["key"], r.get("title_zh", ""), r.get("abstract_zh", ""),
              r.get("review", ""), model, created) for r in rows],
        )
        conn.executemany(
            """INSERT INTO annotation_inputs (key, source_hash, version) VALUES (?,?,?)
               ON CONFLICT(key) DO UPDATE SET source_hash=excluded.source_hash,
               version=excluded.version""",
            [(r["key"], r["source_hash"], ANNOTATION_VERSION)
             for r in rows if r.get("source_hash")],
        )


def load_annotation_map(conn: sqlite3.Connection) -> dict:
    try:
        rows = conn.execute("SELECT key, title_zh, abstract_zh, review FROM annotations").fetchall()
    except sqlite3.OperationalError:
        return {}
    result = {
        r["key"]: {
            "title_zh": r["title_zh"] or "",
            "abstract_zh": r["abstract_zh"] or "",
            "review": r["review"] or "",
        }
        for r in rows
    }
    try:
        offline = conn.execute("SELECT * FROM translations").fetchall()
        legacy = {r['key']: dict(r) for r in conn.execute(
            "SELECT a.key, a.title_zh, a.abstract_zh, m.source_hash, m.version "
            "FROM annotations a LEFT JOIN annotation_inputs m ON m.key=a.key")}
        items = {r['key']: dict(r) for r in conn.execute("SELECT * FROM items")}
    except sqlite3.OperationalError:
        return result
    for row in offline:
        item = items.get(row['key'])
        if item is None:
            continue
        old = legacy.get(row['key']) or {}
        fresh_legacy = (old.get('version') == ANNOTATION_VERSION
                        and old.get('source_hash') == annotation_source_hash(item))
        ann = result.setdefault(row['key'], {'title_zh': '', 'abstract_zh': '', 'review': ''})
        # Fresh Qwen/manual-reviewed text wins. Offline text never supplies a review.
        for name in ('title_zh', 'abstract_zh'):
            if row[name] and not (fresh_legacy and old.get(name)):
                ann[name] = row[name]
    return result


def pending_translations(conn: sqlite3.Connection, limit: int) -> list[dict]:
    """Missing/stale translations, independent of whether a review exists."""
    if int(limit) <= 0:
        return []
    rows = conn.execute(
        """SELECT i.*, a.title_zh AS legacy_title, a.abstract_zh AS legacy_abstract,
                  m.source_hash AS legacy_hash, m.version AS legacy_version,
                  t.title_zh AS offline_title, t.abstract_zh AS offline_abstract,
                  t.source_hash AS offline_hash
           FROM items i
           LEFT JOIN annotations a ON a.key=i.key
           LEFT JOIN annotation_inputs m ON m.key=i.key
           LEFT JOIN translations t ON t.key=i.key
           WHERE i.first_seen >= date('now','-120 day')
           ORDER BY (a.key IS NOT NULL OR t.key IS NOT NULL), i.first_seen DESC, i.score DESC""")
    pending = []
    for row in rows:
        item = dict(row)
        cached = {name: item.pop(name) for name in ('legacy_title', 'legacy_abstract',
            'legacy_hash', 'legacy_version', 'offline_title', 'offline_abstract', 'offline_hash')}
        digest = annotation_source_hash(item)
        legacy_fresh = (cached['legacy_hash'] == digest
                        and cached['legacy_version'] == ANNOTATION_VERSION)
        offline_fresh = cached['offline_hash'] == digest
        title = (cached['legacy_title'] if legacy_fresh else '') or (cached['offline_title'] if offline_fresh else '')
        abstract = (cached['legacy_abstract'] if legacy_fresh else '') or (cached['offline_abstract'] if offline_fresh else '')
        if (title or '').strip() and (not (item.get('abstract') or '').strip() or (abstract or '').strip()):
            continue
        item['cached_title_zh'] = title or ''
        item['cached_abstract_zh'] = abstract or ''
        pending.append(item)
        if len(pending) >= int(limit):
            break
    return pending


def save_translations(conn: sqlite3.Connection, rows: list[dict], model: str) -> None:
    from .util import now as _now
    created = _now().isoformat(timespec='seconds')
    with conn:
        conn.executemany(
            """INSERT INTO translations (key, title_zh, abstract_zh, source_hash, model, created)
               VALUES (?,?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET
               title_zh=excluded.title_zh, abstract_zh=excluded.abstract_zh,
               source_hash=excluded.source_hash, model=excluded.model, created=excluded.created""",
            [(r['key'], r['title_zh'], r['abstract_zh'], r['source_hash'], model, created) for r in rows])


def prune(conn: sqlite3.Connection, keep_days: int) -> int:
    cutoff = (datetime.now() - timedelta(days=keep_days)).date().isoformat()
    cur = conn.execute("DELETE FROM items WHERE first_seen < ?", (cutoff,))
    conn.commit()
    return cur.rowcount


def save_agent_notes(conn: sqlite3.Connection, day: str, overview: str, whys: dict, model: str) -> None:
    from .util import now as _now

    created = _now().isoformat(timespec="seconds")
    rows = [(f"overview:{day}", day, "overview", overview, model, created)]
    rows += [(k, day, "why", v, model, created) for k, v in whys.items()]
    conn.executemany(
        "INSERT OR REPLACE INTO agent_notes (key, day, kind, text, model, created) VALUES (?,?,?,?,?,?)",
        rows,
    )
    conn.commit()


def load_agent_notes(conn: sqlite3.Connection, day: str) -> dict:
    overview, items = "", {}
    try:
        rows = conn.execute("SELECT key, kind, text FROM agent_notes WHERE day = ?", (day,)).fetchall()
    except sqlite3.OperationalError:
        return {"overview": "", "items": {}}
    for r in rows:
        if r["kind"] == "overview":
            overview = r["text"]
        elif r["kind"] == "why":
            items[r["key"]] = r["text"]
    return {"overview": overview, "items": items}
