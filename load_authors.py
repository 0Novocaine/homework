import json
from models import Author
from connect import connect_db

connect_db()


with open("authors.json", "r", encoding="utf-8") as f:
    authors = json.load(f)

for author in authors:
    Author(
        fullname=author["fullname"],
        born_date=author["born_date"],
        born_location=author["born_location"],
        description=author["description"],
    ).save()

print("Authors loaded")