import sqlite3
from contextlib import contextmanager

database = './hw6'


@contextmanager
def create_connection(db_file):
    """ создание подключения к дб """
    conn = sqlite3.connect(db_file)
    yield conn
    conn.rollback()
    conn.close()
