from django.contrib import admin

from libraries.models import Library, Catalog


admin.site.register(Catalog)
admin.site.register(Library)
