import sqlite3
import sys
from pathlib import Path

DB_FILE = 'hw6'
SQL_DIR = Path('.')

with sqlite3.connect(DB_FILE) as con:
    cur = con.cursor()
    sql = (SQL_DIR / sys.argv[1]).read_text()
    cur.execute(sql)
    for row in cur.fetchall():
        print(row)