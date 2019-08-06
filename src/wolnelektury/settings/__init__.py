# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
# Django settings for wolnelektury project.
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

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


try:
    SENTRY_DSN
except NameError:
    pass
else:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )
