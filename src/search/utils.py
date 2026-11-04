from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchVector


# Deprecated
UnaccentSearchQuery = SearchQuery


def UnaccentSearchVector(expression):
    return SearchVector(expression, config=settings.SEARCH_CONFIG)
