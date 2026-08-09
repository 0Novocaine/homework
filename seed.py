from faker import Faker

from src.database.db import SessionLocal
from src.database.models import Contact
from datetime import datetime

fake = Faker("uk_UA")

db = SessionLocal()

start = datetime.strptime("1999-08-10", "%Y-%m-%d")
end = datetime.strptime("1999-08-20", "%Y-%m-%d")

try:
    contacts = [
        Contact(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=fake.phone_number(),
            birthday=fake.date_between_dates(start, end),
            # birthday=fake.date_of_birth(minimum_age=18, maximum_age=80),
            additional_data=fake.sentence(),
        )
        for _ in range(20)
    ]

    db.add_all(contacts)
    db.commit()
finally:
    db.close()