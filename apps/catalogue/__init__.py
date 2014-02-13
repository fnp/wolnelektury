# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import logging
from django.conf import settings as settings
from catalogue.utils import AppSettings


class Settings(AppSettings):
    """Default settings for catalogue app."""
    DEFAULT_LANGUAGE = u'pol'
    # PDF needs TeXML + XeLaTeX, MOBI needs Calibre.
    DONT_BUILD = set(['pdf', 'mobi'])
    FORMAT_ZIPS = {
            'epub': 'wolnelektury_pl_epub',
            'pdf': 'wolnelektury_pl_pdf',
            'mobi': 'wolnelektury_pl_mobi',
            'fb2': 'wolnelektury_pl_fb2',
        }

    REDAKCJA_URL = "http://redakcja.wolnelektury.pl"
    GOOD_LICENSES = set([r'CC BY \d\.\d', r'CC BY-SA \d\.\d'])

    def _more_DONT_BUILD(self, value):
        for format_ in ['cover', 'pdf', 'epub', 'mobi', 'fb2', 'txt']:
            attname = 'NO_BUILD_%s' % format_.upper()
            if hasattr(settings, attname):
                logging.warn("%s is deprecated, "
                        "use CATALOGUE_DONT_BUILD instead", attname)
                if getattr(settings, attname):
                    value.add(format_)
                else:
                    value.remove(format_)
        return value

    def _more_FORMAT_ZIPS(self, value):
        for format_ in ['epub', 'pdf', 'mobi', 'fb2']:
            attname = 'ALL_%s_ZIP' % format_.upper()
            if hasattr(settings, attname):
                logging.warn("%s is deprecated, "
                        "use CATALOGUE_FORMAT_ZIPS[%s] instead",
                            attname, format_)
                value[format_] = getattr(settings, attname)
        return value


app_settings = Settings('CATALOGUE')
