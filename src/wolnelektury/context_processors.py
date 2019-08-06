# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings


def extra_settings(request):
    return {
        'STATIC_URL': settings.STATIC_URL,
        'FULL_STATIC_URL': request.build_absolute_uri(settings.STATIC_URL),
        'USE_OPENID': getattr(settings, 'USE_OPENID', False)
    }
