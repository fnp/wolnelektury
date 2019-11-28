import hashlib
from django.conf import settings


def context_processor(request):
    ab = {}
    overrides = getattr(settings, 'AB_TESTS_OVERRIDES', {})
    for abtest, nvalues in settings.AB_TESTS.items():
        ab[abtest] = overrides.get(
            abtest,
            hashlib.md5(
                (abtest + request.META['REMOTE_ADDR']).encode('utf-8')
            ).digest()[0] % nvalues
        )
    return {'AB': ab}
