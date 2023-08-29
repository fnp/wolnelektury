# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
# Django settings for wolnelektury project.
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .apps import *
from .basic import *
from .auth import *
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


# If Celery broker not configured, enable always-eager mode.
try:
    CELERY_BROKER_URL
except NameError:
    CELERY_TASK_ALWAYS_EAGER = True


try:
    SENTRY_DSN
except NameError:
    pass
else:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )


# Dummy secret key for development.
try:
    SECRET_KEY
except NameError:
    if DEBUG:
        SECRET_KEY = 'not-a-secret-key'
