from django.db.models import CASCADE, CharField, ForeignKey, ManyToManyField, \
    Model, UniqueConstraint

from fpq_author.models import Author
from fpq_tag.models import Tag


class Quote(Model):
    author = ForeignKey(Author, CASCADE)
    phrase = CharField(max_length=1300, null=False)
    tags = ManyToManyField(Tag, related_name='quotes')

    def __str__(self) -> str:
        return self.phrase

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'phrase'],
                name='Quote of author',
            ),
        ]
