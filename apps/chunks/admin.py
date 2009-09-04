from django.contrib import admin

from chunks.models import Chunk, Attachment


class ChunkAdmin(admin.ModelAdmin):
    list_display = ('key', 'description',)
    search_fields = ('key', 'content',)

admin.site.register(Chunk, ChunkAdmin)


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('key',)
    search_fields = ('key',)

admin.site.register(Attachment, AttachmentAdmin)