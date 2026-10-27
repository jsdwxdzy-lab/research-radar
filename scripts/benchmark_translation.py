"""Read-only trial using public papers; no API key, database edits or chat access."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import sqlite3
import sys
import time
from unittest.mock import patch
import urllib.request
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from radar import offline_translate as offline


def prepare_trial(output: Path):
    """Establish and report the archive digest before pinning production config."""
    archive = output.parent / 'opus-2020-07-17.zip'
    if not archive.exists():
        with urllib.request.urlopen(offline.MODEL_URL, timeout=90) as response, archive.open('wb') as out:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    cfg = {'enabled': True, 'archive_sha256': digest, 'max_source_tokens': 192, 'threads': 4,
           'max_per_run': 200, 'max_seconds_per_run': 900}
    base = offline.cache_path(cfg)
    attempt = base / uuid.uuid4().hex
    source = attempt / 'source'
    source.mkdir(parents=True)
    with zipfile.ZipFile(archive) as zipped:
        for entry in zipped.infolist():
            if source.resolve() not in (source / entry.filename).resolve().parents:
                raise ValueError('Unexpected archive path')
        zipped.extractall(source)
    from ctranslate2.converters import OpusMTConverter
    OpusMTConverter(str(source)).convert(str(attempt / 'ct2-int8'), quantization='int8')
    (base / 'ready.json').write_text(json.dumps({'sha256': digest, 'directory': attempt.name}), encoding='utf-8')
    output.write_text(json.dumps(cfg, indent=2), encoding='utf-8')
    print(json.dumps({'archive_sha256': digest, 'archive_bytes': archive.stat().st_size, 'prepared': True}), flush=True)


def benchmark(cfg: dict, output: Path, limit: int = 10, focus_title: str = ''):
    conn = sqlite3.connect('file:' + str(ROOT / 'state' / 'radar.sqlite3') + '?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    rows = [dict(row) for row in conn.execute(
        "SELECT i.*, a.abstract_zh AS qwen_abstract FROM items i LEFT JOIN annotations a ON a.key=i.key "
        "WHERE length(i.abstract)>0 ORDER BY i.score DESC")]
    if focus_title:
        rows = [row for row in rows if focus_title.casefold() in row['title'].casefold()]
    selected = []
    # Cover the longest input and the leading paper in each topic, then fill by score.
    candidates = sorted(rows, key=lambda i: -len(i['abstract']))[:2]
    for topic in ('csp', 'crystal-gen', 'gen-model', 'vision-gen', 'gen-math', 'mlip', 'ai4s'):
        candidates += next(([item] for item in rows if topic in json.loads(item.get('topics') or '[]')), [])
    candidates += rows
    for item in candidates:
        if item['key'] not in [old['key'] for old in selected]:
            selected.append(item)
        if len(selected) == limit:
            break
    if len(selected) != limit:
        raise ValueError('Not enough public papers')
    results = []
    quality = []
    started = time.monotonic()
    # Prove model construction and all inference work without network access.
    def deny(*args, **kwargs):
        raise AssertionError('Network access attempted during offline inference')
    with patch.object(socket.socket, 'connect', deny), patch.object(socket, 'create_connection', deny), \
            patch.object(urllib.request, 'urlopen', deny):
        translator = offline.build_translator(cfg)
        if cfg.get('engine') == 'qwen-offline':
            checks = [
                ('The structures are stable or metastable.', lambda s: '亚稳' in s and '不稳定' not in s),
                ('79% of the structures matched no entry in the Materials Project database.',
                    lambda s: '79%' in s and any(word in s for word in ('没有', '未', '不', '无'))),
                ('The mixed crystals contain anthracene, acridine and phenazine.',
                    lambda s: all(word in s for word in ('蒽', '吖啶', '吩嗪'))),
                ('We learn a flow from inlier text embeddings.',
                    lambda s: '异常' not in s and any(word in s for word in ('内点', '正常', '非离群', '内群'))),
                ('The median figure of merit was nine times higher.',
                    lambda s: any(word in s for word in ('中位', '中值')) and '平均' not in s),
            ]
            for source, check in checks:
                translated = translator.translate(source)
                passed = check(translated)
                quality.append({'source': source, 'translation': translated, 'passed': passed})
                print(json.dumps({'quality_check': source, 'translation': translated, 'passed': passed}, ensure_ascii=False), flush=True)
            if not all(row['passed'] for row in quality):
                output.write_text(json.dumps({'quality_checks': quality}, ensure_ascii=False, indent=2), encoding='utf-8')
                raise ValueError('Critical scientific translation checks failed')
        for item in selected:
            tick = time.monotonic()
            if hasattr(translator, 'set_context'):
                translator.set_context(item['title'])
            title_fn = getattr(translator, 'translate_title', translator.translate)
            title = title_fn(item['title'])
            try:
                abstract = translator.translate(item['abstract'])
            except ValueError:
                issue = getattr(translator, 'last_validation_issue', None)
                if issue:
                    print(json.dumps({'validation_issue': issue}, ensure_ascii=False), flush=True)
                    output.write_text(json.dumps({'validation_issue': issue, 'completed_results': results},
                        ensure_ascii=False, indent=2), encoding='utf-8')
                raise
            chunks = (translator.chunks(item['abstract']) if hasattr(translator, 'chunks') else
                      offline.split_text(item['abstract'], translator.source.encode, translator.max_tokens))
            record = {'key': item['key'], 'url': item['url'], 'topics': json.loads(item.get('topics') or '[]'),
                'title': item['title'], 'title_zh': title, 'abstract': item['abstract'], 'abstract_zh': abstract,
                'previous_qwen_abstract': item.get('qwen_abstract'), 'source_chunks': len(chunks),
                'translated_chunks': len(abstract.splitlines()), 'seconds': round(time.monotonic()-tick, 2)}
            results.append(record)
            print(json.dumps({'number': len(results), 'seconds': record['seconds'], 'source_chunks': len(chunks),
                'translated_chunks': record['translated_chunks'], 'title_zh': title}, ensure_ascii=False), flush=True)
    report = {'model': getattr(translator, 'model_id', offline.MODEL_ID),
        'model_sha256': getattr(translator, 'model_sha256', cfg.get('archive_sha256')),
        'network_disabled_during_inference': True, 'papers': len(results),
        'seconds': round(time.monotonic()-started, 2), 'quality_checks': quality, 'results': results}
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'results'}, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--hymt', '--configured-model', dest='configured_model', action='store_true')
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--limit', type=int, choices=(1, 4, 10), default=10)
    parser.add_argument('--focus-title', default='')
    args = parser.parse_args()
    if args.prepare:
        if args.configured_model:
            offline.prepare(json.loads(args.config.read_text()))
        else:
            prepare_trial(args.config)
    else:
        benchmark(json.loads(args.config.read_text()), args.output, args.limit, args.focus_title)


if __name__ == '__main__':
    main()
