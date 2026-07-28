from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.forms import CharField, EmailField, EmailInput, PasswordInput, \
    TextInput

from fpq_core.forms import FormHelper


USERNAME = {'min_length': 3, 'max_length': 16, 'required': True}


class LoginForm(AuthenticationForm):
    username = CharField(
        widget=TextInput(FormHelper.attributes('username')),
        **USERNAME,
    )

    password = CharField(
        required=True,
        widget=PasswordInput(FormHelper.attributes('password')),
    )

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)

        FormHelper.validate(self)

    class Meta:
        model = User
        fields = ('username', 'password')


class RegisterForm(UserCreationForm):
    username = CharField(
        widget=TextInput(FormHelper.attributes('username')),
        **USERNAME,
    )

    email = EmailField(
        min_length=7,
        max_length=40,
        required=True,
        widget=EmailInput(FormHelper.attributes('email')),
    )

    password1 = CharField(
        required=True,
        widget=PasswordInput(FormHelper.attributes('password')),
    )

    password2 = CharField(
        required=True,
        widget=PasswordInput(FormHelper.attributes('confirm-password')),
    )

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)

        FormHelper.validate(self)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
