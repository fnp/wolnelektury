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
}

CACHE_MIDDLEWARE_SECONDS = 24 * 60 * 60
