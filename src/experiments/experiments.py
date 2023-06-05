import re
from django.conf import settings
from django.utils.translation import get_language
from .base import Experiment


class NewLayout(Experiment):
    slug = 'layout'
    name = 'Nowy layout strony'
    size = settings.EXPERIMENTS_LAYOUT

    def qualify(self, request):
        if get_language() != 'pl':
            return False


class Sowka(Experiment):
    slug = 'sowka'
    name = 'Pan Sówka'
    size = settings.EXPERIMENTS_SOWKA
    switchable = False


class Search(Experiment):
    slug = 'search'
    name = 'Nowa wyszukiwarka'
    size = settings.EXPERIMENTS_SEARCH


experiments = [
    NewLayout,
    Sowka,
    Search
]
