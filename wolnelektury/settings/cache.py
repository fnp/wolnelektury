from os import path
from .paths import PROJECT_DIR

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            '127.0.0.1:11211',
        ]
    },
    'permanent': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'TIMEOUT': 2419200,
        'LOCATION': [
            '127.0.0.1:11211',
        ]
    },
    'api': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': path.join(PROJECT_DIR, '../django_cache/'),
        'KEY_PREFIX': 'api',
        'TIMEOUT': 86400,
    },
}
