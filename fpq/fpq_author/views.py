from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from fpq_core.views import FormView
from .forms import CreationForm
from .models import Author


class CreationView(FormView):
    template_name = 'fpq_author/create.html'
    form_class = CreationForm

    def _guest(self) -> bool:
        return True


def detail(request: WSGIRequest, author_id: int) -> HttpResponse:
    author = get_object_or_404(Author, pk=author_id)

    return render(request, 'fpq_author/detail.html', {'author': author})
