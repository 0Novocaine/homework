from sqlite3 import Error
import argparse
from connect import create_connection, database

parser = argparse.ArgumentParser()

def drop_table(conn, table_name):
    """ drop a table from the drop_table statement
    :param table_name:
    :param conn: Connection object
    :return:
    """
    try:
        sql = f"DROP TABLE IF EXISTS {table_name};"
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        print(f"Table '{table_name}' dropped successfully.")
    except Error as e:

        print(e)
    finally:
        cur.close()


if __name__ == '__main__':
    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description="Drop a table from SQLite database.")
        parser.add_argument("table_name", help="Name of the table to drop")
        args = parser.parse_args()

        with create_connection(database) as conn:
            drop_table(conn, args.table_name)