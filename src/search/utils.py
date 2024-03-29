from django.conf import settings
from django.db.models import Func
from django.contrib.postgres.search import SearchQuery, SearchVectorField


class UnaccentSearchQuery(SearchQuery):
    '''
    The idea is to run unaccent *after* the query is already passed through the language dictionary.
    '''
    def as_sql(self, *args, **kwargs):
        sql, params = super().as_sql(*args, **kwargs)
        if settings.SEARCH_USE_UNACCENT:
            sql = f'unaccent({sql}::text)::tsquery'
        return sql, params


class UnaccentSearchVector(Func):
    '''
    We do the indexing twice, to account for non-diacritic versions.
    For example: user enters 'róże' -> stem to 'róża' -> unaccent to 'roza'.
    But user enters 'roze' -> stem leaves it as is, so we need original form in the vector.
    '''
    function='to_tsvector'
    if settings.SEARCH_USE_UNACCENT:
        template = f'''unaccent(
        %(function)s('{settings.SEARCH_CONFIG}', %(expressions)s)::text)::tsvector ||
        to_tsvector(
        '{settings.SEARCH_CONFIG_SIMPLE}', 
        unaccent(%(expressions)s)
        )'''
    output_field = SearchVectorField()
