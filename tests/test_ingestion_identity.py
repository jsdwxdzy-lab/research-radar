"""Cross-run identities, provenance and source-versioned display; no network."""
import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import Mock, patch

from radar import dashboard, pipeline, store
from radar.util import canonical_key, now


TITLE = 'Spin controlled transport switching with negative differential resistance in a chiral molecular device'


def paper(**fields):
    item = dict(title=TITLE, authors='Yachao Zhang', kind='paper', source='crossref',
                doi='10.1063/5.0354814', arxiv_id='', abstract='Original full abstract.',
                venue='The Journal of Chemical Physics', url='https://doi.org/10.1063/5.0354814',
                published=now().date().isoformat(), score=7, topics=[], matched=[], extra={})
    item.update(fields)
    item['key'] = canonical_key(item)
    return item


class DatabaseCase(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(store.SCHEMA)
        self.addCleanup(self.conn.close)
        self.seen = now().isoformat(timespec='seconds')

    def put(self, *items):
        return store.upsert_items(self.conn, list(items), self.seen)

    def rows(self):
        return [dict(r) for r in self.conn.execute('SELECT * FROM items')]


class IdentityTests(DatabaseCase):
    def test_cross_day_supplementary_doi_reuses_original_key_and_first_seen(self):
        original = paper(_seen='2026-11-03T12:00:00+08:00')
        self.put(original)
        later = paper(source='openalex', doi='10.60893/figshare.jcp.c.8768934')
        self.assertEqual(self.put(later), (0, 1))
        row, = self.rows()
        self.assertEqual(later['key'], original['key'])
        self.assertEqual(row['first_seen'], original['_seen'])
        self.assertEqual(row['doi'], original['doi'])
        self.assertEqual(set(row['sources'].split(',')), {'crossref', 'openalex'})
        self.assertIn('doi:10.60893/figshare.jcp.c.8768934', json.loads(row['extra'])['identity_keys'])

    def test_later_doi_enriches_title_only_record_without_changing_reading_key(self):
        original = paper(doi='')
        self.put(original)
        later = paper()
        self.assertEqual(self.put(later), (0, 1))
        row, = self.rows()
        self.assertEqual(row['key'], original['key'])
        self.assertEqual(row['doi'], later['doi'])
        # The known DOI still resolves if a source later corrects the title.
        corrected = paper(title='A corrected title with entirely different wording')
        self.assertEqual(self.put(corrected), (0, 1))

    def test_arxiv_id_resolves_published_version_with_a_new_title(self):
        original = paper(doi='', arxiv_id='2611.01234', kind='preprint', source='arxiv')
        self.put(original)
        published = paper(title='A revised title', arxiv_id='2611.01234v2')
        self.assertEqual(self.put(published), (0, 1))
        self.assertEqual(published['key'], original['key'])

    def test_identical_short_or_unrelated_author_titles_stay_separate(self):
        for title, first_author, second_author in [('Editorial', 'A Author', 'A Author'),
                                                  (TITLE, 'First Author', 'Other Author')]:
            with self.subTest(title=title):
                first = paper(title=title, authors=first_author, doi='10.1/first-' + title)
                second = paper(title=title, authors=second_author, doi='10.1/second-' + title)
                self.assertEqual(self.put(first, second), (2, 0))

    def test_github_releases_with_identical_titles_are_not_collapsed(self):
        first = paper(title=TITLE, kind='release', source='github', source_id='repo/v1', doi='')
        second = paper(title=TITLE, kind='release', source='github', source_id='repo/v2', doi='')
        self.assertEqual(self.put(first, second), (2, 0))

    def test_same_batch_merge_preserves_all_sources_and_arxiv_pdf(self):
        merged, = pipeline._merge([paper(), paper(source='openalex'),
                                  paper(source='arxiv', arxiv_id='2611.01234', kind='preprint')])
        self.put(merged)
        row, = self.rows()
        self.assertEqual(row['arxiv_id'], '2611.01234')
        self.assertEqual(set(row['sources'].split(',')), {'crossref', 'openalex', 'arxiv'})
        board = dashboard.collect({'topics': []}, self.conn)
        self.assertEqual(set(board['items'][0]['src']), {'crossref', 'openalex', 'arxiv'})
        self.assertEqual(board['items'][0]['ax'], '2611.01234')

    def test_supplement_doi_alias_survives_merge_and_a_later_changed_title(self):
        supplement = paper(source='openalex', doi='10.60893/figshare.jcp.c.8768934')
        merged, = pipeline._merge([paper(), copy.deepcopy(supplement)])
        self.put(merged)
        supplement['title'] = 'Corrected supplementary material title'
        self.assertEqual(self.put(supplement), (0, 1))

    def test_dry_resolution_does_not_modify_database(self):
        self.put(paper())
        before = self.rows()
        later = paper(source='openalex', doi='10.60893/figshare.jcp.c.8768934')
        store.resolve_item_keys(self.conn, [later])
        self.assertEqual(later['key'], before[0]['key'])
        self.assertEqual(self.rows(), before)

    def test_pipeline_does_not_count_cross_run_duplicate_as_new(self):
        self.put(paper())
        incoming = paper(source='openalex', doi='10.60893/figshare.jcp.c.8768934')
        cfg = {'run': {'lookback_hours': 40}, 'topics': [],
               'sources': {'openalex': {'enabled': True}},
               'output': {'daily_dir': 'daily', 'latest': 'latest.md', 'keep_days': 400}}
        matcher = Mock()
        matcher.excluded.return_value = False
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(pipeline, 'ROOT', Path(directory)), \
             patch.object(store, 'connect', return_value=self.conn), \
             patch.object(pipeline, 'REGISTRY', {'openalex': lambda *a, **k: [incoming]}), \
             patch.object(pipeline, 'Matcher', return_value=matcher), \
             patch.object(pipeline, 'eligible', return_value=True), \
             patch.object(pipeline.agent, 'load_config', return_value={}), \
             patch.object(pipeline.annotate, 'run'), \
             patch.object(pipeline.render, 'topic_trends', return_value={}), \
             patch.object(pipeline.render, 'upcoming_events', return_value=[]), \
             patch.object(pipeline.render, 'digest', return_value='digest'), \
             patch.object(pipeline.render, 'write_index'), \
             patch.object(store, 'prune'), \
             patch.object(dashboard, 'build', return_value='board.html'):
            result = pipeline.run(cfg, use_agent=False, verbose=False)
        self.assertEqual(result['new'], 0)
        self.assertEqual(store.recent_runs(self.conn, 1)[0]['new_items'], 0)
        self.assertEqual(len(self.rows()), 1)


class DisplayCacheTests(DatabaseCase):
    def test_source_change_hides_stale_translation_and_review_but_preserves_cache(self):
        item = paper()
        self.put(item)
        store.save_annotations(self.conn, [dict(key=item['key'], title_zh='旧标题',
            abstract_zh='旧摘要', review='旧评论', source_hash=store.annotation_source_hash(item))], 'review-model')
        store.save_translations(self.conn, [dict(key=item['key'], title_zh='旧离线标题',
            abstract_zh='旧离线摘要', source_hash=store.annotation_source_hash(item))], 'offline')
        self.conn.execute('UPDATE items SET abstract=?', ('A changed and complete abstract.',))
        row, = dashboard.collect({'topics': []}, self.conn)['items']
        self.assertEqual((row['tz'], row['az'], row['rv']), ('', '', ''))
        self.assertEqual(self.conn.execute('SELECT abstract_zh FROM annotations').fetchone()[0], '旧摘要')
        self.assertEqual(self.conn.execute('SELECT abstract_zh FROM translations').fetchone()[0], '旧离线摘要')
        self.assertEqual(len(store.pending_translations(self.conn, 10)), 1)

    def test_fresh_offline_translation_does_not_revive_stale_review(self):
        item = paper()
        self.put(item)
        store.save_annotations(self.conn, [dict(key=item['key'], title_zh='旧标题',
            abstract_zh='旧摘要', review='旧评论', source_hash=store.annotation_source_hash(item))], 'review-model')
        self.conn.execute('UPDATE items SET abstract=?', ('New source abstract.',))
        current = self.rows()[0]
        store.save_translations(self.conn, [dict(key=item['key'], title_zh='新标题',
            abstract_zh='新摘要', source_hash=store.annotation_source_hash(current))], 'offline')
        row, = dashboard.collect({'topics': []}, self.conn)['items']
        self.assertEqual((row['tz'], row['az'], row['rv']), ('新标题', '新摘要', ''))


if __name__ == '__main__':
    unittest.main()
