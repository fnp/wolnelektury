# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin

from modeltranslation.admin import TranslationAdmin
from infopages.models import InfoPage


class InfoPageAdmin(TranslationAdmin):
    list_display = ('title', 'slug', 'main_page')

admin.site.register(InfoPage, InfoPageAdmin)
