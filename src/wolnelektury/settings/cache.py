# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            '127.0.0.1:11211',
        ]
    },
    'ssify': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'TIMEOUT': None,
        'KEY_PREFIX': 'ssify',
        'LOCATION': [
            '127.0.0.1:11211',
        ],
    },
    'template_fragments': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'TIMEOUT': 86400,
        'LOCATION': [
            '127.0.0.1:11211',
        ],
    },
}

CACHE_MIDDLEWARE_SECONDS = 24 * 60 * 60
