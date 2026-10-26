"""Offline regression checks: no network, real credentials, or on-disk database."""
import ast
import json
from pathlib import Path
import sqlite3
import sys
import unittest
from unittest.mock import patch

STAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE))
from radar import agent, annotate, dashboard, store


def connection():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.executescript(store.SCHEMA)
    return conn


def add_item(conn, key='paper:one', abstract='Full abstract.'):
    conn.execute(
        """INSERT INTO items (key, title, abstract, authors, venue, first_seen, score,
               topics, matched, extra, sources)
           VALUES (?, 'Title', ?, 'Author', 'Journal', datetime('now'), 5, '[]', '[]', '{}', 'arxiv')""",
        (key, abstract),
    )
    conn.commit()
    return dict(conn.execute('SELECT * FROM items WHERE key=?', (key,)).fetchone())


def full_result(abstract='完整摘要', end=True):
    return {'text': 'TITLE: 中文标题\nABS: ' + abstract + '\nREV: 方法、对象与研究方向。'
            + ('\nEND: 完整' if end else ''), 'finish_reason': 'stop'}


class TranslationFixes(unittest.TestCase):
    def test_long_input_and_translation_survive(self):
        original = 'Original sentence. ' * 200 + 'SOURCE_LAST_SENTENCE'
        chinese = '保留全部信息。' * 400 + '译文最后一句'
        item = {'key': 'one', 'title': 'Title', 'abstract': original}
        with patch.object(annotate.agent, 'chat', return_value=full_result(chinese)) as chat:
            rows = annotate._one_batch({'abstract_chars': 700}, [item])
        prompt = chat.call_args.args[1][1]['content']
        self.assertIn('SOURCE_LAST_SENTENCE', prompt)
        self.assertEqual(rows[0]['abstract_zh'], chinese)
        self.assertEqual(rows[0]['source_hash'], store.annotation_source_hash(item))

    def test_token_cutoff_is_rejected(self):
        result = full_result()
        result['finish_reason'] = 'length'
        with patch.object(annotate.agent, 'chat', return_value=result):
            with self.assertRaises(ValueError):
                annotate._one_batch({}, [{'key': 'one', 'abstract': 'Original'}])

    def test_missing_end_or_abstract_is_rejected(self):
        for result in (full_result(end=False), full_result('（无）')):
            with self.subTest(result=result), patch.object(annotate.agent, 'chat', return_value=result):
                with self.assertRaises(ValueError):
                    annotate._one_batch({}, [{'key': 'one', 'abstract': 'Original'}])

    def test_one_invalid_row_cannot_be_hidden_by_valid_row(self):
        text = full_result()['text'] + '\n===\nTITLE: 标题\nABS: 摘要\nREV:\nEND: 完整'
        with patch.object(annotate.agent, 'chat', return_value={'text': text}):
            with self.assertRaises(ValueError):
                annotate._one_batch({}, [{'key': 'one'}, {'key': 'two'}])

    def test_no_abstract_is_preserved_as_missing(self):
        with patch.object(annotate.agent, 'chat', return_value=full_result('（无）')):
            rows = annotate._one_batch({}, [{'key': 'one', 'abstract': ''}])
        self.assertEqual(rows[0]['abstract_zh'], '')

    def test_legacy_cache_is_refreshed_and_source_changes_invalidate(self):
        conn = connection()
        item = add_item(conn)
        store.save_annotations(conn, [{'key': item['key'], 'title_zh': '旧标题',
                                      'abstract_zh': '旧节选', 'review': '旧短评'}], 'old-model')
        self.assertEqual(len(store.pending_annotations(conn, 5)), 1)
        store.save_annotations(conn, [{'key': item['key'], 'title_zh': '新标题',
                                      'abstract_zh': '完整译文', 'review': '短评',
                                      'source_hash': store.annotation_source_hash(item)}], 'new-model')
        self.assertEqual(store.pending_annotations(conn, 5), [])
        conn.execute('UPDATE items SET abstract=? WHERE key=?', ('A newly recovered full abstract.', item['key']))
        self.assertEqual(len(store.pending_annotations(conn, 5)), 1)
        self.assertEqual(store.pending_annotations(conn, 0), [])

    def test_schema_migration_keeps_existing_items_and_translations(self):
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        conn.executescript(store.SCHEMA.split('CREATE TABLE IF NOT EXISTS annotation_inputs')[0])
        item = add_item(conn)
        conn.execute("INSERT INTO annotations (key, abstract_zh) VALUES (?, '原译文')", (item['key'],))
        conn.commit()
        conn.executescript(store.SCHEMA)
        self.assertEqual(conn.execute('SELECT COUNT(*) FROM items').fetchone()[0], 1)
        self.assertEqual(conn.execute('SELECT abstract_zh FROM annotations').fetchone()[0], '原译文')
        self.assertEqual(len(store.pending_annotations(conn, 5)), 1)

    def test_failed_translation_keeps_old_cache_and_retries_later(self):
        conn = connection()
        item = add_item(conn)
        store.save_annotations(conn, [{'key': item['key'], 'title_zh': '旧标题',
                                      'abstract_zh': '旧译文', 'review': '旧短评'}], 'old-model')
        with patch.object(annotate, 'load_config', return_value={'enabled': True, 'base_url': 'https://example.invalid'}), \
             patch.object(annotate, 'api_key', return_value='offline-placeholder'), \
             patch.object(annotate, '_one_batch', side_effect=ValueError('incomplete')), \
             patch.dict(annotate.os.environ, {}, clear=True):
            self.assertEqual(annotate.run({}, conn, log=lambda *args: None), 0)
        self.assertEqual(conn.execute('SELECT abstract_zh FROM annotations').fetchone()[0], '旧译文')
        self.assertEqual(len(store.pending_annotations(conn, 5)), 1)

    def test_translation_budget_stops_before_next_call(self):
        conn = connection()
        add_item(conn)
        with patch.object(annotate, 'load_config', return_value={'enabled': True, 'base_url': 'https://example.invalid'}), \
             patch.object(annotate, 'api_key', return_value='offline-placeholder'), \
             patch.object(annotate.time, 'monotonic', side_effect=[0, 601]), \
             patch.object(annotate, '_one_batch') as batch, \
             patch.dict(annotate.os.environ, {}, clear=True):
            self.assertEqual(annotate.run({}, conn, log=lambda *args: None), 0)
        batch.assert_not_called()

    def test_dashboard_keeps_last_sentence(self):
        conn = connection()
        abstract = 'Original. ' * 400 + 'LAST_SENTENCE'
        item = add_item(conn, abstract=abstract)
        self.assertEqual(dashboard._row(item)['a'], abstract)

    def test_review_credentials_do_not_fall_back_to_overview_key_files(self):
        self.assertEqual(agent._candidate_key_files({'api_key_env': 'USTC_LLM_KEY'}), [])

    def test_missing_interface_credential_stops_before_network(self):
        with patch.object(agent, 'api_key', return_value=''), patch.object(agent.urllib.request, 'urlopen') as request:
            with self.assertRaisesRegex(RuntimeError, '专用凭据'):
                agent.chat({'base_url': 'https://example.invalid'}, [])
        request.assert_not_called()

    def test_all_proposed_python_files_parse(self):
        for path in (STAGE / 'radar').rglob('*.py'):
            ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        json.loads((STAGE / 'config/review.json').read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)
