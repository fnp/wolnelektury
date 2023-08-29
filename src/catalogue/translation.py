# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#

from modeltranslation.translator import translator, TranslationOptions
from catalogue.models import Collection, Tag, Source


class TagTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'wiki_link')


class CollectionTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


class SourceTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Tag, TagTranslationOptions)
translator.register(Collection, CollectionTranslationOptions)
translator.register(Source, SourceTranslationOptions)
