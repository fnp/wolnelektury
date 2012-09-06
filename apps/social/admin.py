# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from social.models import Cite


class CiteAdmin(admin.ModelAdmin):
    list_display = ['text', 'sticky', 'vip', 'small', 'has_image']
    fieldsets = (
        (None, {'fields': ('book', 'text', 'small', 'vip', 'link', 'sticky')}),
        (
            _('Background'),
            {'fields': ('image', 'image_title', 'image_author',
                'image_link', 'image_license', 'image_license_link')
                }
            )
    )

    def has_image(self, cite):
        return bool(cite.image)
    has_image.description = _('image')
    has_image.boolean = True


admin.site.register(Cite, CiteAdmin)
