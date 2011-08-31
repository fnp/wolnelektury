import os.path
from django.conf import settings


try:
    MOBILE_INIT_DB = settings.API_MOBILE_INIT_DB
except AttributeError:
    MOBILE_INIT_DB = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'api/mobile/initial/'))
