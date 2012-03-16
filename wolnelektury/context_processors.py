from django.conf import settings

def extra_settings(request):
    return {
        'STATIC_URL': settings.STATIC_URL,
        'FULL_STATIC_URL': request.build_absolute_uri(settings.STATIC_URL)
    }
