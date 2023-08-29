# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.contrib import admin
from django.db.models import TextField
from sponsors import models
from sponsors import widgets


class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


class SponsorPageAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': widgets.SponsorPageWidget},
    }
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


admin.site.register(models.Sponsor, SponsorAdmin)
admin.site.register(models.SponsorPage, SponsorPageAdmin)
