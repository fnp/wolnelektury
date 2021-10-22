import hashlib
from django.conf import settings


def experiments_middleware(get_response):
    def middleware(request):
        exps = {}

        overrides = getattr(settings, 'EXPERIMENTS_OVERRIDES', {})
        for exp in settings.EXPERIMENTS:
            slug = exp['slug']
            if slug in overrides:
                exps[slug] = overrides[slug]
                continue

            cookie_value = request.COOKIES.get(f'EXPERIMENT_{slug}')
            if cookie_value is not None:
                for cohort in exp.get('cohorts', []):
                    if cohort['value'] == cookie_value:
                        exps[slug] = cookie_value
                        break

            if slug not in exps:
                number = int(
                    # TODO sth else?
                    hashlib.md5(
                        (slug + request.META['REMOTE_ADDR']).encode('utf-8')
                    ).hexdigest(),
                    16
                ) % 10e6 / 10e6
                for cohort in exp.get('cohorts', []):
                    number -= cohort.get('size', 1)
                    if number < 0:
                        exps[slug] = cohort['value']
                        break

        request.EXPERIMENTS = exps
        response = get_response(request)
        return response

    return middleware
