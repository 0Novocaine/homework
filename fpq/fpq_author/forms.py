from datetime import datetime

from django.forms import CharField, DateField, DateInput, ModelForm, \
    Textarea, TextInput

from fpq_core.forms import FormHelper
from .models import Author


FORMAT = '%B %d, %Y'


class CreationForm(FormHelper, ModelForm):
    name = CharField(
        min_length=10,
        max_length=50,
        required=True,
        widget=TextInput(FormHelper.attributes('name')),
    )

    born_date = DateField(
        required=True,

        widget=DateInput(
            attrs={
                **FormHelper.attributes('born-date'),
                'placeholder': (
                    'E.g.: '
                    f'{datetime.now().date().strftime(FORMAT)}'
                ),
            },
            format=FORMAT,
        ),
    )

    born_location = CharField(
        min_length=10,
        max_length=100,
        required=True,
        widget=TextInput(FormHelper.attributes('born-location')),
    )

    bio = CharField(
        min_length=30,
        required=True,
        widget=Textarea(FormHelper.attributes('bio')),
    )

    class Meta:
        model = Author
        fields = ('name', 'born_date', 'born_location', 'bio')
