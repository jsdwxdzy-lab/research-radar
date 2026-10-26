"""GitHub releases: new versions of the tools this field runs on."""
from __future__ import annotations

import os
from datetime import date

from ..http import fetch_json
from ..util import clean, parse_date

API = "https://api.github.com/repos/{repo}/releases"


def fetch(cfg: dict, since: date, log=print) -> list[dict]:
    out: list[dict] = []
    ttl = int(cfg.get("cache_ttl", 3600 * 2))
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for repo in cfg.get("repos", []):
        url = API.format(repo=repo) + "?per_page=3"
        try:
            releases = fetch_json(url, ttl=ttl, headers=headers, min_interval=0.7)
        except Exception as exc:
            log(f"  ! github {repo}: {exc}")
            continue
        kept = 0
        for rel in releases or []:
            published = parse_date(rel.get("published_at"))
            if published is None or published < since:
                continue
            tag = rel.get("tag_name") or rel.get("name") or ""
            body = clean(rel.get("body", ""), 900)
            out.append(
                {
                    "source": "github",
                    "source_id": f"{repo}@{tag}",
                    "kind": "release",
                    "title": f"{repo} · {tag}",
                    "abstract": body,
                    "authors": "",
                    "venue": "GitHub",
                    "url": rel.get("html_url", f"https://github.com/{repo}"),
                    "published": published,
                    "doi": "",
                    "arxiv_id": "",
                    "extra": {"repo": repo, "tag": tag, "prerelease": rel.get("prerelease", False)},
                }
            )
            kept += 1
        log(f"  · github {repo}: {kept}")
    return out
