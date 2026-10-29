#!/usr/bin/env python3
"""Skip redundant scheduled retries only after a complete daily update."""
from __future__ import annotations

import argparse
from contextlib import closing
import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

SHANGHAI = timezone(timedelta(hours=8))


def latest_run(database: Path) -> tuple[dict, list]:
    # The page is rendered before finish_run updates the database. Its embedded
    # run status can still be "running" after a successful commit.
    with closing(sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute('SELECT started,status,note FROM runs ORDER BY id DESC LIMIT 1').fetchone()
    if row is None:
        return {}, []
    run = dict(row)
    stats = json.loads(run.get('note') or '{}').get('stats', {})
    health = [{'src':name, 'err':entry.get('error') or ''} for name,entry in stats.items()]
    return run, health


def needed(data: dict, today: str) -> tuple[bool, str]:
    if data.get('today') != today:
        return True, 'board date is stale'
    run = data.get('run') or {}
    if run.get('status') != 'ok' or not str(run.get('started', '')).startswith(today + 'T'):
        return True, 'no successful fetch today'
    health = data.get('health') or []
    if not health or any(h.get('err') for h in health):
        return True, 'source health needs retry'
    items = data.get('items') or []
    if not items:
        return True, 'no visible papers'
    if any(not (i.get('tz') or '').strip() or
           ((i.get('a') or '').strip() and not (i.get('az') or '').strip())
           for i in items):
        return True, 'translation coverage incomplete'
    return False, 'today already fetched and translated'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--event', required=True)
    parser.add_argument('--board', type=Path, default=Path('index.html'))
    parser.add_argument('--database', type=Path, default=Path('state/radar.sqlite3'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.event != 'schedule':
        decision, reason = True, 'manual runs always allowed'
    else:
        try:
            html = args.board.read_text(encoding='utf-8')
            marker = re.search(r'(?:const|let) DATA\s*=\s*', html)
            if marker is None:
                raise ValueError('missing data marker')
            data, _ = json.JSONDecoder().raw_decode(html[marker.end():])
            data['run'], data['health'] = latest_run(args.database)
            decision, reason = needed(data, datetime.now(SHANGHAI).date().isoformat())
        except (OSError, ValueError, TypeError, AttributeError, sqlite3.Error):
            decision, reason = True, 'board unavailable or invalid'
    value = 'true' if decision else 'false'
    print('needed=' + value + ': ' + reason)
    if args.output:
        with args.output.open('a', encoding='utf-8') as output:
            output.write('needed=' + value + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
