import importlib.util
import json
from pathlib import Path
import subprocess
import sqlite3
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/daily_update_needed.py'
spec = importlib.util.spec_from_file_location('daily_gate', SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class DailyGateTests(unittest.TestCase):
    def setUp(self):
        self.data = {'today':'2026-10-28', 'generated':'2026-10-28 08:00',
                     'run':{'status':'ok','started':'2026-10-28T07:35'},
                     'health':[{'src':'arxiv','err':''}],
                     'items':[{'tz':'中文标题','a':'abstract','az':'完整摘要'}]}

    def check_needed(self, expected):
        self.assertEqual(gate.needed(self.data, '2026-10-28')[0], expected)

    def test_complete_today_skips(self): self.check_needed(False)
    def test_stale_board_retries(self):
        self.data['today']='2026-10-27'; self.check_needed(True)
    def test_rendering_today_does_not_replace_a_fetch(self):
        self.data['run']['started']='2026-10-27T14:20'; self.check_needed(True)
    def test_failed_fetch_retries(self):
        self.data['run']['status']='error'; self.check_needed(True)
    def test_missing_title_retries(self):
        self.data['items'][0]['tz']=''; self.check_needed(True)
    def test_missing_translation_retries(self):
        self.data['items'][0]['az']=''; self.check_needed(True)
    def test_absent_source_abstract_does_not_retry(self):
        self.data['items'][0].update(a='',az=''); self.check_needed(False)
    def test_source_error_retries(self):
        self.data['health'][0]['err']='timeout'; self.check_needed(True)
    def test_no_papers_retries(self):
        self.data['items']=[]; self.check_needed(True)
    def test_invalid_board_emits_needed(self):
        with tempfile.TemporaryDirectory() as directory:
            board=Path(directory)/'index.html'; board.write_text('broken')
            output=Path(directory)/'output'
            result=subprocess.run([sys.executable,'-B',str(SCRIPT),'--event','schedule',
                                   '--board',str(board),'--output',str(output)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0)
            self.assertEqual(output.read_text(),'needed=true\n')
    def test_manual_does_not_need_a_board(self):
        result=subprocess.run([sys.executable,'-B',str(SCRIPT),'--event','workflow_dispatch',
                               '--board','/nonexistent/board'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0)
        self.assertIn('needed=true',result.stdout)
    def test_successful_database_overrides_render_time_running_status(self):
        with tempfile.TemporaryDirectory() as directory:
            db=Path(directory)/'radar.sqlite3'
            with sqlite3.connect(db) as conn:
                conn.execute('CREATE TABLE runs (id INTEGER, started TEXT, status TEXT, note TEXT)')
                conn.execute('INSERT INTO runs VALUES (1,?,?,?)',('2026-10-28T07:35','ok',
                             json.dumps({'stats':{'arxiv':{'error':''}}})))
            self.data['run']={'status':'running','started':'2026-10-28T07:35'}
            self.data['health']=[]
            self.data['run'], self.data['health']=gate.latest_run(db)
            self.check_needed(False)
    def test_missing_database_does_not_create_one(self):
        with tempfile.TemporaryDirectory() as directory:
            db=Path(directory)/'missing.sqlite3'
            with self.assertRaises(sqlite3.Error): gate.latest_run(db)
            self.assertFalse(db.exists())


if __name__=='__main__': unittest.main()
