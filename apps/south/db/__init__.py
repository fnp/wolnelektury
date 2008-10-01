
# Establish the common DatabaseOperations instance, which we call 'db'.
# This code somewhat lifted from django evolution
from django.conf import settings
import sys
module_name = ['south.db', settings.DATABASE_ENGINE]
try:
    module = __import__('.'.join(module_name),{},{},[''])
except ImportError:
    sys.stderr.write("There is no South database module for the engine '%s'. Please either choose a supported one, or remove South from INSTALLED_APPS.\n" % settings.DATABASE_ENGINE)
    sys.exit(1)
db = module.DatabaseOperations()