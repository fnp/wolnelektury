# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from catalogue.models import Tag, Book, Fragment, BookMedia, Collection, Source
from pz.admin import EmptyFieldListFilter


class BlankFieldListFilter(EmptyFieldListFilter):
    with_empty_str = True


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'sort_key', 'category', 'has_description', 'occurrences')
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('occurrences',)

    def occurrences(self, tag):
        return tag.items.count()
    occurrences.short_description = 'Wystąpienia'

    prepopulated_fields = {'slug': ('name',), 'sort_key': ('name',)}
    radio_fields = {'category': admin.HORIZONTAL}


class MediaInline(admin.TabularInline):
    model = BookMedia
    readonly_fields = ['source_sha1']
    extra = 0


class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'slug', 'created_at', 'has_epub_file', 'has_html_file', 'has_description',
    )
    list_filter = [
            'print_on_demand',
            ('wiki_link', BlankFieldListFilter),
            ('parent', EmptyFieldListFilter),
            ]
    search_fields = ('title',)
    ordering = ('title',)

    inlines = [MediaInline]


class FragmentAdmin(admin.ModelAdmin):
    list_display = ('book', 'anchor',)
    ordering = ('book', 'anchor',)


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'listed')
    prepopulated_fields = {'slug': ('title',)}


class SourceAdmin(admin.ModelAdmin):
    list_display = ('netloc', 'name')


admin.site.register(Tag, TagAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Fragment, FragmentAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Source, SourceAdmin)
