# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#

from modeltranslation.translator import translator, TranslationOptions
from chunks.models import Chunk, MenuItem


class ChunkTranslationOptions(TranslationOptions):
    fields = ('content',)

translator.register(Chunk, ChunkTranslationOptions)


class MenuItemTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(MenuItem, MenuItemTranslationOptions)
