from django.contrib import admin
from django.contrib.sites.models import Site
from . import models


class RedirectAdmin(admin.ModelAdmin):
    list_display = ['slug', 'url', 'counter', 'created_at', 'full_url']
    readonly_fields = ['counter', 'created_at', 'full_url']
    fields = ['slug', 'url', 'counter', 'created_at', 'full_url']

    def full_url(self, obj):
        site = Site.objects.get_current()
        url = obj.get_absolute_url()
        return f'https://{site.domain}{url}'


admin.site.register(models.Redirect, RedirectAdmin)
