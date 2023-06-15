from django.contrib import admin
from . import models


@admin.register(models.Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ['uri', 'label']
    search_fields = ['uri', 'label']
