from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from lessons.models import Document


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'slideshare_id')
    list_filter = ('author',)
    search_fields = ('name', 'author',)
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Document, DocumentAdmin)
