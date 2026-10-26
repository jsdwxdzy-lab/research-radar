"""Source adapters. Each exposes fetch(cfg, since) -> list[item dict]."""
from __future__ import annotations

from . import arxiv, crossref, github, openalex, rss

REGISTRY = {
    "arxiv": arxiv.fetch,
    "crossref": crossref.fetch,
    "openalex": openalex.fetch,
    "rss": rss.fetch,
    "github": github.fetch,
}

__all__ = ["REGISTRY"]
