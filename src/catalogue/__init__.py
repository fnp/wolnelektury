# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import logging
from catalogue.utils import AppSettings


class Settings(AppSettings):
    """Default settings for catalogue app."""
    DEFAULT_LANGUAGE = 'pol'
    # PDF needs TeXML + XeLaTeX, MOBI needs Calibre.
    DONT_BUILD = {'pdf', 'mobi'}


app_settings = Settings('CATALOGUE')
