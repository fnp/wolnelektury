from django.contrib import admin
from . import models


@admin.register(models.Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ['uuid', 'created_at', 'user', 'book', 'anchor']
    raw_id_fields = ['book', 'user']


@admin.register(models.Quote)
class BookmarkAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ['uuid', 'created_at', 'user', 'book', 'start_elem']
    raw_id_fields = ['book', 'user']
