# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from social.models import Cite


class CiteAdmin(admin.ModelAdmin):
    list_display = ['nonempty_text', 'sticky', 'vip', 'small', 'has_image']
    fieldsets = (
        (None, {'fields': ('book', 'text', 'small', 'vip', 'link', 'sticky')}),
        (
            _('Background'),
            {'fields': ('image', 'image_shift', 'image_title', 'image_author',
                'image_link', 'image_license', 'image_license_link')
                }
            )
    )

    def nonempty_text(self, cite):
        if cite.text.strip():
            return cite.text
        return "(%s)" % (cite.image_title.strip() or cite.link)
    nonempty_text.short_description = _('text')

    def has_image(self, cite):
        return bool(cite.image)
    has_image.short_description = _('image')
    has_image.boolean = True


admin.site.register(Cite, CiteAdmin)
