"""Offline translation regression checks; no downloads, keys or file database."""
import json
from pathlib import Path
import re
import sqlite3
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from radar import annotate, local_llm_translate, offline_translate as offline, store


def connection():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.executescript(store.SCHEMA)
    return conn


def add_item(conn, key='paper:one', abstract='First sentence. Last sentence.'):
    conn.execute("INSERT INTO items (key,title,abstract,authors,venue,first_seen,score) "
                 "VALUES (?, 'A paper', ?, 'Author', 'Journal', datetime('now'), 10)", (key, abstract))
    conn.commit()
    return dict(conn.execute('SELECT * FROM items WHERE key=?', (key,)).fetchone())


def old_translation(conn, item, review='已有短评', abstract='已有完整摘要'):
    store.save_annotations(conn, [{'key': item['key'], 'title_zh': '已有中文标题',
        'abstract_zh': abstract, 'review': review, 'source_hash': store.annotation_source_hash(item)}], 'qwen')


class OfflineTranslationTests(unittest.TestCase):
    def test_method_name_before_colon_is_kept_without_translating_it(self):
        translator = local_llm_translate.Translator.__new__(local_llm_translate.Translator)
        translator.translate = Mock(return_value='在Wyckoff轨道上生成晶体')
        translator.set_context('Orbitol: Crystal Generation on Wyckoff Orbits')
        self.assertEqual(translator.protected_terms, ['Orbitol'])
        self.assertEqual(translator.translate_title('Orbitol: Crystal Generation on Wyckoff Orbits'),
                         'Orbitol：在Wyckoff轨道上生成晶体')
        translator.translate.assert_called_once_with('Crystal Generation on Wyckoff Orbits')

    def test_wrong_median_translation_is_rejected(self):
        translator = local_llm_translate.Translator.__new__(local_llm_translate.Translator)
        translator.chunks = lambda text: [text]
        translator.engine = Mock()
        translator.engine.create_completion.return_value = {'choices': [{'text': '平均性能提高九倍。', 'finish_reason': 'stop'}]}
        with self.assertRaisesRegex(ValueError, '关键科研术语'):
            translator.translate('Their median figure of merit was nine times higher.')

    def test_missing_percent_sign_retries_the_original_sentence(self):
        translator = local_llm_translate.Translator.__new__(local_llm_translate.Translator)
        translator.chunks = lambda text: [text]
        translator.engine = Mock()
        translator.engine.create_completion.side_effect = [
            {'choices': [{'text': '24%的候选材料进入前10名。', 'finish_reason': 'stop'}]},
            {'choices': [{'text': '24%的候选材料进入前10%。', 'finish_reason': 'stop'}]},
        ]
        original = "24% of the candidates ranked in that set's top 10%."
        self.assertEqual(translator.translate(original), '24%的候选材料进入前10%。')
        prompt = translator.engine.create_completion.call_args.kwargs['prompt']
        self.assertIn(original, prompt)
        self.assertIn('10%', prompt)
        self.assertIn('必须完整保留', prompt)

    def test_repeated_missing_percentage_is_not_cached(self):
        translator = local_llm_translate.Translator.__new__(local_llm_translate.Translator)
        translator.chunks = lambda text: [text]
        translator.engine = Mock()
        translator.engine.create_completion.return_value = {'choices': [{'text': '候选结构位列前十名。', 'finish_reason': 'stop'}]}
        with self.assertRaisesRegex(ValueError, '百分比'):
            translator.translate('The structures ranked in the top 10%.')

    def test_qwen_chunk_packing_keeps_the_complete_input(self):
        translator = local_llm_translate.Translator.__new__(local_llm_translate.Translator)
        translator.max_tokens = 80
        translator.engine = SimpleNamespace(tokenize=lambda b, **kw: list(b))
        source = 'One source sentence. ' * 300 + 'The final sentence about crystals.'
        chunks = translator.chunks(source)
        self.assertEqual(re.sub(r'\s', '', ''.join(chunks)), re.sub(r'\s', '', source))
        self.assertTrue(all(len(translator.encode(p)) <= 80 for p in chunks))
        self.assertTrue(chunks[-1].endswith('crystals.'))

    def test_qwen_requires_complete_output_and_disables_thinking(self):
        translator = local_llm_translate.Translator.__new__(local_llm_translate.Translator)
        translator.chunks = lambda text: [text]
        translator.engine = Mock()
        translator.engine.create_completion.return_value = {'choices': [{'text': '截断的译文', 'finish_reason': 'length'}]}
        with self.assertRaisesRegex(ValueError, '未完整结束'):
            translator.translate('A source sentence.')
        prompt = translator.engine.create_completion.call_args.kwargs['prompt']
        self.assertTrue(prompt.endswith('<|im_start|>assistant\n'))
        translator.engine.create_completion.return_value = {'choices': [{'text': '<think>思考</think>译文', 'finish_reason': 'stop'}]}
        with self.assertRaisesRegex(ValueError, '思考'):
            translator.translate('A source sentence.')
        translator.engine.create_completion.return_value = {'choices': [{'text': '完整译文。', 'finish_reason': 'stop'}]}
        self.assertEqual(translator.translate('A source sentence.'), '完整译文。')

    def test_long_text_and_last_sentence_are_never_discarded(self):
        original = ('First sentence about crystals. ' * 200) + 'THE_LAST_SENTENCE_IS_HERE.'
        parts = offline.split_text(original, lambda s: list(s), 80)
        self.assertGreater(len(parts), 100)
        self.assertEqual(re.sub(r'\s', '', ''.join(parts)), re.sub(r'\s', '', original))
        self.assertTrue(parts[-1].endswith('THE_LAST_SENTENCE_IS_HERE.'))
        self.assertTrue(all(0 < len(p) <= 80 for p in parts))

    def test_unbroken_text_is_split_without_losing_characters(self):
        original = 'LongFormula123' * 300
        parts = offline.split_text(original, list, 64)
        self.assertEqual(''.join(parts), original)
        self.assertTrue(all(len(p) <= 64 for p in parts))
        self.assertEqual(offline.split_text('  \n ', list), [])

    def test_decoder_cutoff_is_rejected_and_input_truncation_disabled(self):
        translator = offline.Translator.__new__(offline.Translator)
        translator.source = SimpleNamespace(encode=lambda value, **kwargs: list(value))
        translator.target = SimpleNamespace(decode=lambda value: ''.join(value))
        translator.max_tokens = 192
        translator.engine = Mock()
        translator.engine.translate_batch.return_value = [SimpleNamespace(hypotheses=[['中', '文']])]
        with self.assertRaisesRegex(ValueError, '未完整结束'):
            translator.translate('An original sentence.')
        self.assertEqual(translator.engine.translate_batch.call_args.kwargs['max_input_length'], 0)
        translator.engine.translate_batch.return_value = [SimpleNamespace(hypotheses=[['中', '文', '</s>']])]
        self.assertEqual(translator.translate('An original sentence.'), '中文')

    def test_existing_qwen_text_is_kept_without_requiring_a_review(self):
        conn = connection()
        item = add_item(conn)
        old_translation(conn, item, review='')
        before = [tuple(r) for r in conn.execute('SELECT * FROM annotations')]
        self.assertEqual(store.pending_translations(conn, 5), [])
        with patch.object(offline, 'Translator', autospec=True) as engine:
            self.assertEqual(offline.run({}, conn, log=lambda *a: None), 0)
        engine.assert_not_called()
        self.assertEqual([tuple(r) for r in conn.execute('SELECT * FROM annotations')], before)

    def test_offline_dispatch_does_not_read_or_call_qwen(self):
        conn = connection()
        add_item(conn)
        with patch.object(offline, 'load_config', return_value={'enabled': True}), \
             patch.object(offline, 'run', return_value=1) as run, \
             patch.object(annotate, 'api_key') as credential, patch.object(annotate.agent, 'chat') as chat:
            self.assertEqual(annotate.run({}, conn), 1)
        credential.assert_not_called()
        chat.assert_not_called()
        run.assert_called_once()

    def test_new_translation_never_fabricates_a_review(self):
        conn = connection()
        item = add_item(conn)
        with patch.object(offline, 'Translator', autospec=True) as engine:
            engine.return_value.translate.side_effect = ['离线中文标题', '第一句。最后一句。']
            self.assertEqual(offline.run({}, conn, log=lambda *a: None), 1)
        self.assertEqual(conn.execute('SELECT count(*) FROM annotations').fetchone()[0], 0)
        result = store.load_annotation_map(conn)[item['key']]
        self.assertEqual(result, {'title_zh': '离线中文标题', 'abstract_zh': '第一句。最后一句。', 'review': ''})
        self.assertEqual(store.pending_translations(conn, 5), [])
        self.assertEqual(store.pending_translations(conn, 0), [])

    def test_newly_recovered_abstract_invalidates_the_old_translation(self):
        conn = connection()
        item = add_item(conn, abstract='')
        store.save_translations(conn, [{'key': item['key'], 'title_zh': '标题', 'abstract_zh': '',
            'source_hash': store.annotation_source_hash(item)}], offline.MODEL_ID)
        self.assertEqual(store.pending_translations(conn, 5), [])
        conn.execute("UPDATE items SET abstract='Recovered complete abstract.'")
        self.assertEqual(len(store.pending_translations(conn, 5)), 1)

    def test_only_the_missing_field_is_translated(self):
        conn = connection()
        item = add_item(conn)
        old_translation(conn, item, abstract='')
        with patch.object(offline, 'Translator', autospec=True) as engine:
            engine.return_value.translate.return_value = '补齐的完整摘要'
            self.assertEqual(offline.run({}, conn, log=lambda *a: None), 1)
        engine.return_value.translate.assert_called_once_with(item['abstract'])
        result = store.load_annotation_map(conn)[item['key']]
        self.assertEqual(result['title_zh'], '已有中文标题')
        self.assertEqual(result['abstract_zh'], '补齐的完整摘要')
        self.assertEqual(result['review'], '已有短评')

    def test_failure_does_not_overwrite_any_existing_text(self):
        conn = connection()
        item = add_item(conn)
        old_translation(conn, item)
        conn.execute("UPDATE items SET abstract='A changed abstract.'")
        with patch.object(offline, 'Translator', autospec=True) as engine:
            engine.return_value.translate.side_effect = ['新标题', ValueError('cutoff')]
            self.assertEqual(offline.run({}, conn, log=lambda *a: None), 0)
        self.assertEqual(store.load_annotation_map(conn)[item['key']]['abstract_zh'], '已有完整摘要')
        self.assertEqual(conn.execute('SELECT count(*) FROM translations').fetchone()[0], 0)
        self.assertEqual(len(store.pending_translations(conn, 5)), 1)

    def test_absent_source_abstract_is_not_invented(self):
        conn = connection()
        add_item(conn, abstract='')
        with patch.object(offline, 'Translator', autospec=True) as engine:
            engine.return_value.translate.side_effect = lambda s: '标题' if s else ''
            self.assertEqual(offline.run({}, conn, log=lambda *a: None), 1)
        self.assertEqual(conn.execute('SELECT abstract_zh FROM translations').fetchone()[0], '')
        self.assertEqual(store.pending_translations(conn, 5), [])

    def test_time_budget_leaves_pending_work_for_next_run(self):
        conn = connection()
        add_item(conn)
        with patch.object(offline, 'Translator', autospec=True) as engine, \
             patch.object(offline.time, 'monotonic', side_effect=[0, 901]):
            self.assertEqual(offline.run({}, conn, log=lambda *a: None), 0)
        engine.return_value.translate.assert_not_called()
        self.assertEqual(len(store.pending_translations(conn, 5)), 1)

    def test_completed_work_survives_a_budget_cutoff_and_next_run_continues(self):
        conn = connection()
        add_item(conn, key='paper:first')
        add_item(conn, key='paper:second')
        with patch.object(offline, 'Translator', autospec=True) as engine, \
             patch.object(offline.time, 'monotonic', side_effect=[0, 0, 901]):
            engine.return_value.translate.return_value = '完整译文'
            self.assertEqual(offline.run({}, conn, log=lambda *a: None), 1)
        self.assertEqual(conn.execute('SELECT count(*) FROM translations').fetchone()[0], 1)
        self.assertEqual(len(store.pending_translations(conn, 5)), 1)
        with patch.object(offline, 'Translator', autospec=True) as engine:
            engine.return_value.translate.return_value = '下一篇译文'
            self.assertEqual(offline.run({}, conn, log=lambda *a: None), 1)
            self.assertEqual(engine.return_value.translate.call_count, 2)
        self.assertEqual(store.pending_translations(conn, 5), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
