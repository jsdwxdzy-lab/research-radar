"""Tencent's dedicated translation model, with all inference on the local CPU."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent.parent
MODEL_ID = "tencent/HY-MT1.5-1.8B-GGUF:Q4_K_M"
MODEL_URL = "https://huggingface.co/tencent/HY-MT1.5-1.8B-GGUF/resolve/main/HY-MT1.5-1.8B-Q4_K_M.gguf"
MODEL_SHA256 = "4383ac0c3c8e476de98ff979c2a3f069f8c4fb385e7860cf2d28da896cc477c7"
GLOSSARY = """参考下面的科研术语翻译（仅在原文出现时使用）：
crystal structure prediction 翻译成 晶体结构预测
molecular crystal 翻译成 分子晶体
flow matching 翻译成 流匹配
optimal transport 翻译成 最优传输
Prussian blue analogue 翻译成 普鲁士蓝类似物
antiperovskite 翻译成 反钙钛矿
phenazine 翻译成 吩嗪
Jahn-Teller effect 翻译成 Jahn–Teller 效应

"""


def model_path() -> Path:
    root = Path(os.environ.get("RADAR_TRANSLATION_CACHE") or
                Path.home() / ".cache" / "research-radar" / "translation").expanduser().resolve()
    if root == ROOT or ROOT in root.parents:
        raise ValueError("翻译模型缓存必须放在项目目录外")
    return root / ("hymt-1.8b-q4-" + MODEL_SHA256[:16]) / "model.gguf"


def prepare(cfg: dict, log=print) -> None:
    target = model_path()
    marker = target.with_suffix('.verified.json')
    if target.is_file() and marker.is_file():
        record = json.loads(marker.read_text())
        if record.get('sha256') == MODEL_SHA256 and record.get('bytes') == target.stat().st_size:
            log('离线翻译模型：使用校验过的已有缓存')
            return
    target.parent.mkdir(parents=True, exist_ok=True)
    download = target.parent / (uuid.uuid4().hex + '.download')
    request = urllib.request.Request(MODEL_URL, headers={'User-Agent': 'research-radar-model-setup'})
    digest = hashlib.sha256()
    log('离线翻译模型：下载作者公开权重（约 1.13 GB，不需要密钥）')
    with urllib.request.urlopen(request, timeout=120) as response, download.open('wb') as out:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
            out.write(block)
    if digest.hexdigest() != MODEL_SHA256:
        raise ValueError('离线翻译权重校验失败')
    # Existing interrupted downloads remain available for inspection.
    download.replace(target)
    marker.write_text(json.dumps({'sha256': MODEL_SHA256, 'bytes': target.stat().st_size}), encoding='utf-8')
    log('离线翻译模型：权重校验完成')


class Translator:
    def __init__(self, cfg: dict):
        from llama_cpp import Llama
        target = model_path()
        if not target.is_file() or not target.with_suffix('.verified.json').is_file():
            raise ValueError('请先准备离线翻译模型')
        self.engine = Llama(model_path=str(target), n_ctx=8192,
            n_threads=int(cfg.get('threads', 4)), n_threads_batch=int(cfg.get('threads', 4)),
            n_gpu_layers=0, n_batch=512, verbose=False)
        self.max_tokens = int(cfg.get('max_source_tokens', 1024))
        self.source = self
        self.model_id = MODEL_ID

    def encode(self, text: str, **kwargs) -> list[int]:
        return self.engine.tokenize(text.encode('utf-8'), add_bos=False, special=False)

    def chunks(self, text: str) -> list[str]:
        from .offline_translate import split_text
        pieces = split_text(text, self.encode, self.max_tokens)
        packed = []
        for piece in pieces:
            if packed and len(self.encode(packed[-1] + ' ' + piece)) <= self.max_tokens:
                packed[-1] += ' ' + piece
            else:
                packed.append(piece)
        return packed

    def translate(self, text: str) -> str:
        if not text.strip():
            return ''
        if re.search(r'[\u3400-\u9fff]', text) and not re.search(r'[A-Za-z]{3}', text):
            return text.strip()
        parts = self.chunks(text)
        translated = []
        for part in parts:
            prompt = (GLOSSARY + '将以下文本翻译为简体中文，注意只需要输出翻译后的结果，不要额外解释。'
                '完整保留原文信息，不要总结或省略；方法名、模型名保留原拼写，保留化学式与数值：\n\n' + part)
            result = self.engine.create_chat_completion(messages=[{'role': 'user', 'content': prompt}],
                max_tokens=3072, temperature=0.0, top_p=1.0, repeat_penalty=1.05)
            choice = result['choices'][0]
            if choice.get('finish_reason') != 'stop':
                raise ValueError('离线译文未完整结束，本条不缓存')
            value = (choice.get('message', {}).get('content') or '').strip()
            if not value or not re.search(r'[\u3400-\u9fff]', value):
                raise ValueError('离线模型没有生成中文译文')
            translated.append(value)
        return '\n'.join(translated)
