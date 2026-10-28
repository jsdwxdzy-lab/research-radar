"""Relevance scoring: topic keywords, watched authors, venue boosts, recency."""
from __future__ import annotations

import re
from datetime import date

from .util import keyword_regex


class Matcher:
    def __init__(self, cfg: dict):
        self.topics = []
        self.config = cfg
        for topic in cfg.get("topics", []):
            kws = [
                (kw, float(w), keyword_regex(kw)) for kw, w in (topic.get("keywords") or {}).items()
            ]
            kws.sort(key=lambda t: -len(t[0]))
            groups = topic.get("require_all_groups") or []
            if not isinstance(groups, list) or any(not isinstance(g, list) or not g or
                    any(not isinstance(term, str) or not term.strip() for term in g) for g in groups):
                raise ValueError("require_all_groups 必须是非空关键词组的列表")
            self.topics.append(
                {
                    "id": topic["id"],
                    "name": topic.get("name", topic["id"]),
                    "weight": float(topic.get("weight", 1.0)),
                    "min_hits": int(topic.get("min_hits", 1)),
                    "require_any": [
                        keyword_regex(r) for r in (topic.get("require_any") or [])
                    ],
                    "require_all_groups": [[keyword_regex(term) for term in group] for group in groups],
                    "keywords": kws,
                }
            )
        self.excludes = [keyword_regex(p) for p in cfg.get("exclude_patterns", [])]
        # these are phrases, not tokens: plain substring matching is what we want
        self.venue_blocks = [
            re.compile(re.escape(p), re.IGNORECASE) for p in cfg.get("venue_block_patterns", [])
        ]
        self.negatives = [
            re.compile(re.escape(p), re.IGNORECASE) for p in cfg.get("negative_patterns", [])
        ]
        self.authors = []
        for name in cfg.get("watch_authors", []):
            parts = [p for p in re.split(r"\s+", name.strip()) if p]
            if len(parts) < 2:
                continue
            surname = re.escape(parts[-1])
            initial = re.escape(parts[0][0])
            # "Graeme M. Day" / "Day, G. M." / "G. Day" all match
            rx = re.compile(
                rf"(?<![A-Za-z]){surname}(?![A-Za-z])|(?<![A-Za-z]){surname},?\s+{initial}",
                re.IGNORECASE,
            )
            self.authors.append((name, rx))
        self.venues = [
            (v.lower(), float(b)) for v, b in (cfg.get("venue_boosts") or {}).items()
        ]
        self.source_weights = {
            name: float((scfg or {}).get("weight", 1.0))
            for name, scfg in (cfg.get("sources") or {}).items()
        }

    def excluded(self, item: dict) -> bool:
        title = item.get("title", "") or ""
        venue = item.get("venue", "") or ""
        abstract = item.get("abstract", "") or ""
        return (
            any(rx.search(title) for rx in self.excludes)
            or any(rx.search(venue) for rx in self.venue_blocks)
            or any(rx.search(title) or rx.search(abstract) for rx in self.negatives)
        )

    def score(self, item: dict, run_date: date) -> dict:
        title = item.get("title", "") or ""
        text = title + " . " + (item.get("abstract", "") or "")
        hits_by_topic: dict[str, list[tuple[str, float, bool]]] = {}
        name_by_topic = {}
        for topic in self.topics:
            if topic["require_any"] and not any(rx.search(text) for rx in topic["require_any"]):
                continue
            if any(not any(rx.search(text) for rx in group) for group in topic["require_all_groups"]):
                continue
            hits = []
            for kw, weight, rx in topic["keywords"]:
                if rx.search(text):
                    in_title = bool(rx.search(title))
                    hits.append((kw, weight, in_title))
            if len(hits) < topic["min_hits"]:
                continue
            hits_by_topic[topic["id"]] = hits
            name_by_topic[topic["id"]] = topic["name"]

        if not hits_by_topic:
            item["score"] = 0.0
            item["topics"] = []
            item["matched"] = []
            return item

        topic_scores = {}
        for tid, hits in hits_by_topic.items():
            weight = next(t["weight"] for t in self.topics if t["id"] == tid)
            raw = sum(w for _, w, _ in hits) + 0.6 * sum(1 for _, _, in_title in hits if in_title)
            topic_scores[tid] = raw * weight

        best = max(topic_scores.values())
        # keep the leading topics only, so tags stay meaningful
        topics = [tid for tid, s in sorted(topic_scores.items(), key=lambda kv: -kv[1]) if s >= 0.55 * best]

        extra_in = dict(item.get("extra") or {})
        author_blob = (item.get("authors") or "") + " " + " ".join(extra_in.get("corresponding") or [])
        author_hits = [name for name, rx in self.authors if rx.search(author_blob)]
        venue = (item.get("venue", "") or "").lower()
        venue_boost = max([b for v, b in self.venues if v and v in venue] or [0.0])
        trust, trust_why = _trust(item, author_hits, venue_boost)

        score = best + venue_boost
        if author_hits:
            score += 3.0
        if trust == "high":
            score += 0.4
        elif trust == "low":
            score *= 0.92
        if item.get("kind") == "release":
            # a release only matters when it touches a tracked topic
            score += 2.5

        source_w = self.source_weights.get(item.get("source", ""), 1.0)
        score *= source_w

        published = item.get("published")
        if isinstance(published, date):
            age = (run_date - published).days
            if age <= 3:
                factor = 1.0
            elif age <= 7:
                factor = 0.92
            elif age <= 14:
                factor = 0.8
            elif age <= 30:
                factor = 0.65
            else:
                factor = 0.5
            if item.get("kind") == "release":
                factor = max(factor, 0.9)
            score *= factor

        item["score"] = round(score, 3)
        item["topics"] = topics
        item["matched"] = [
            {"topic": tid, "kw": kw, "w": w} for tid in topics for kw, w, _ in hits_by_topic[tid]
        ]
        item["extra"] = extra_in
        item["extra"]["author_hits"] = author_hits
        item["extra"]["venue_boost"] = venue_boost
        item["extra"]["trust"] = trust
        item["extra"]["trust_why"] = trust_why
        item["extra"]["topic_names"] = {tid: name_by_topic[tid] for tid in topics}
        return item


def _trust(item: dict, author_hits: list[str], venue_boost: float) -> tuple[str, str]:
    """High / mid / low from venue and watched authors. Country is not a signal."""
    reasons = []
    venue = (item.get("venue") or "").strip()
    kind = item.get("kind") or ""
    abstract = (item.get("abstract") or "").strip()
    low_venue = (not venue) or venue.lower().startswith("arxiv")
    if author_hits:
        reasons.append("作者：" + "、".join(author_hits[:3]))
    if venue_boost >= 0.7:
        reasons.append("期刊在重点名单")
    elif venue_boost > 0:
        reasons.append("期刊在关注名单")
    if author_hits or venue_boost >= 0.7:
        level = "high"
    elif venue_boost > 0 or (venue and not low_venue and kind != "preprint"):
        level = "mid"
        if venue and not low_venue:
            reasons.append("正式发表")
    else:
        level = "low"
        if low_venue:
            reasons.append("预印本或来源不明")
        if not author_hits:
            reasons.append("作者不在关注名单")
    if not abstract and level != "high":
        level = "low"
        reasons.append("没有摘要")
    return level, "；".join(reasons)

    def explain(self, text: str) -> list[dict]:
        item = {"title": text, "abstract": "", "authors": "", "venue": "", "source": "x"}
        self.score(item, date.today())
        per_topic = {}
        for m in item["matched"]:
            per_topic.setdefault(m["topic"], []).append(m["kw"])
        return [
            {"topic": k, "keywords": v, "score": item["score"]} for k, v in per_topic.items()
        ]


def eligible(cfg: dict, item: dict) -> bool:
    """One relevance threshold shared by ingestion and the current dashboard."""
    if not item.get("topics"):
        return False
    run = cfg.get("run") or {}
    tiers = {t["id"]: t.get("tier", "core") for t in cfg.get("topics", [])}
    core = any(tiers.get(t, "core") == "core" for t in item["topics"])
    threshold = float(run.get("min_score", 2.6))
    if item.get("kind") in ("news", "release"):
        threshold = float(run.get("min_score_news", threshold))
    if not core:
        threshold = max(threshold, float(run.get("min_score_adjacent", float(run.get("min_score", 2.6)) * 1.8)))
    return float(item.get("score") or 0) >= threshold
