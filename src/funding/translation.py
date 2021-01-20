# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#

from modeltranslation.translator import translator, TranslationOptions
from . import models


class OfferTranslationOptions(TranslationOptions):
    fields = ('description',)


translator.register(models.Offer, OfferTranslationOptions)


class PerkTranslationOptions(TranslationOptions):
    fields = ('name', 'long_name')


translator.register(models.Perk, PerkTranslationOptions)
