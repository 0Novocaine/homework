# my_select.py
from typing import Any

from sqlalchemy import func
from config.db import DATABASE_URL
from config.models import Student, Teacher, Group, Subject, Grade
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# 1. Знайти 5 студентів із найбільшим середнім балом з усіх предметів
def select_1() -> list:
    session = SessionLocal()
    result = (session.query(
        Student.fullname,
        func.round(func.avg(Grade.grade), 2).label('avg_grade'))
              .join(Grade)
              .group_by(Student.id)
              .order_by(func.avg(Grade.grade).desc()).limit(5).all())
    session.close()
    return result

# 2. Знайти студента із найвищим середнім балом з певного предмета
def select_2(subject_name: str) -> list:
    session = SessionLocal()
    result = (session.query(
        Student.fullname,
        func.avg(Grade.grade).label('avg_grade'))
              .join(Grade)
              .join(Grade.discipline)
              .filter(Subject.name == subject_name)
              .group_by(Student.id).order_by(func.avg(Grade.grade).desc()).first())
    session.close()
    return result

# 3. Знайти середній бал у групах з певного предмета
def select_3(subject_name: str) -> list:
    session = SessionLocal()
    result = (session.query(
        Group.name,
        func.avg(Grade.grade).label('avg_grade'))
              .join(Student, Student.group_id == Group.id)
              .join(Grade).join(Grade.discipline)
              .filter(Subject.name == subject_name)
              .group_by(Group.id).all())
    session.close()
    return result

# 4. Знайти середній бал на потоці (по всій таблиці оцінок)
def select_4() -> list:
    session = SessionLocal()
    result = session.query(func.avg(Grade.grade)).scalar()
    session.close()
    return result

# 5. Знайти які курси читає певний викладач
def select_5(teacher_name: str) -> list:
    session = SessionLocal()
    result = (session.query(Subject.name)
              .join(Subject.teacher)
              .filter(Teacher.fullname == teacher_name).all())
    session.close()
    return [r[0] for r in result]

# 6. Знайти список студентів у певній групі
def select_6(group_name:str) -> list:
    session = SessionLocal()
    result = (session.query(Student.fullname)
              .join(Student.group)
              .filter(Group.name == group_name).all())
    session.close()
    return [r[0] for r in result]

# 7. Знайти оцінки студентів у окремій групі з певного предмета
def select_7(group_name:str, subject_name: str) -> list:
    session = SessionLocal()
    result = (session.query(
        Student.fullname,
        Grade.grade)
              .join(Student.group)
              .join(Grade)
              .join(Grade.discipline)
              .filter(Group.name == group_name,
                      Subject.name == subject_name)
              .all())
    session.close()
    return result

# 8. Знайти середній бал, який ставить певний викладач зі своїх предметиів
def select_8(teacher_name:str) -> list:
    session = SessionLocal()
    result = (session.query(func.avg(Grade.grade))
              .join(Grade.discipline)
              .join(Subject.teacher)
              .filter(Teacher.fullname == teacher_name).scalar())
    session.close()
    return result

# 9. Знайти список курсів, які відвідує певний студент
def select_9(student_id: int) -> list:
    session = SessionLocal()
    result = (session.query(Subject.name)
              .join(Grade)
              .filter(Grade.student_id == student_id).distinct().all())
    courses = [row.name for row in result]
    session.close()
    return courses


# 10. Список курсів, які певному студенту читає певний викладач
def select_10(student_id: int, teacher_id: int) -> list:
    session = SessionLocal()
    result = (
        session.query(Subject.name)
        .join(Grade, Grade.subjects_id == Subject.id)
        .filter(Grade.student_id == student_id, Subject.teacher_id == teacher_id)
        .distinct()
        .all()
    )
    session.close()
    return [r[0] for r in result]


print(select_1())
print(select_2('Math'))
print(select_3('Math'))
print(select_4())
print(select_5('Викладач Гордій Кибкало'))
print(select_6('Group A'))
print(select_7('Group A', 'Math'))
print(select_8('Викладач Гордій Кибкало'))
print(select_9(2))
print(select_10(2,1 ))