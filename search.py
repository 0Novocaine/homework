from models import Author, Quote
from connect import connect_db

connect_db()

while True:

    command = input(">>> ")

    if command == "exit":
        break

    if command.startswith("name:"):
        name = command.replace("name:", "").strip()

        author = Author.objects(fullname=name).first()

        if author:
            quotes = Quote.objects(author=author)

            for q in quotes:
                print(q.quote)

    elif command.startswith("tag:"):
        tag = command.replace("tag:", "").strip()

        quotes = Quote.objects(tags=tag)

        for q in quotes:
            print(q.quote)

    elif command.startswith("tags:"):
        tags = command.replace("tags:", "").split(",")

        quotes = Quote.objects(tags__in=tags)

        for q in quotes:
            print(q.quote)