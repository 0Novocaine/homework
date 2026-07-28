from abc import ABC, abstractmethod
from typing import Any

from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, F, Window
from django.db.models.functions import RowNumber
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponsePermanentRedirect, QueryDict
from django.shortcuts import redirect, render
from django.views import View

from fpq_quote.models import Quote
from fpq_tag.models import Tag


Response = HttpResponse | HttpResponsePermanentRedirect


class FormView(ABC, View):
    def _context(self) -> dict:
        return dict()

    @abstractmethod
    def _guest(self) -> bool:
        ...

    def _save(
        self,
        response: QueryDict,
        form: ModelForm,
        commit: bool = True
    ) -> Any:
        return form.save(commit)

    def dispatch(self, request: WSGIRequest) -> Response:
        if request.user.is_anonymous == self._guest():
            return redirect('fpq_core:index')

        return super().dispatch(request)

    def get(self, request: WSGIRequest) -> HttpResponse:
        return render(
            request,
            self.template_name,
            {'form': self.form_class, **self._context()},
        )

    def post(self, request: WSGIRequest) -> Response:
        form = self.form_class(request.POST)

        if form.is_valid():
            self._save(request.POST, form)

            return redirect('fpq_core:index')

        return render(
            request,
            self.template_name,
            {'form': form, **self._context()},
        )


def index(request: WSGIRequest) -> HttpResponse:
    tags = Tag.objects.annotate(
        usages=Count('quotes'),
        row_number=Window(
            RowNumber(),
            order_by=(F('usages').desc(), F('name').asc()),
        ),
    ).filter(row_number__lte=10)

    context = {'tags': tags}

    query = Quote.objects

    if (tag_id := request.GET.get('tag')):
        context['current_tag'] = Tag.objects.filter(pk=tag_id).first()

        if context['current_tag']:
            query = query.filter(tags=tag_id)

    context['quotes'] = query.all()

    paginator = Paginator(range(len(context['quotes'])), size := 10)
    page = request.GET.get('page', 1)

    offset = size * (int(page) - 1)
    context['quotes'] = context['quotes'][offset:offset + size]

    try:
        page = paginator.page(page)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    context['pager'] = {
        'Previous': page.previous_page_number if page.has_previous else '#',
        'Next': page.next_page_number if page.has_next else '#',
    }

    return render(request, 'fpq_core/index.html', context)
