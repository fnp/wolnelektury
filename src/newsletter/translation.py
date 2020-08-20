# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#

from modeltranslation.translator import translator, TranslationOptions
from . import models


class NewsletterTranslationOptions(TranslationOptions):
    fields = ['page_title']


translator.register(models.Newsletter, NewsletterTranslationOptions)
