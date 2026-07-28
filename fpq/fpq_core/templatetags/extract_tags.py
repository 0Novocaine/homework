from django.template import Library

from fpq_tag.models import Tag


register = Library()


def tags(tags) -> list[Tag]:
    return tags.all()


register.filter('tags', tags)
