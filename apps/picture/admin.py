# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from picture.models import Picture
from sorl.thumbnail.admin import AdminImageMixin

class PictureAdmin(AdminImageMixin, admin.ModelAdmin):
    pass

admin.site.register(Picture, PictureAdmin)
