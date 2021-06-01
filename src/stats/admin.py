from django.contrib import admin
from . import models


class VisitsAdmin(admin.ModelAdmin):
    list_display = ['book', 'date', 'views', 'unique_views']
    raw_id_fields = ['book']
    date_hierarchy = 'date'



admin.site.register(models.Visits, VisitsAdmin)
