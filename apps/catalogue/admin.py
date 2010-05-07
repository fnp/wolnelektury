# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin

from newtagging.admin import TaggableModelAdmin
from catalogue.models import Tag, Book, Fragment, BookStub


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'sort_key', 'category', 'has_description', 'main_page',)
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('name',)

    prepopulated_fields = {'slug': ('name',), 'sort_key': ('name',),}
    radio_fields = {'category': admin.HORIZONTAL}


class BookAdmin(TaggableModelAdmin):
    tag_model = Tag
    
    list_display = ('title', 'slug', 'has_pdf_file', 'has_odt_file', 'has_html_file', 'has_description',)
    search_fields = ('title',)
    ordering = ('title',)

    prepopulated_fields = {'slug': ('title',)}


class FragmentAdmin(TaggableModelAdmin):
    tag_model = Tag
    
    list_display = ('book', 'anchor',)
    ordering = ('book', 'anchor',)


class BookStubAdmin(admin.ModelAdmin):
    # tag_model = Tag
    
    list_display = ('title', 'author', 'slug','pd')
    search_fields = ('title','author')
    ordering = ('title',)

    prepopulated_fields = {'slug': ('title',)}


admin.site.register(BookStub, BookStubAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Fragment, FragmentAdmin)

