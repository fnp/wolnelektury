# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.contrib import admin

from modeltranslation.admin import TranslationAdmin
from infopages.models import InfoPage


class InfoPageAdmin(TranslationAdmin):
    list_display = ('title', 'slug', 'published', 'findable')

admin.site.register(InfoPage, InfoPageAdmin)
