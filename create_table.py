from sqlite3 import Error

from connect import create_connection, database


def create_table(conn, create_table_sql):
    """

    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        conn.commit()
    except Error as e:
        print(e)
conn = create_connection(database)
print(conn)

if __name__ == '__main__':

    sql_create_groups_table = """
    CREATE TABLE IF NOT EXISTS groups (
    id integer PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL
    );
    """

    sql_create_students_table = """
    CREATE TABLE IF NOT EXISTS students (
     id integer PRIMARY KEY AUTOINCREMENT,
     name text NOT NULL,
     group_id integer NOT NULL,
     FOREIGN KEY (group_id) REFERENCES groups (id)
    );
    """

    sql_create_teachers_table = """
    CREATE TABLE IF NOT EXISTS teachers (
     id integer PRIMARY KEY AUTOINCREMENT,
     name text NOT NULL
    );
    """

    sql_create_subjects_table = """
    CREATE TABLE IF NOT EXISTS subjects (
    id integer PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL,
    teacher_id INTEGER NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
    );
    """


    sql_create_marks_table = """
    CREATE TABLE marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
    );
    """


    with create_connection(database) as conn:
        print(type(conn))
        if conn is not None:
            create_table(conn, sql_create_students_table)
            create_table(conn, sql_create_teachers_table)
            create_table(conn, sql_create_groups_table)
            create_table(conn, sql_create_subjects_table)
            create_table(conn, sql_create_marks_table)

        else:
            print("Error! cannot create the database connection.")
