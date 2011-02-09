# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from django import forms

from newtagging.admin import TaggableModelAdmin
from catalogue.models import Tag, Book, Fragment, BookMedia


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'sort_key', 'category', 'has_description', 'main_page',)
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('name',)

    prepopulated_fields = {'slug': ('name',), 'sort_key': ('name',),}
    radio_fields = {'category': admin.HORIZONTAL}


class BookAdmin(TaggableModelAdmin):
    tag_model = Tag

    list_display = ('title', 'slug', 'created_at', 'has_pdf_file', 'has_epub_file', 'has_html_file', 'has_description',)
    search_fields = ('title',)
    ordering = ('title',)

    filter_horizontal = ('medias',)

    def change_view(self, request, object_id, extra_context=None):
        if not request.GET.has_key('advanced'):
            self.fields = ('title', 'description', 'gazeta_link', 'wiki_link', 'pdf_file', 'medias',)
            self.readonly_fields = ('title',)
        else:
            self.fields = None
            self.readonly_fields = ()
        return super(BookAdmin, self).change_view(request, object_id,
            extra_context=extra_context)



class FragmentAdmin(TaggableModelAdmin):
    tag_model = Tag

    list_display = ('book', 'anchor',)
    ordering = ('book', 'anchor',)



class BookMediaAdminForm(forms.ModelForm):
    books = forms.CharField(required=False)

    class Meta:
        model = BookMedia


class MediaAdmin(admin.ModelAdmin):
    form = BookMediaAdminForm

    list_display = ('name', 'type', 'book_count', 'uploaded_at')
    ordering = ('name', 'type')
    search_fields = ('name',)
    fields = ('type', 'name', 'file', 'books')
    readonly_fields = ('books',)



admin.site.register(Tag, TagAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Fragment, FragmentAdmin)
admin.site.register(BookMedia, MediaAdmin)
