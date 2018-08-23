# -*- coding: utf-8 -*-
# Django settings for wolnelektury project.
from .apps import *
from .basic import *
from .auth import *
from .cache import *
from .celery import *
from .contrib import *
from .custom import *
from .locale import *
from .static import *
from .paths import *

# Load localsettings, if they exist
try:
    from wolnelektury.localsettings import *
except ImportError:
    pass
