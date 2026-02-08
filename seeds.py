# seed.py
from faker import Faker
from random import randint, choice
from itertools import cycle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.db import DATABASE_URL
from config.models import Base, Student, Teacher, Group, Subject, Grade


NUMBER_OF_STUDENTS = 30
NUMBER_OF_TEACHERS = 3
GROUPS = ["Group A", "Group B", "Group C"]
SUBJECTS = ["Math", "Biology", "Geography", "Physics", "Chemistry", "Computer Science"]
GRADES_OPTIONS = [1, 20]

faker = Faker("uk_UA")


#   ♂️Создание сессии
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


#   ♂️Генерация данных

#   Генерация групп
groups = [Group(name=name) for name in GROUPS]
session.add_all(groups)
session.commit()


#   Генерация учителей
teachers = [Teacher(fullname=f"Викладач {faker.name()}") for _ in range(NUMBER_OF_TEACHERS)]
session.add_all(teachers)
session.commit()


#   Генерация студентов
students = [Student(fullname=faker.name(), group_id=randint(1, len(groups))) for _ in range(NUMBER_OF_STUDENTS)]
session.add_all(students)
session.commit()


#   Генерация дисциплин
teacher_cycle = cycle(teachers)
subjects = [Subject(name=name, teacher=next(teacher_cycle)) for name in SUBJECTS]
session.add_all(subjects)
session.commit()


#   Генерация оценок
grades_list = []
for student in students:
    marks_count = choice(GRADES_OPTIONS)
    for _ in range(marks_count):
        grade = Grade(
            grade=randint(1, 12),
            grade_date=faker.date_this_year(),
            student=student,
            discipline=choice(subjects)
        )
        grades_list.append(grade)


session.add_all(grades_list)
session.commit()


print("DB seeded successfully!")