"""Offline English-to-Simplified-Chinese translation using OPUS-MT and CTranslate2.

Only ``prepare`` downloads public weights. Inference reads local files, needs no
credential, and never sends article text to a translation service.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import time
import urllib.request
import uuid
import zipfile

from . import store

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "translation.json"
MODEL_URL = "https://object.pouta.csc.fi/Tatoeba-MT-models/eng-zho/opus-2020-07-17.zip"
MODEL_ID = "Helsinki-NLP/opus-mt-en-zh:2020-07-17:int8"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"enabled": False}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def cache_path(cfg: dict) -> Path:
    base = Path(os.environ.get("RADAR_TRANSLATION_CACHE") or
                Path.home() / ".cache" / "research-radar" / "translation").expanduser().resolve()
    if base == ROOT or ROOT in base.parents:
        raise ValueError("翻译模型缓存必须放在项目目录外")
    return base / ("opus-eng-zho-v1-" + cfg["archive_sha256"][:16])


def model_paths(cfg: dict) -> tuple[Path, Path]:
    base = cache_path(cfg)
    manifest = json.loads((base / "ready.json").read_text(encoding="utf-8"))
    if manifest.get("sha256") != cfg["archive_sha256"]:
        raise ValueError("翻译模型版本不匹配")
    source = (base / manifest["directory"] / "source").resolve()
    converted = (source.parent / "ct2-int8").resolve()
    if base not in source.parents or not all(p.is_file() for p in
            (source / "source.spm", source / "target.spm", converted / "model.bin")):
        raise ValueError("翻译模型缓存不完整，请重新准备模型")
    return source, converted


def prepare(cfg: dict, log=print) -> None:
    if cfg.get('engine') == 'hymt':
        from .hymt_translate import prepare as prepare_hymt
        prepare_hymt(cfg, log=log)
        return
    try:
        model_paths(cfg)
        log("离线翻译模型：使用已有缓存")
        return
    except (OSError, ValueError, KeyError):
        pass
    # Keep interrupted attempts for inspection; never delete an existing file.
    base = cache_path(cfg)
    attempt = base / uuid.uuid4().hex
    attempt.mkdir(parents=True)
    archive = attempt / "model.zip"
    request = urllib.request.Request(MODEL_URL, headers={"User-Agent": "research-radar-model-setup"})
    digest = hashlib.sha256()
    log("离线翻译模型：下载公开权重（不需要密钥）")
    with urllib.request.urlopen(request, timeout=90) as response, archive.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            out.write(chunk)
    if digest.hexdigest() != cfg["archive_sha256"]:
        raise ValueError("翻译模型下载校验失败")
    source = attempt / "source"
    source.mkdir()
    with zipfile.ZipFile(archive) as zipped:
        for entry in zipped.infolist():
            target = (source / entry.filename).resolve()
            if source.resolve() not in target.parents:
                raise ValueError("翻译模型压缩包路径异常")
        zipped.extractall(source)
    from ctranslate2.converters import OpusMTConverter
    OpusMTConverter(str(source)).convert(str(attempt / "ct2-int8"), quantization="int8")
    manifest = {"sha256": cfg["archive_sha256"], "directory": attempt.name, "model": MODEL_ID}
    (base / "ready.json").write_text(json.dumps(manifest), encoding="utf-8")
    model_paths(cfg)
    log("离线翻译模型：准备完成")


def split_text(text: str, encode, max_tokens: int = 192) -> list[str]:
    """Split at sentence/word boundaries without discarding any source content."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    if max_tokens < 2:
        raise ValueError("max_tokens must be at least 2")
    result = []

    def add(piece):
        if len(encode(piece)) <= max_tokens:
            result.append(piece)
            return
        middle = len(piece) // 2
        positions = [m.start() for m in re.finditer(r"\s", piece)]
        cut = min(positions, key=lambda n: abs(n - middle)) if positions else middle
        if cut <= 0 or cut >= len(piece):
            raise ValueError("无法在模型限制内拆分原文")
        add(piece[:cut].strip())
        add(piece[cut:].strip())

    for sentence in re.split(r"(?<=[.!?])\s+", text):
        add(sentence)
    # A character-level check also covers exceptional long words/formulas.
    if re.sub(r"\s", "", "".join(result)) != re.sub(r"\s", "", text):
        raise ValueError("原文分段完整性检查失败")
    return result


class Translator:
    def __init__(self, cfg: dict):
        import ctranslate2
        import sentencepiece
        source, converted = model_paths(cfg)
        self.source = sentencepiece.SentencePieceProcessor(model_file=str(source / "source.spm"))
        self.target = sentencepiece.SentencePieceProcessor(model_file=str(source / "target.spm"))
        self.engine = ctranslate2.Translator(str(converted), device="cpu", compute_type="int8",
            inter_threads=1, intra_threads=int(cfg.get("threads", 4)))
        self.max_tokens = int(cfg.get("max_source_tokens", 192))
        self.cfg = cfg

    def translate(self, text: str) -> str:
        if not text.strip():
            return ""
        # Already-Chinese inputs do not need a round-trip through an English model.
        if re.search(r"[\u3400-\u9fff]", text) and not re.search(r"[A-Za-z]{3}", text):
            return text.strip()
        encode = lambda value: self.source.encode(value, out_type=str)
        parts = split_text(text, encode, self.max_tokens)
        sources = [[">>cmn_Hans<<"] + encode(part) for part in parts]
        limit = 512
        batches = self.engine.translate_batch(sources, beam_size=4, max_batch_size=16,
            max_input_length=0, max_decoding_length=limit, return_end_token=True,
            replace_unknowns=True)
        if len(batches) != len(parts):
            raise ValueError("译文段数与原文不一致")
        translated = []
        for result in batches:
            tokens = result.hypotheses[0]
            # CTranslate2 returns </s> on normal completion. Reject a token cutoff.
            if not tokens or tokens[-1] != "</s>":
                raise ValueError("译文未完整结束，本条不缓存")
            value = self.target.decode(tokens[:-1]).strip()
            if not value:
                raise ValueError("译文段落为空，本条不缓存")
            translated.append(value)
        output = "\n".join(translated)
        if not re.search(r"[\u3400-\u9fff]", output):
            raise ValueError("模型未生成中文，本条不缓存")
        return output


def run(cfg: dict, conn, log=print, limit: int | None = None) -> int:
    cap = int(limit if limit is not None else cfg.get("max_per_run", 200))
    pending = store.pending_translations(conn, cap)
    if not pending:
        log("  · 离线翻译：没有待补齐的标题或摘要，保留已有译文")
        return 0
    translator = build_translator(cfg)
    deadline = time.monotonic() + int(cfg.get("max_seconds_per_run", 900))
    done = 0
    for number, item in enumerate(pending, 1):
        if time.monotonic() >= deadline:
            log("  · 离线翻译：达到时间预算，剩余条目下次继续")
            break
        try:
            title = item.get("cached_title_zh") or translator.translate(item.get("title") or "")
            abstract = item.get("cached_abstract_zh") or translator.translate(item.get("abstract") or "")
            if not title or (item.get("abstract", "").strip() and not abstract):
                raise ValueError("译文缺失")
            store.save_translations(conn, [{"key": item["key"], "title_zh": title,
                "abstract_zh": abstract, "source_hash": store.annotation_source_hash(item)}],
                getattr(translator, 'model_id', MODEL_ID))
            done += 1
            log(f"  · 离线翻译：完成 {number}/{len(pending)}（标题和完整摘要）")
        except Exception as exc:
            log(f"  ! 离线翻译失败（{type(exc).__name__}），保留已有译文，下次重试")
    return done


def build_translator(cfg: dict):
    if cfg.get('engine') == 'hymt':
        from .hymt_translate import Translator as HYTranslator
        return HYTranslator(cfg)
    return Translator(cfg)


def main() -> int:
    parser = argparse.ArgumentParser(description="准备或核验离线翻译")
    parser.add_argument("action", choices=("prepare", "verify"))
    args = parser.parse_args()
    cfg = load_config()
    if not cfg.get("enabled"):
        raise SystemExit("离线翻译未启用")
    if args.action == "prepare":
        prepare(cfg)
        return 0
    conn = store.connect()
    pending = store.pending_translations(conn, 1000000)
    count = conn.execute("SELECT count(*) FROM items WHERE first_seen >= date('now','-120 day')").fetchone()[0]
    print(json.dumps({"translation_engine": "offline-opus-mt", "visible_items": count,
        "pending_translations": len(pending)}, ensure_ascii=False))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as out:
            out.write(f"\n- 离线翻译：{count-len(pending)}/{count} 篇标题与现有摘要已齐全\n")
    return 1 if pending else 0


if __name__ == "__main__":
    raise SystemExit(main())
