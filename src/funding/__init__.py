# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings as settings
from catalogue.utils import AppSettings


class Settings(AppSettings):
    """Default settings for funding app."""
    DEFAULT_LANGUAGE = u'pl'
    DEFAULT_AMOUNT = 20
    MIN_AMOUNT = 1
    DAYS_NEAR = 2


app_settings = Settings('FUNDING')
