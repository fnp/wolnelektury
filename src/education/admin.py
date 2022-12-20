from django.contrib import admin
from . import models


admin.site.register(models.Course)
admin.site.register(models.Track)
admin.site.register(models.Tag)
admin.site.register(models.Item)
admin.site.register(models.YPlaylist)
admin.site.register(models.YouTubeToken)

# Register your models here.
