import hashlib
from django.conf import settings


class Experiment:
    slug = None
    name = 'experiment'
    explicit = False
    size = 0

    def qualify(self, request):
        return True

    def __init__(self, request):
        self.value = self.get_value(request)

    def override(self, value):
        self.value = value
        
    def get_value(self, request):
        overrides = getattr(settings, 'EXPERIMENTS_OVERRIDES', {})
        slug = self.slug
        if slug in overrides:
            return overrides[slug]

        if self.qualify(request) is False:
            return None

        cookie_value = request.COOKIES.get(f'EXPERIMENT_{slug}')
        if cookie_value is not None:
            if cookie_value == 'on':
                return True
            elif cookie_value == 'off':
                return False

        number = int(
            hashlib.md5(
                (slug + request.META['REMOTE_ADDR']).encode('utf-8')
            ).hexdigest(),
            16
        ) % 10e6 / 10e6
        return number < self.size
