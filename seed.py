"""Create a test user and 20 contacts owned by that user."""

from datetime import date, timedelta

from faker import Faker

from src.database.db import SessionLocal
from src.database.models import Contact, User
from src.services.auth import auth_service

SEED_EMAIL = "seed@example.com"
SEED_PASSWORD = "seedpassword"
CONTACTS_TO_CREATE = 20

fake = Faker("uk_UA")
db = SessionLocal()

try:
    user = db.query(User).filter(User.email == SEED_EMAIL).first()
    if user is None:
        user = User(
            username="seed_user",
            email=SEED_EMAIL,
            password=auth_service.get_password_hash(SEED_PASSWORD),
        )
        db.add(user)
        db.flush()

    if db.query(Contact).filter(Contact.user_id == user.id).count() == 0:
        today = date.today()
        contacts = []
        for day_offset in range(CONTACTS_TO_CREATE):
            birthday = today + timedelta(days=day_offset % 8)
            contacts.append(
                Contact(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.unique.email(),
                    phone=fake.phone_number(),
                    birthday=birthday.replace(year=1990),
                    additional_data=fake.sentence(),
                    user=user,
                )
            )
        db.add_all(contacts)
        db.commit()
        print(f"Created {CONTACTS_TO_CREATE} contacts for {SEED_EMAIL}.")
    else:
        db.commit()
        print(f"Contacts for {SEED_EMAIL} already exist; nothing was added.")

    print(f"Login: {SEED_EMAIL} / {SEED_PASSWORD}")
finally:
    db.close()
