import hashlib
from django.conf import settings


def context_processor(request):
    ab = {}
    for abtest, nvalues in settings.AB_TESTS.items():
        print(abtest, nvalues)
        ab[abtest] = hashlib.md5(
                (abtest + request.META['REMOTE_ADDR']).encode('utf-8')
            ).digest()[0] % nvalues
    print(ab)
    return {'AB': ab}
