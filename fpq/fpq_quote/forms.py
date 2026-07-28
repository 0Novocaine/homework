from django.forms import CharField, ModelForm, Textarea

from fpq_core.forms import FormHelper
from .models import Quote


class CreationForm(FormHelper, ModelForm):
    phrase = CharField(
        required=True,
        widget=Textarea(FormHelper.attributes('phrase')),
    )

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)

        self.fields['phrase'].widget.attrs['rows'] = 3

    class Meta:
        model = Quote
        fields = ('phrase',)
        exclude = ('author', 'tags')
