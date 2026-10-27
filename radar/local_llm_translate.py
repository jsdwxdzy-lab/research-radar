"""Qwen's offline translation worker, with all inference on the local CPU."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent.parent
MODEL_ID = "Qwen3-4B-Instruct-2507:Q4_K_M"
MODEL_URL = "https://huggingface.co/bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF/resolve/ae44f08e1392f39c0e474af10c3ff8355c8b6688/Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf"
MODEL_SHA256 = "2fde00ce69dd4899c70d020845e2638353015bba0fdf161b3eb965f2bca4464e"
GLOSSARY = """参考下面的科研术语翻译（仅在原文出现时使用）：
crystal structure prediction 翻译成 晶体结构预测
molecular crystal 翻译成 分子晶体
flow matching 翻译成 流匹配
optimal transport 翻译成 最优传输
Prussian blue analogue 翻译成 普鲁士蓝类似物
antiperovskite 翻译成 反钙钛矿
phenazine 翻译成 吩嗪
Jahn-Teller effect 翻译成 Jahn–Teller 效应
anthracene 翻译成 蒽
acridine 翻译成 吖啶
metastable 翻译成 亚稳态
cathode 翻译成 阴极（电池放电语境中为正极）
anode 翻译成 阳极（电池放电语境中为负极）
median 翻译成 中位数
space group 翻译成 空间群

"""


def model_path() -> Path:
    root = Path(os.environ.get("RADAR_TRANSLATION_CACHE") or
                Path.home() / ".cache" / "research-radar" / "translation").expanduser().resolve()
    if root == ROOT or ROOT in root.parents:
        raise ValueError("翻译模型缓存必须放在项目目录外")
    return root / ("qwen3-4b-instruct-q4-" + MODEL_SHA256[:16]) / "model.gguf"


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
    log('离线翻译模型：下载作者公开权重（约 2.50 GB，不需要密钥）')
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
        self.model_sha256 = MODEL_SHA256
        self.protected_terms = []

    def encode(self, text: str, **kwargs) -> list[int]:
        return self.engine.tokenize(text.encode('utf-8'), add_bos=False, special=False)

    def chunks(self, text: str) -> list[str]:
        from .offline_translate import split_text
        # One source sentence at a time avoids abstract-level summarization and
        # keeps numerical/negative statements tied to their local context.
        return split_text(text, self.encode, self.max_tokens)

    def set_context(self, title: str) -> None:
        match = re.match(r'^([A-Za-z][A-Za-z0-9._-]{1,40}):\s*(.+)$', title)
        self.protected_terms = [match.group(1)] if match else []

    def translate_title(self, title: str) -> str:
        match = re.match(r'^([A-Za-z][A-Za-z0-9._-]{1,40}):\s*(.+)$', title)
        if match:
            return match.group(1) + '：' + self.translate(match.group(2))
        return self.translate(title)

    def translate(self, text: str) -> str:
        if not text.strip():
            return ''
        if re.search(r'[\u3400-\u9fff]', text) and not re.search(r'[A-Za-z]{3}', text):
            return text.strip()
        parts = self.chunks(text)
        translated = []
        for part in parts:
            names = ''.join(name + ' 翻译成 ' + name + '\n' for name in getattr(self, 'protected_terms', []))
            prompt = (GLOSSARY + names + '将以下文本翻译为简体中文，注意只需要输出翻译后的结果，不要额外解释。'
                '完整保留原文信息，不要总结或省略；方法名、模型名保留原拼写，保留化学式与数值：\n\n' + part)
            # This Instruct checkpoint is non-thinking; use its standard ChatML template.
            formatted = ('<|im_start|>system\n你是严谨的科研英译中翻译员。只输出完整译文。<|im_end|>\n'
                '<|im_start|>user\n' + prompt + '<|im_end|>\n'
                '<|im_start|>assistant\n')
            percentages = re.findall(r'\d+(?:\.\d+)?\s*%', part)
            for attempt in range(2):
                result = self.engine.create_completion(prompt=formatted, max_tokens=3072,
                    temperature=0.0, top_p=1.0, repeat_penalty=1.05,
                    stop=['<|im_end|>', '<|endoftext|>'], echo=False)
                choice = result['choices'][0]
                if choice.get('finish_reason') != 'stop':
                    raise ValueError('离线译文未完整结束，本条不缓存')
                value = (choice.get('text') or '').strip()
                if '<think>' in value or '</think>' in value:
                    raise ValueError('模型意外输出思考内容，本条不缓存')
                if not value or not re.search(r'[\u3400-\u9fff]', value):
                    raise ValueError('离线模型没有生成中文译文')
                missing = []
                normalized = re.sub(r'\s+', '', value).replace('％', '%')
                actual_percentages = set(re.findall(r'\d+(?:\.\d+)?%', normalized))
                for token in percentages:
                    if re.sub(r'\s+', '', token) not in actual_percentages:
                        missing.append(token)
                for english, allowed in (('median', ('中位数', '中值')), ('metastable', ('亚稳态', '亚稳')),
                                         ('cathode', ('阴极', '正极')), ('anode', ('阳极', '负极')),
                                         ('space group', ('空间群',))):
                    if re.search(r'\b' + english + r's?\b', part, re.I) and not any(word in value for word in allowed):
                        missing.append('/'.join(allowed))
                if not missing:
                    break
                if attempt:
                    raise ValueError('关键科研术语或百分比未保留，本条不缓存')
                # Retry the original sentence with explicit constraints; never
                # patch a finished translation by hand or drop the failing tail.
                constraint = '翻译时必须完整保留这些数字、百分号和术语：' + '、'.join(missing) + '。\n'
                formatted = formatted.replace('<|im_start|>user\n', '<|im_start|>user\n' + constraint, 1)
            translated.append(value)
        return '\n'.join(translated)
