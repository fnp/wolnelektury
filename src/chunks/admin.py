# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.contrib import admin
from django import forms
from chunks import models
from modeltranslation.admin import TranslationStackedInline


class ChunkAdmin(admin.ModelAdmin):
    list_display = ('key', 'description',)
    search_fields = ('key', 'content',)

admin.site.register(models.Chunk, ChunkAdmin)


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('key',)
    search_fields = ('key',)

admin.site.register(models.Attachment, AttachmentAdmin)


class MenuItemInline(TranslationStackedInline):
    model = models.MenuItem
    extra = 1


@admin.register(models.Menu)
class MenuAdmin(admin.ModelAdmin):
    inlines = [MenuItemInline]
