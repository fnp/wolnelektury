# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#

from modeltranslation.translator import translator, TranslationOptions
from infopages.models import InfoPage


class InfoPageTranslationOptions(TranslationOptions):
    fields = ('title', 'left_column', 'right_column')

translator.register(InfoPage, InfoPageTranslationOptions)
