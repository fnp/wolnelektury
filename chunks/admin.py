from django.contrib import admin

from chunks.models import Chunk


class ChunkAdmin(admin.ModelAdmin):
  list_display = ('key',)
  search_fields = ('key', 'content')

admin.site.register(Chunk, ChunkAdmin)

