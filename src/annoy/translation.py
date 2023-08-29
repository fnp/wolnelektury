# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from modeltranslation.translator import translator, TranslationOptions
from . import models


class BannerTranslationOptions(TranslationOptions):
    fields = ('text',)


translator.register(models.Banner, BannerTranslationOptions)
