# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#

from modeltranslation.translator import translator, TranslationOptions
from . import models


class OfferTranslationOptions(TranslationOptions):
    fields = ('description',)


translator.register(models.Offer, OfferTranslationOptions)


class PerkTranslationOptions(TranslationOptions):
    fields = ('name', 'long_name')


translator.register(models.Perk, PerkTranslationOptions)
