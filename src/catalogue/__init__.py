# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import logging
from django.conf import settings
from django.utils.module_loading import import_string
from catalogue.utils import AppSettings


default_app_config = 'catalogue.apps.CatalogueConfig'


class Settings(AppSettings):
    """Default settings for catalogue app."""
    DEFAULT_LANGUAGE = 'pol'
    # PDF needs TeXML + XeLaTeX, MOBI needs Calibre.
    DONT_BUILD = {'pdf', 'mobi'}

    REDAKCJA_URL = "http://redakcja.wolnelektury.pl"
    GOOD_LICENSES = {r'CC BY \d\.\d', r'CC BY-SA \d\.\d'}
    RELATED_RANDOM_PICTURE_CHANCE = .5
    GET_MP3_LENGTH = 'catalogue.utils.get_mp3_length'

    def _more_GET_MP3_LENGTH(self, value):
        return import_string(value)


app_settings = Settings('CATALOGUE')
