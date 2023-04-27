import re
from django.conf import settings
from django.utils.translation import get_language
from .base import Experiment


class NewLayout(Experiment):
    slug = 'layout'
    name = 'Nowy layout strony'
    size = 1 or settings.EXPERIMENTS_LAYOUT

    def qualify(self, request):
        if get_language() != 'pl':
            return False


experiments = [
    NewLayout,
]
