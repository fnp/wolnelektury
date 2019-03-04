# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#

from modeltranslation.translator import translator, TranslationOptions
from .models import ReminderEmail


class ReminderEmailTranslationOptions(TranslationOptions):
    fields = ('subject', 'body')

translator.register(ReminderEmail, ReminderEmailTranslationOptions)
