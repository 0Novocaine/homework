from django.db.models import CharField, DateField, Model, TextField


class Author(Model):
    name = CharField(
        null=False,
        unique=True,
        max_length=50,
    )

    born_date = DateField(null=False)
    born_location = CharField(null=False, max_length=100)
    bio = TextField(null=False)

    def __str__(self) -> str:
        return self.name
