from faker import Faker
from random import randint, choice
import sqlite3
from itertools import cycle

NUMBER_OF_STUDENTS = 30
NUMBER_OF_TEACHERS = 3
GROUPS = ["Group A", "Group B", "Group C"]
SUBJECTS = ["Math", "Biology", "Geography", "Physics", "Chemistry", "Computer Science"]
GRADES_OPTIONS = [1, 20]

faker = Faker("uk_UA")


def generate_fake_students(students_count: int) -> list[str]:
    """

    :param students_count:
    :return:
    """
    return [faker.name() for _ in range(students_count)]


def generate_fake_teachers(teachers_count: int) -> list[str]:
    """

    :param teachers_count:
    :return:
    """
    return [f"викладач {faker.name()}" for _ in range(teachers_count)]


def generate_fake_subjects(subjects_list: list[str], teachers_count: int) -> list[tuple]:
    """

    :param subjects_list:
    :param teachers_count:
    :return:
    """
    teacher_cycle = cycle(range(1, teachers_count + 1))
    return [(subject, next(teacher_cycle)) for subject in subjects_list]


def generate_fake_marks(grades_options: list, students_count: int, subjects_list: list) -> list[tuple]:
    """

    :param grades_options:
    :param students_count:
    :param subjects_list:
    :return:
    """
    marks_list = []
    for student_id in range(1, students_count+1):
        marks_count = choice(grades_options)
        for _ in range(marks_count):
            marks_list.append((
                student_id,
                randint(1, len(subjects_list)),
                randint(1, 12),
                faker.date_this_year().isoformat()
            ))
    return marks_list


def prepare_data(students_list: list,
                 teachers_list: list,
                 groups_list: list,
                 subjects_list: list,
                 marks_list: list,
                 ) -> tuple:
    """
    :param students_list:
    :param teachers_list:
    :param groups_list:
    :param subjects_list:
    :param marks_list:
    :return:
    """
    for_students = [(student,randint(1, len(groups_list))) for student in students_list]
    for_teachers = [(teacher,) for teacher in teachers_list]
    for_groups = [(group,) for group in groups_list]
    for_subjects = subjects_list
    for_marks = marks_list
    print(for_groups)
    return for_students, for_teachers, for_groups, for_subjects, for_marks


def insert_data_to_db(students_list: list,
                      teachers_list: list,
                      groups_list: list,
                      subjects_list: list,
                      marks_list: list) -> None:
    """
    :param students_list:
    :param teachers_list:
    :param groups_list:
    :param subjects_list:
    :param marks_list:
    :return:
    """

    with sqlite3.connect('hw6') as con:

        cur = con.cursor()

        # Студенты
        sql_to_students = """INSERT INTO students(name, group_id)
                               VALUES (?, ?)"""
        cur.executemany(sql_to_students, students_list)

        # Учителя
        sql_to_teachers = """INSERT INTO teachers(name)
                                       VALUES (?)"""
        cur.executemany(sql_to_teachers, teachers_list)

        # Группы
        sql_to_groups = """INSERT INTO groups(name)
                                       VALUES (?)"""
        cur.executemany(sql_to_groups, groups_list)

        #Предметы
        sql_to_subjects = """INSERT INTO subjects(name, teacher_id)
                                      VALUES (?, ?)"""
        cur.executemany(sql_to_subjects, subjects_list)

        # Оценки
        sql_to_marks = """INSERT INTO marks(student_id, subject_id, score, date)
                               VALUES (?, ?, ?, ?)"""
        cur.executemany(sql_to_marks, marks_list)

        con.commit()


if __name__ == "__main__":
    students, teachers, groups, subjects, marks = prepare_data(
        generate_fake_students(NUMBER_OF_STUDENTS),
        generate_fake_teachers(NUMBER_OF_TEACHERS),
        GROUPS,
        generate_fake_subjects(SUBJECTS, NUMBER_OF_TEACHERS),
        generate_fake_marks(GRADES_OPTIONS, NUMBER_OF_STUDENTS, SUBJECTS)
    )
    # print(subjects)
    # print(students)
    # print(teachers)
    # print(marks)
    # print(groups)
    # print(subjects)
    insert_data_to_db(students, teachers, groups, subjects, marks)







