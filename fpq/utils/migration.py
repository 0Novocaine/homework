from os import environ

from django import setup
from dotenv import load_dotenv


load_dotenv()
setup()


from mongoengine import connect, Document # noqa
from mongoengine.connection import ConnectionFailure # noqa
from mongoengine.fields import DateField, ListField, ReferenceField, \
    StringField # noqa
from pymongo.errors import ConfigurationError # noqa

from fpq_author.models import Author as TargetAuthor # noqa
from fpq_quote.models import Quote as TargetQuote # noqa
from fpq_tag.models import Tag # noqa


class Author(Document):
    fullname = StringField(max_length=50, required=True)
    born_date = DateField(required=True)
    born_location = StringField(max_length=100, required=True)
    description = StringField(required=True)
    meta = {'collection': 'authors'}


class Quote(Document):
    tags = ListField(StringField(max_length=30), required=True)
    author = ReferenceField('Author', required=True)
    quote = StringField(required=True)
    meta = {'collection': 'quotes'}


try:
    connect(
        db=environ['MONGODB_DATABASE'],
        host=environ['MONGODB_URL'],
        tls=True,
        tlsAllowInvalidCertificates=True,
    )
except (ConfigurationError, ConnectionFailure):
    raise Exception('Invalid credentials.')

authors = {
    author.id: TargetAuthor.objects.get_or_create(
        name=author.fullname,
        born_date=author.born_date,
        born_location=author.born_location,
        bio=author.description,
    )[0]
    for author in Author.objects()
}

for source_quote in Quote.objects():
    target_quote, _ = TargetQuote.objects.get_or_create(
        author=authors[source_quote.author.id],
        phrase=source_quote.quote,
    )

    for tag in source_quote.tags:
        target_quote.tags.add(Tag.objects.get_or_create(name=tag)[0])
