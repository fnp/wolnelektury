# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from admin_ordering.admin import OrderableAdmin
from social.models import Cite, BannerGroup, Carousel, CarouselItem


class CiteAdmin(admin.ModelAdmin):
    list_display = ['nonempty_text', 'created_at', 'sticky', 'vip', 'small', 'has_image']
    list_filter = ['group']
    readonly_fields = ['created_at']
    fieldsets = (
        (None, {'fields': ('group', 'sticky', 'created_at')}),
        (_('Content'), {'fields': ('book', 'text', 'small', 'vip', 'link', 'video', 'picture', 'banner')}),
        (
            _('Background'),
            {'fields': (
                'image', 'image_shift', 'image_title', 'image_author',
                'image_link', 'image_license', 'image_license_link')},
        )
    )

    def nonempty_text(self, cite):
        if cite.text.strip():
            return cite.text
        return "(%s)" % ((cite.image_title or '').strip() or cite.link)
    nonempty_text.short_description = _('text')

    def has_image(self, cite):
        return bool(cite.image)
    has_image.short_description = _('image')
    has_image.boolean = True


admin.site.register(Cite, CiteAdmin)


class BannerGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    fields = ['name', 'created_at']
    readonly_fields = ['created_at']

admin.site.register(BannerGroup, BannerGroupAdmin)


class CarouselItemInline(OrderableAdmin, admin.TabularInline):
    model = CarouselItem
    ordering_field = 'order'


class CarouselAdmin(admin.ModelAdmin):
    inlines = [CarouselItemInline]


admin.site.register(Carousel, CarouselAdmin)

