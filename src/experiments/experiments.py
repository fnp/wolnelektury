import re
from .base import Experiment


class NewLayout(Experiment):
    slug = 'layout'
    name = 'Nowy layout strony'

    def qualify(self, request):
        if re.search(
                'iphone|mobile|androidtouch',
                request.META['HTTP_USER_AGENT'],
                re.IGNORECASE):
            return False


experiments = [
    NewLayout,
]
