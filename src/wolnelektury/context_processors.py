# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.conf import settings


def extra_settings(request):
    return {
        'STATIC_URL': settings.STATIC_URL,
        'FULL_STATIC_URL': request.build_absolute_uri(settings.STATIC_URL),
        'USE_OPENID': getattr(settings, 'USE_OPENID', False),
        'VARIANT': settings.VARIANTS.get(request.get_host()),
    }
