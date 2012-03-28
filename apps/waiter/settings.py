from os.path import join
from django.conf import settings

try:
    WAITER_ROOT = settings.WAITER_ROOT
except AttributeError:
    WAITER_ROOT = join(settings.MEDIA_ROOT, 'waiter')

try:
    WAITER_URL = settings.WAITER_URL
except AttributeError:
    WAITER_URL = join(settings.MEDIA_URL, 'waiter')

try:
    WAITER_MAX_QUEUE = settings.WAITER_MAX_QUEUE
except AttributeError:
    WAITER_MAX_QUEUE = 20

