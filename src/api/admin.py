# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from . import models


class TokenAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']


admin.site.register(models.Nonce)
admin.site.register(models.Consumer)
admin.site.register(models.Token, TokenAdmin)
