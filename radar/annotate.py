"""Chinese titles, abstracts, and short reviews via a second OpenAI-compatible endpoint.

The key stays outside the repo (env USTC_LLM_KEY or .secrets/ustc_llm_key).
Results are cached in SQLite so a daily run only calls the model for new items.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from . import agent, store

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "review.json"

PROMPT = """你是科研阅读助手。对下面每一条文献按输入顺序各输出一块，块与块之间只放一行 === 。
每块三行，以 TITLE:、ABS:、REV: 开头。不要使用英文双引号，引用词语时用「」。

TITLE: 中文标题。方法名、模型名可保留英文。
ABS: 中文摘要，尽量忠实翻译，不要缩成一句话。没有摘要就写（无）。
REV: 80–140 字短评。写出方法或对象、它实际做了什么、和「有机分子晶体 / 生成模型 / 视觉生成 / 相关数学」哪一类更近。不要编造未出现的数字或结论。关系弱就直说。

文献：
{material}
"""


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"enabled": False}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"enabled": False}


def api_key(cfg: dict) -> str:
    value = (os.environ.get(cfg.get("api_key_env", "USTC_LLM_KEY"), "") or "").strip()
    if value:
        return value
    candidates = [
        ROOT.parent / ".secrets" / "ustc_llm_key",
        Path.home() / ".config" / "research-radar" / "ustc_llm_key",
    ]
    for path in candidates:
        try:
            if path.exists():
                return path.read_text(encoding="utf-8").strip()
        except OSError:
            continue
    return ""


def _material(items: list[dict], max_chars: int) -> str:
    blocks = []
    for i, it in enumerate(items, 1):
        abstract = (it.get("abstract") or "").strip()
        if len(abstract) > max_chars:
            abstract = abstract[:max_chars] + "…"
        blocks.append(
            f"{i}. 标题：{it.get('title', '')}\n"
            f"   期刊：{it.get('venue') or '—'}｜作者：{(it.get('authors') or '')[:180]}\n"
            f"   摘要：{abstract or '（无摘要）'}"
        )
    return "\n".join(blocks)


def _fields(block: str) -> dict:
    current = None
    buf = {"TITLE": [], "ABS": [], "REV": []}
    for line in block.splitlines():
        jumped = False
        for name in ("TITLE", "ABS", "REV"):
            if line.startswith(name + ":"):
                current = name
                buf[name].append(line[len(name) + 1 :].strip())
                jumped = True
                break
        if not jumped and current and line.strip():
            buf[current].append(line.strip())
    return {k: " ".join(v).strip() for k, v in buf.items()}


def _one_batch(cfg: dict, items: list[dict]) -> list[dict]:
    prompt = PROMPT.format(material=_material(items, int(cfg.get("abstract_chars", 700))))
    result = agent.chat(
        cfg,
        [
            {"role": "system", "content": "按要求的 TITLE/ABS/REV 格式输出，不要 JSON，不要英文双引号。"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=int(cfg.get("max_tokens", 3500)),
        temperature=float(cfg.get("temperature", 0.2)),
    )
    text = (result.get("text") or "").strip()
    blocks = [b.strip() for b in text.split("===") if b.strip()]
    if len(blocks) < len(items):
        blocks = [b.strip() for b in text.split("\n\n") if "TITLE:" in b]
    out = []
    for src, block in zip(items, blocks):
        fields = _fields(block)
        title = fields["TITLE"][:300]
        abstract = fields["ABS"][:1200]
        if abstract in {"（无）", "(无)", "无"}:
            abstract = ""
        review = fields["REV"][:400]
        out.append({"key": src["key"], "title_zh": title, "abstract_zh": abstract, "review": review})
    if len(out) != len(items):
        raise ValueError(f"返回 {len(out)} 块，输入 {len(items)} 条")
    if not any(row["title_zh"] or row["review"] for row in out):
        raise ValueError("翻译和短评都是空的")
    return out


def run(cfg_main: dict, conn, log=print, limit: int | None = None) -> int:
    cfg = load_config()
    cfg["api_key"] = api_key(cfg)
    if not cfg.get("enabled"):
        return 0
    if not cfg["api_key"]:
        log("  · 短评/翻译：没有 USTC_LLM_KEY，跳过")
        return 0
    if not cfg.get("base_url"):
        return 0
    # agent.chat reads the key through agent.api_key(); give it this key via env for the call
    os.environ[cfg.get("api_key_env", "USTC_LLM_KEY")] = cfg["api_key"]
    cap = limit if limit is not None else int(cfg.get("max_per_run", 12))
    pending = store.pending_annotations(conn, cap)
    if not pending:
        log("  · 短评/翻译：没有新条目")
        return 0
    batch_size = max(1, int(cfg.get("batch_size", 2)))
    done = 0
    model = cfg.get("model", "")
    for start in range(0, len(pending), batch_size):
        batch = pending[start : start + batch_size]
        try:
            rows = _one_batch(cfg, batch)
        except Exception as exc:
            log(f"  ! 短评批次失败（{len(batch)} 条）：{exc}")
            if len(batch) == 1:
                continue
            for it in batch:
                try:
                    rows = _one_batch(cfg, [it])
                    store.save_annotations(conn, rows, model)
                    done += len(rows)
                except Exception as exc2:
                    log(f"  ! 单条失败：{exc2}")
            continue
        store.save_annotations(conn, rows, model)
        done += len(rows)
        log(f"  · 短评/翻译：{done}/{len(pending)}")
    return done
