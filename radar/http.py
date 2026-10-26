"""Tiny stdlib HTTP client with on-disk cache, retries and gzip handling."""
from __future__ import annotations

import gzip
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "state" / "http_cache"
UA = "research-radar/0.1 (personal research digest; contact: local user)"

_last_call: dict[str, float] = {}


def _cache_paths(url: str) -> tuple[Path, Path]:
    from .util import short_hash

    h = short_hash(url, 20)
    return CACHE_DIR / f"{h}.body", CACHE_DIR / f"{h}.meta"


def fetch(
    url: str,
    *,
    timeout: int = 30,
    retries: int = 2,
    ttl: int = 0,
    headers: dict | None = None,
    min_interval: float = 0.0,
) -> bytes:
    """GET url. ttl=0 disables the cache. Raises RuntimeError on failure."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    body_path, meta_path = _cache_paths(url)

    if ttl > 0 and body_path.exists() and meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text())
            if time.time() - meta.get("ts", 0) < ttl:
                return body_path.read_bytes()
        except Exception:
            pass

    if min_interval:
        host = urllib.parse.urlparse(url).netloc
        wait = _last_call.get(host, 0) + min_interval - time.time()
        if wait > 0:
            time.sleep(wait)
        _last_call[host] = time.time()

    hdrs = {
        "User-Agent": UA,
        "Accept": "*/*",
        "Accept-Encoding": "identity",
    }
    if headers:
        hdrs.update(headers)

    last_err = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
            if raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            if ttl > 0:
                body_path.write_bytes(raw)
                meta_path.write_text(json.dumps({"ts": time.time(), "url": url}))
            return raw
        except urllib.error.HTTPError as exc:
            last_err = f"HTTP {exc.code} {url}"
            if exc.code in (400, 401, 403, 404, 422):
                break
        except Exception as exc:  # timeouts, DNS, TLS
            last_err = f"{type(exc).__name__}: {exc} ({url})"
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(last_err or f"failed to fetch {url}")


def fetch_json(url: str, **kwargs):
    raw = fetch(url, **kwargs)
    return json.loads(raw.decode("utf-8", "replace"))


def fetch_text(url: str, **kwargs) -> str:
    raw = fetch(url, **kwargs)
    return raw.decode("utf-8", "replace")
