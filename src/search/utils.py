from django.db.models import Func
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchQueryField, SearchHeadline as SH



class UnaccentTSVector(Func):
    function = 'UNACCENT'
    template = '%(function)s(%(expressions)s::text)::tsvector'


class Unaccent(Func):
    function = 'UNACCENT'

    
class ConcatTSVector(Func):
    function = 'CONCAT'
    template = '%(function)s(%(expressions)s)::tsvector'    


class UnaccentTSQuery(Func):
    function = 'UNACCENT'
    template = '%(function)s(%(expressions)s::text)::tsquery'
    output_field = SearchQueryField()


class TSV(Func):
    function='to_tsvector'
    template = '''unaccent(
      %(function)s('polish', %(expressions)s)::text)::tsvector ||
     to_tsvector(
       'polish_simple', 
       unaccent(%(expressions)s)
     )'''


def build_search_vector(*fields):
    return TSV(*fields)


def build_search_query(*fields, **kwargs):
    return UnaccentTSQuery(SearchQuery(*fields, **kwargs))



class SearchHeadline(SH):

    def __init__(
        self,
        expression,
        query,
        *,
        config=None,
        start_sel=None,
        stop_sel=None,
        max_words=None,
        min_words=None,
        short_word=None,
        highlight_all=None,
        max_fragments=None,
        fragment_delimiter=None,
    ):
        options = {
            "StartSel": start_sel,
            "StopSel": stop_sel,
            "MaxWords": max_words,
            "MinWords": min_words,
            "ShortWord": short_word,
            "HighlightAll": highlight_all,
            "MaxFragments": max_fragments,
            "FragmentDelimiter": fragment_delimiter,
        }
        self.options = {
            option: value for option, value in options.items() if value is not None
        }
        expressions = (expression, query)
        if config is not None:
            config = SearchConfig.from_parameter(config)
            expressions = (config,) + expressions
        Func.__init__(self, *expressions)
