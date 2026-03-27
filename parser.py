from typing import Any

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

BASE_URL = "http://quotes.toscrape.com/"

session = requests.Session()


def get_soup(url):
    """

    :param url:
    :return soup:
    """
    r = session.get(url)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def parse_quotes_page(url) -> tuple[list[Any], set[Any], str | None]:
    """
    Parse the quotes page and return a tuple of (author, quote, url).
    :param url:
    :return author, quote, url:
    """
    soup = get_soup(url)
    quotes_data = []
    author_links = set()
    records = soup.find_all("div", class_="quote")

    for record in records:
        quote = record.find("span", class_="text").text
        author = record.find("small", class_="author").text
        tags = [t.text for t in record.find_all("a", class_="tag")]
        href = record.find("a")["href"]
        author_links.add(urljoin(BASE_URL, href))
        quotes_data.append({
            "quote": quote,
            "author": author,
            "tags": tags
        })

    next_btn = soup.find("li", class_="next")
    next_page = (
        urljoin(BASE_URL, next_btn.find("a")["href"])
        if next_btn else None
    )

    return quotes_data, author_links, next_page


def parse_author_page(url) -> dict[str, str]:
    """

    :param url:
    :return dict[str, str]:
    """
    soup = get_soup(url)

    return {
        "fullname": soup.find("h3", class_="author-title").text.strip(),
        "born_date": soup.find("span", class_="author-born-date").text.strip(),
        "born_location": soup.find("span", class_="author-born-location").text.strip(),
        "description": soup.find("div", class_="author-description").text.strip()
    }


def crawl() -> tuple[list[Any], list[Any]]:
    """

    :return tuple[list[Any], list[Any], list[Any]]:
    """
    url = BASE_URL
    all_quotes = []
    author_urls = set()
    authors_cache = {}

    while url:
        quotes, authors, url = parse_quotes_page(url)
        all_quotes.extend(quotes)
        author_urls.update(authors)

    for a_url in author_urls:
        authors_cache[a_url] = parse_author_page(a_url)

    return all_quotes, list(authors_cache.values())


def save_json(quotes, authors):
    """

    :param quotes:
    :param authors:
    :return None:
    """
    with open("quotes.json", "w", encoding="utf-8") as f:
        json.dump(quotes, f, ensure_ascii=False, indent=4)

    with open("authors.json", "w", encoding="utf-8") as f:
        json.dump(authors, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    quotes, authors = crawl()
    save_json(quotes, authors)