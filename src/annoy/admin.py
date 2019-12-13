from django.contrib import admin
from django import forms
from modeltranslation.admin import TranslationAdmin
from . import models


class BannerAdmin(TranslationAdmin):
    list_display = ['place', 'text', 'priority', 'since', 'until', 'show_members', 'staff_preview']

    
admin.site.register(models.Banner, BannerAdmin)


class DynamicTextInsertTextInline(admin.TabularInline):
    model = models.DynamicTextInsertText
    fields = ['text', 'image', 'background_color', 'text_color']


class DynamicTextInsertAdmin(admin.ModelAdmin):
    list_display = ['paragraphs']
    inlines = [DynamicTextInsertTextInline]


admin.site.register(models.DynamicTextInsert, DynamicTextInsertAdmin)
