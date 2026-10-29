import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from radar import pipeline,store


class CompletedBoardTests(unittest.TestCase):
    def execute(self,board):
        conn=sqlite3.connect(':memory:');conn.row_factory=sqlite3.Row;conn.executescript(store.SCHEMA)
        self.addCleanup(conn.close)
        cfg={'run':{'lookback_hours':40},'output':{'daily_dir':'daily','latest':'latest.md','keep_days':400},'topics':[]}
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(pipeline,'ROOT',Path(directory)), \
             patch.object(pipeline.store,'connect',return_value=conn), \
             patch.object(pipeline,'REGISTRY',{}), \
             patch.object(pipeline.agent,'load_config',return_value={}), \
             patch.object(pipeline.annotate,'run'), \
             patch.object(pipeline.render,'topic_trends',return_value={}), \
             patch.object(pipeline.render,'upcoming_events',return_value=[]), \
             patch.object(pipeline.render,'digest',return_value='digest'), \
             patch.object(pipeline.render,'write_index'), \
             patch.object(pipeline.store,'prune'), \
             patch.object(pipeline.dashboard,'build',side_effect=lambda *_:board(conn)):
            return pipeline.run(cfg,use_agent=False,verbose=False)

    def test_zero_new_board_embeds_completed_record(self):
        def board(conn):
            row=conn.execute('SELECT * FROM runs ORDER BY id DESC LIMIT 1').fetchone()
            self.assertEqual(row['status'],'ok')
            self.assertEqual(row['new_items'],0)
            self.assertIsNotNone(row['finished'])
            self.assertEqual(json.loads(row['note'])['stats'],{})
            return 'test-board.html'
        summary=self.execute(board)
        self.assertEqual(summary['new'],0)

    def test_render_failure_cannot_silently_publish_stale_html(self):
        def broken(conn):raise OSError('render failed')
        with self.assertRaisesRegex(OSError,'render failed'):self.execute(broken)


if __name__=='__main__':unittest.main()
