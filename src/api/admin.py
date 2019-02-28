from django.contrib import admin
from . import models


class TokenAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']


admin.site.register(models.Nonce)
admin.site.register(models.Consumer)
admin.site.register(models.Token, TokenAdmin)
