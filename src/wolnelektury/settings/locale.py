# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from os import path
from .paths import PROJECT_DIR

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True

LOCALE_PATHS = [
    path.join(PROJECT_DIR, 'locale-contrib')
]

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pl'


def gettext(s):
    return s

LANGUAGES = tuple(sorted([
    ('pl', u'polski'),
    ('de', u'Deutsch'),
    ('en', u'English'),
    ('lt', u'lietuvių'),
    ('fr', u'français'),
    ('ru', u'русский'),
    ('es', u'español'),
    ('uk', u'українська'),
    # ('jp', u'日本語'),
    ('it', u'italiano'),
], key=lambda x: x[0]))
