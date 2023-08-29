# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#

from modeltranslation.translator import translator, TranslationOptions
from .models import ReminderEmail


class ReminderEmailTranslationOptions(TranslationOptions):
    fields = ('subject', 'body')

translator.register(ReminderEmail, ReminderEmailTranslationOptions)
