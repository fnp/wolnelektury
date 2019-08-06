# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#

from modeltranslation.translator import translator, TranslationOptions
from chunks.models import Chunk


class ChunkTranslationOptions(TranslationOptions):
    fields = ('content',)

translator.register(Chunk, ChunkTranslationOptions)
