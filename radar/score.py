"""Relevance scoring: topic keywords, watched authors, venue boosts, recency."""
from __future__ import annotations

import re
from datetime import date

from .util import keyword_regex


class Matcher:
    def __init__(self, cfg: dict):
        self.topics = []
        for topic in cfg.get("topics", []):
            kws = [
                (kw, float(w), keyword_regex(kw)) for kw, w in (topic.get("keywords") or {}).items()
            ]
            kws.sort(key=lambda t: -len(t[0]))
            self.topics.append(
                {
                    "id": topic["id"],
                    "name": topic.get("name", topic["id"]),
                    "weight": float(topic.get("weight", 1.0)),
                    "min_hits": int(topic.get("min_hits", 1)),
                    "require_any": [
                        keyword_regex(r) for r in (topic.get("require_any") or [])
                    ],
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

        author_hits = [name for name, rx in self.authors if rx.search(item.get("authors", "") or "")]
        venue = (item.get("venue", "") or "").lower()
        venue_boost = max([b for v, b in self.venues if v and v in venue] or [0.0])

        score = best + venue_boost
        if author_hits:
            score += 3.0
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
        item["extra"] = dict(item.get("extra") or {})
        item["extra"]["author_hits"] = author_hits
        item["extra"]["venue_boost"] = venue_boost
        item["extra"]["topic_names"] = {tid: name_by_topic[tid] for tid in topics}
        return item

    def explain(self, text: str) -> list[dict]:
        item = {"title": text, "abstract": "", "authors": "", "venue": "", "source": "x"}
        self.score(item, date.today())
        per_topic = {}
        for m in item["matched"]:
            per_topic.setdefault(m["topic"], []).append(m["kw"])
        return [
            {"topic": k, "keywords": v, "score": item["score"]} for k, v in per_topic.items()
        ]
