from django.contrib import admin
from . import models


admin.site.register(models.Nonce)
admin.site.register(models.Consumer)
admin.site.register(models.Token)
