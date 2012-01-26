# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin

from social.models import Cite


class CiteAdmin(admin.ModelAdmin):
    list_display = ['text', 'vip', 'small']


admin.site.register(Cite, CiteAdmin)
