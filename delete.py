from sqlite3 import Error

from connect import create_connection, database


def delete_task(conn):
    """
    Clean all tables
    :param conn:  Connection to the SQLite database
    :return:
    """
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM marks")
        cur.execute("DELETE FROM students")
        cur.execute("DELETE FROM teachers")
        cur.execute("DELETE FROM groups")
        cur.execute("DELETE FROM subjects")

        conn.commit()
    except Error as e:
        print(e)
    finally:
        cur.close()


if __name__ == '__main__':
    with create_connection(database) as conn:
        delete_task(conn)

