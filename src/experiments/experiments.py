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

        if re.search(
                'iphone|mobile|androidtouch',
                request.META.get('HTTP_USER_AGENT', ''),
                re.IGNORECASE):
            return False


experiments = [
    NewLayout,
]
