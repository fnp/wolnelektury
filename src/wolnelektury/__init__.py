# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.utils.translation import gettext

from .celery import app as celery_app

default_app_config = 'wolnelektury.apps.WLCoreConfig'

if False:
    gettext("Please enter a correct %(username)s and password. Note that both fields may be case-sensitive.")
