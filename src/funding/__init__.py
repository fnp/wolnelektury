# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.conf import settings as settings
from catalogue.utils import AppSettings


class Settings(AppSettings):
    """Default settings for funding app."""
    DEFAULT_LANGUAGE = 'pl'
    DEFAULT_AMOUNT = 20
    MIN_AMOUNT = 1
    DAYS_NEAR = 2
    PAYU_POS = '300746'


app_settings = Settings('FUNDING')
