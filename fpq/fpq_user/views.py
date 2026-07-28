from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import redirect

from fpq_core.views import FormView
from .forms import RegisterForm


class RegisterView(FormView):
    template_name = 'fpq_user/register.html'
    form_class = RegisterForm

    def _guest(self) -> bool:
        return False


@login_required
def signout(request: WSGIRequest) -> HttpResponsePermanentRedirect:
    logout(request)

    return redirect('fpq_core:index')
