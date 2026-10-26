"""Optional LLM layer: one daily overview + one line per top item.

Any OpenAI-compatible endpoint works (DeepSeek, OpenAI, Kimi, Ollama, vLLM …).
Configured in config/agent.json, key comes from an env var so it never lands in
the repo. Every failure is swallowed: the digest must still be produced.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "agent.json"

SYSTEM = (
    "你是计算化学 / 材料信息学的研究助理，服务对象是研究有机分子晶体结构预测（CSP）、"
    "晶体生成模型与机器学习势的博士生。你只根据给定材料作答，不编造未出现的结论、数字或对比。"
)

PROMPT = """用户的研究方向：{field}
当前课题：化学知识驱动的有机分子晶体生成模型；关注 CSP、多晶型、能量图景、MLIP/通用势、缺陷与固溶、功能导向筛选。

下面是 {n} 条候选（按相关度排序）。请完成两件事：

1) 「总览」：120–180 字中文。说明今天最值得注意的 1–2 条是什么、它们和用户方向的关系（是竞品、可用工具、还是方法学启发），以及有没有值得追的线索。不要逐条罗列，不要空话。

2) 每条一句「为什么值得看」：30–45 字中文，具体到方法、体系或结论。如果和用户课题关系不大，就直说「关联较弱，可作为背景」。不要复述标题。

严格只输出 JSON，不要代码块、不要解释：
{{"overview": "...", "items": {{"<编号>": "..."}}}}

候选：
{material}
"""


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"enabled": False}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"enabled": False}


def _candidate_key_files(cfg: dict) -> list[Path]:
    """Key files live outside the repo so they can never be committed."""
    out: list[Path] = []
    if cfg.get("api_key_file"):
        out.append(Path(os.path.expanduser(cfg["api_key_file"])))
    out.append(ROOT.parent / ".secrets" / "agent_key")          # sibling of the project
    out.append(Path.home() / ".config" / "research-radar" / "agent_key")
    return out


def api_key(cfg: dict) -> str:
    """Env var first, then a key file outside the repo (never committed)."""
    value = (os.environ.get(cfg.get("api_key_env", "AGENT_API_KEY"), "") or "").strip()
    if value:
        return value
    for p in _candidate_key_files(cfg):
        try:
            if p.exists():
                return p.read_text(encoding="utf-8").strip()
        except OSError:
            continue
    return ""


def enabled(cfg: dict) -> bool:
    return bool(cfg.get("enabled")) and bool(api_key(cfg)) and bool(cfg.get("base_url"))


def chat(cfg: dict, messages: list[dict], max_tokens: int = 1200, temperature: float | None = None) -> dict:
    """POST /chat/completions. Returns {text, model, usage}."""
    base = (cfg.get("base_url") or "").rstrip("/")
    url = base + ("/chat/completions" if base.endswith("/v1") else "/v1/chat/completions")
    body = {
        "model": cfg.get("model", "gpt-4o-mini"),
        "messages": messages,
        "temperature": cfg.get("temperature", 0.3) if temperature is None else temperature,
        "max_tokens": max_tokens,
    }
    if cfg.get("json_mode", True):
        body["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key(cfg)}",
            "User-Agent": "research-radar/0.2",
        },
        method="POST",
    )
    timeout = int(cfg.get("timeout_seconds", 120))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"连接失败: {exc.reason}") from exc
    text = ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    return {"text": text, "model": data.get("model") or body["model"], "usage": data.get("usage") or {}}


def _parse_json(text: str) -> dict:
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.S)
    start, end = t.find("{"), t.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("模型没有返回 JSON")
    return json.loads(t[start : end + 1])


def _material(items: list[dict], max_chars: int) -> str:
    blocks = []
    for i, it in enumerate(items, 1):
        abstract = (it.get("abstract") or "").strip()
        if len(abstract) > max_chars:
            abstract = abstract[:max_chars] + "…"
        blocks.append(
            f"{i}. {it.get('title', '')}\n   期刊/来源：{it.get('venue') or '—'}｜日期：{it.get('published') or '—'}"
            f"\n   摘要：{abstract or '（无摘要）'}"
        )
    return "\n".join(blocks)


def enrich(cfg: dict, conn, items: list[dict], run_date, log=print, force: bool = False) -> dict:
    """Call the model once for the day's top items and persist the result."""
    from . import store

    day = run_date.isoformat() if hasattr(run_date, "isoformat") else str(run_date)
    cached = store.load_agent_notes(conn, day)
    if force:
        cached = {"overview": "", "items": {}}
    if cached.get("overview") and cached.get("items"):
        log("  · agent: 使用今天已生成的点评")
        return cached

    top = [it for it in items if it.get("kind") not in ("release",)][: int(cfg.get("max_items", 6))]
    if not top:
        return {"overview": "", "items": {}}

    prompt = PROMPT.format(
        field=cfg.get("field") or "计算化学 / 有机分子晶体",
        n=len(top),
        material=_material(top, int(cfg.get("max_chars", 700))),
    )
    started = time.time()
    result = chat(
        cfg,
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
        max_tokens=int(cfg.get("max_tokens", 1200)),
    )
    data = _parse_json(result["text"])
    overview = (data.get("overview") or "").strip()
    raw_items = data.get("items") or {}
    index = {str(i): it["key"] for i, it in enumerate(top, 1)}
    whys: dict[str, str] = {}
    for idx, text in raw_items.items():
        key = index.get(str(idx).strip())
        if key and isinstance(text, str) and text.strip():
            whys[key] = text.strip()[:300]

    store.save_agent_notes(conn, day, overview, whys, result.get("model", ""))
    usage = result.get("usage") or {}
    log(
        f"  · agent: {len(whys)} 条点评 · {result.get('model', '')} · "
        f"{time.time() - started:.1f}s · tokens {usage.get('total_tokens', '?')}"
    )
    return {"overview": overview, "items": whys}


def self_test(cfg: dict | None = None, log=print) -> int:
    cfg = cfg or load_config()
    if not cfg.get("enabled"):
        log("agent 未启用：把 config/agent.json 里的 enabled 改成 true")
        return 1
    if not api_key(cfg):
        log(f"没有找到 API key：请设置环境变量 {cfg.get('api_key_env', 'AGENT_API_KEY')}")
        return 1
    log(f"endpoint {cfg.get('base_url')} · model {cfg.get('model')}")
    try:
        res = chat(cfg, [{"role": "user", "content": "只回复两个字：正常"}], max_tokens=16, temperature=0)
    except Exception as exc:
        log(f"失败：{exc}")
        return 1
    log(f"成功：{res['text'].strip()[:40]!r} · model={res['model']} · usage={res.get('usage')}")
    return 0
