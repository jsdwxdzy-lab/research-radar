"""Scan local Codex sessions to suggest what to track.

The pipeline's topic list was seeded from these sessions; this command keeps it
honest as interests drift. It only reads local session logs, never uploads them.
"""
from __future__ import annotations

import json
import re
import time
from collections import Counter
from pathlib import Path

from .util import keyword_regex

CODEX_DIR = Path.home() / ".codex"
STOP = set(
    """the and for with that this from have not are was were you your our their its can will
    would should could what when where which while into than then them these those there here
    about above after again against all also because been before being below between both but
    did does doing down during each few further had has having how more most other some such
    only own same so too very just now one two three use used using make made like want need
    file files code run runs make sure please thanks thank help look looks need now let see
    something anything everything good better best first second next last new old big small
    """.split()
)
NOISE = {
    "user", "users", "request", "requested", "treat", "source", "sources", "block", "blocks",
    "supplied", "ambient", "automatically", "context", "true", "false", "none", "null",
    "codex", "claude", "chatgpt", "cursor", "cloud", "python", "python3", "macos", "html", "json",
    "pdf", "ppt", "docx", "md", "png", "jpg", "github", "http", "https", "www", "com",
    "app", "apps", "desktop", "shell", "bash", "zsh", "api", "llm", "gpt", "model", "models",
    "data", "test", "tests", "paper", "papers", "work", "workflow", "agent", "agents",
}
WORD_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9\-]{3,24})\b")


def _session_files(days: int) -> list[Path]:
    cutoff = time.time() - days * 86400
    out = []
    for base in (CODEX_DIR / "sessions", CODEX_DIR / "archived_sessions"):
        if not base.exists():
            continue
        for p in base.rglob("*.jsonl"):
            try:
                if p.stat().st_mtime >= cutoff:
                    out.append(p)
            except OSError:
                continue
    return sorted(out, key=lambda p: -p.stat().st_mtime)


_BLOCK_RE = re.compile(r"<[a-zA-Z_][\w-]*(?:\s[^>]*)?>.*?</[a-zA-Z_][\w-]*>", re.S)
_TAG_RE = re.compile(r"<[^>]{1,300}>")
_HEADER_RE = re.compile(r"^(#|##)\s")


def _clean_msg(txt: str) -> str:
    """Drop the harness wrappers (app context, browser state, annotations) around a message."""
    txt = _BLOCK_RE.sub(" ", txt)
    txt = _TAG_RE.sub(" ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    if txt.startswith(("# AGENTS.md", "# Files mentioned", "# Response annotations", "The following is the Codex")):
        return ""
    return txt


def _user_texts(path: Path, max_msgs: int = 60) -> list[str]:
    texts = []
    try:
        with path.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"user"' not in line or len(texts) >= max_msgs:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                pl = d.get("payload") or {}
                if pl.get("type") != "message" or pl.get("role") != "user":
                    continue
                txt = " ".join(
                    c.get("text", "") for c in pl.get("content", []) if isinstance(c, dict)
                )
                txt = _clean_msg(txt)
                if len(txt) < 12:
                    continue
                texts.append(txt[:1200])
    except OSError:
        return []
    return texts


def scan(cfg: dict, days: int = 45, limit: int = 30) -> dict:
    files = _session_files(days)
    corpus: list[str] = []
    for p in files:
        corpus.extend(_user_texts(p))
    blob = "\n".join(corpus).lower()

    covered = {}
    for topic in cfg.get("topics", []):
        hits = 0
        for kw in (topic.get("keywords") or {}):
            hits += len(keyword_regex(kw).findall(blob))
        for hint in topic.get("zh_hints") or []:
            hits += blob.count(hint.lower())
        covered[topic["id"]] = hits

    known_terms = set()
    for topic in cfg.get("topics", []):
        for kw in (topic.get("keywords") or {}):
            known_terms.update(w.lower() for w in kw.split())

    counter = Counter()
    for w in WORD_RE.findall(blob):
        lw = w.lower()
        if lw in STOP or lw in NOISE or lw in known_terms or len(lw) < 4:
            continue
        counter[lw] += 1

    suggestions = [(w, c) for w, c in counter.most_common(limit * 3) if c >= 3][:limit]
    return {
        "sessions": len(files),
        "messages": len(corpus),
        "covered": covered,
        "suggestions": suggestions,
        "generated": time.strftime("%Y-%m-%d %H:%M"),
    }


def render_report(result: dict) -> str:
    cfg_topics = result.get("topic_names") or {}
    lines = [
        f"扫描 Codex 会话：{result['sessions']} 个文件 / {result['messages']} 条用户消息",
        "",
        "现有主题在会话中的命中次数（越高说明越贴近你实际在做的事）：",
    ]
    for tid, n in sorted(result["covered"].items(), key=lambda kv: -kv[1]):
        lines.append(f"- {cfg_topics.get(tid, tid)}: {n}")
    lines += ["", "会话里高频、但尚未进入主题词表的术语（可考虑加进 config.json）："]
    for w, c in result["suggestions"]:
        lines.append(f"- {w}  ×{c}")
    lines += [
        "",
        "用法：把确有价值的词加进对应 topic 的 keywords，权重 1.0~3.0；",
        "加完可用 `python3 -m radar explain \"含该词的标题\"` 验证打分。",
    ]
    return "\n".join(lines)


def save(result: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
