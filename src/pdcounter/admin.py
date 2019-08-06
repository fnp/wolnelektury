# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin

from pdcounter.models import BookStub, Author


class BookStubAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'slug', 'pd')
    search_fields = ('title', 'author')
    ordering = ('title',)

    prepopulated_fields = {'slug': ('title',)}


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'death')
    search_fields = ('name',)
    ordering = ('sort_key', 'name')

    prepopulated_fields = {'slug': ('name',), 'sort_key': ('name',)}


admin.site.register(BookStub, BookStubAdmin)
admin.site.register(Author, AuthorAdmin)
