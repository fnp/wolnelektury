
def extra_settings(request):
    from django.conf import settings
    return {
        'STATIC_URL': settings.STATIC_URL,
    }
