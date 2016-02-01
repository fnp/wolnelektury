# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from django import forms

from newtagging.admin import TaggableModelAdmin, TaggableModelForm
from catalogue.models import Tag, Book, Fragment, BookMedia, Collection, Source


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'sort_key', 'category', 'has_description',)
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('name',)

    prepopulated_fields = {'slug': ('name',), 'sort_key': ('name',)}
    radio_fields = {'category': admin.HORIZONTAL}


class MediaInline(admin.TabularInline):
    model = BookMedia
    readonly_fields = ['source_sha1']
    extra = 0


class BookAdmin(TaggableModelAdmin):
    tag_model = Tag

    list_display = ('title', 'slug', 'created_at', 'has_epub_file', 'has_html_file', 'has_description',)
    search_fields = ('title',)
    ordering = ('title',)

    inlines = [MediaInline]

    def change_view(self, request, object_id, extra_context=None):
        if 'advanced' not in request.GET:
            self.form = forms.ModelForm
            self.fields = ('title', 'description', 'gazeta_link', 'wiki_link')
            self.readonly_fields = ('title',)
        else:
            self.form = TaggableModelForm
            self.fields = None
            self.readonly_fields = ()
        return super(BookAdmin, self).change_view(request, object_id, extra_context=extra_context)


class FragmentAdmin(TaggableModelAdmin):
    tag_model = Tag

    list_display = ('book', 'anchor',)
    ordering = ('book', 'anchor',)


class CollectionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


class SourceAdmin(admin.ModelAdmin):
    list_display = ('netloc', 'name')


admin.site.register(Tag, TagAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Fragment, FragmentAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Source, SourceAdmin)
