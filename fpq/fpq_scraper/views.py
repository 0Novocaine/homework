from collections import defaultdict
from datetime import datetime
from logging import basicConfig, INFO, info
from re import search, sub

from bs4 import BeautifulSoup
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from requests import get

from fpq_author.models import Author
from fpq_quote.models import Quote
from fpq_tag.models import Tag


def author_key(name: str) -> str:
    return sub(r'\W', '', name)


def scrape(path: str) -> BeautifulSoup | None:
    path = 'https://quotes.toscrape.com' + path

    info(f'Parsing {path}')

    response = get(path)

    return BeautifulSoup(response.text, 'lxml') \
        if response.status_code == 200 else None


def scraping(request: WSGIRequest) -> HttpResponse:
    if request.user.is_anonymous:
        return redirect('fpq_core:index')

    basicConfig(level=INFO, format='%(message)s')

    ATTRIBUTES = {
        field: {key: field for key in ('class', 'itemprop')}
        for field in ('author', 'text')
    }

    results = defaultdict(list)
    path = '/'

    while (page := scrape(path)):
        nodes = page.find_all(
            'div',
            {
                'class': 'quote',
                'itemtype': 'http://schema.org/CreativeWork'
            },
        )

        for quote in nodes:
            phrase = quote.find('span', ATTRIBUTES['text'])

            wrapper = phrase.find_next_sibling('span')
            author_name = wrapper.find('small', ATTRIBUTES['author']).text
            author_link = wrapper.select('a[href^="/author/"]')[0]

            author_info = f'by {author_name}{author_link.text}'

            if wrapper.text.replace('\n', '') != author_info:
                continue

            results['authors'].append(author_link['href'])

            tags = quote.find('div', class_='tags') \
                .select('a.tag[href^="/tag/"]')

            results['quotes'].append({
                'tags': [tag.text for tag in tags],
                'author': author_name,
                'quote': phrase.text,
            })

        if (not (
            (nodes := page.select('nav > ul.pager > li.next > a')) and
            search(r'^/page/\d+/$', path := nodes[0]['href'])
        )):
            break

    paths = set(results['authors'])
    results['authors'] = []

    for path in paths:
        if not (page := scrape(path)):
            continue

        wrapper = page.find('div', class_='author-details')
        author = {}

        for name in ('title', 'born-date', 'born-location', 'description'):
            value = wrapper.select(f'.author-{name}')[0].text.strip()

            if name == 'born-date':
                value = datetime.strptime(value, '%B %d, %Y').date()
            elif name == 'born-location':
                value = value[3:]

            match name:
                case 'title': field = 'name'
                case 'description': field = 'bio'
                case _: field = name.replace('-', '_')

            author[field] = value

        results['authors'].append(author)

    authors = {}

    counts = defaultdict(int)

    for source_author in results['authors']:
        target_author, created = Author.objects.get_or_create(**source_author)
        authors[author_key(source_author['name'])] = target_author

        if created:
            counts['authors'] += 1

    for source_quote in results['quotes']:
        target_quote, created = Quote.objects.get_or_create(
            author=authors[author_key(source_quote['author'])],
            phrase=source_quote['quote'],
        )

        if created:
            counts['quotes'] += 1

        for source_tag in source_quote['tags']:
            target_tag, created = Tag.objects.get_or_create(name=source_tag)
            target_quote.tags.add(target_tag)

            if created:
                counts['tags'] += 1

    for type, count in counts.items():
        info(f'Found {count} {type}.')

    return redirect('fpq_core:index')
