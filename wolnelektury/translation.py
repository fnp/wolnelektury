# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#

from modeltranslation.translator import translator, TranslationOptions
from catalogue.models import Collection, Tag
from infopages.models import InfoPage

class InfoPageTranslationOptions(TranslationOptions):
    fields = ('title', 'left_column', 'right_column')

class TagTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'wiki_link')

class CollectionTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

translator.register(InfoPage, InfoPageTranslationOptions)
translator.register(Tag, TagTranslationOptions)
translator.register(Collection, CollectionTranslationOptions)

