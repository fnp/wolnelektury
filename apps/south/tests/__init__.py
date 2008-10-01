
from django.conf import settings

try:
    skiptest = settings.SKIP_SOUTH_TESTS
except:
    skiptest = False

if not skiptest:
    from south.tests.db import *
    from south.tests.logic import *