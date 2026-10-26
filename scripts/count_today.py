#!/usr/bin/env python3
"""Print how many items were first seen today (used by the Actions summary)."""
import sqlite3
import sys
from pathlib import Path

db = Path(__file__).resolve().parent.parent / "state" / "radar.sqlite3"
try:
    conn = sqlite3.connect(str(db))
    n = conn.execute(
        "SELECT COUNT(*) FROM items WHERE first_seen >= date('now')"
    ).fetchone()[0]
    print(n)
except Exception as exc:  # pragma: no cover
    print("n/a")
    sys.exit(0)
