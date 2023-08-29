# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#

from modeltranslation.translator import translator, TranslationOptions
from . import models


class NewsletterTranslationOptions(TranslationOptions):
    fields = ['page_title']


translator.register(models.Newsletter, NewsletterTranslationOptions)
