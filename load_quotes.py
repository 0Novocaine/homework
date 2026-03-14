import json
from models import Author, Quote
from connect import connect_db

connect_db()


with open("quotes.json", "r", encoding="utf-8") as f:
    quotes = json.load(f)

for quote in quotes:
    author = Author.objects(fullname=quote["author"]).first()

    Quote(
        tags=quote["tags"],
        author=author,
        quote=quote["quote"]
    ).save()

print("Quotes loaded")