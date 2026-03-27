from models import Author, Quote
from connect import connect_db

connect_db()


def print_help():
    """
    Display help message
    :return:
    """
    print("""
Available commands:

help            -   show this help message
exit            -   exit program

name:<name>     -   find quotes by author name
tag:<tag>       -   find quotes by single tag
tags:<t1,t2>    -   find quotes by multiple tags

all_quotes      -   show all quotes
all_authors     -   show all  authors
all_tags        -   show all unique tags
""")


def print_all_quotes():
    """
    Display all quotes
    :return:
    """
    for q in Quote.objects:
        print(f"{q.author.fullname}: {q.quote}")


def print_all_authors():
    """
    Display all authors
    :return:
    """
    for a in Author.objects:
        print(a.fullname)


def print_all_tags():
    """
    Display all unique tags
    :return:
    """
    tags = set()
    for q in Quote.objects:
        tags.update(q.tags)
    for t in sorted(tags):
        print(t)


while True:
    command = input(">>> ").strip()

    if command == "exit":
        break

    if command == "help":
        print_help()

    elif command == "all_quotes":
        print_all_quotes()

    elif command == "all_authors":
        print_all_authors()

    elif command == "all_tags":
        print_all_tags()

    elif command.startswith("name:"):
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