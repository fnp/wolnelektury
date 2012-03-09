from django.conf import settings

def extra_settings(request):
    return {
        'STATIC_URL': settings.STATIC_URL,
    }
