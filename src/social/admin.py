# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from django.forms import ModelForm
from django.forms.widgets import TextInput
from admin_ordering.admin import OrderableAdmin
from social.models import Cite, BannerGroup, Carousel, CarouselItem


class CiteForm(ModelForm):
    class Meta:
        model = Cite
        fields = '__all__'
        widgets = {
            'background_color': TextInput(attrs={'type': 'color'}),
        }

class CiteAdmin(admin.ModelAdmin):
    form = CiteForm
    list_display = ['nonempty_text', 'created_at', 'sticky', 'vip', 'small', 'has_image']
    list_filter = ['group']
    readonly_fields = ['created_at']
    autocomplete_fields = ['book']
    search_fields = ['text', 'link', 'picture_alt', 'picture_author', 'picture_link', 'image_title', 'image_author', 'image_link']
    fieldsets = (
        (None, {'fields': ('group', 'sticky', 'created_at', 'book')}),
        ('Zawartość', {'fields': ('link', 'vip', 'text', 'small')}),
        ('Media', {'fields': (
            'video',
            'picture', 'picture_alt',
                'picture_title', 'picture_author', 'picture_link',
                'picture_license', 'picture_license_link'
        )}),
        (
            'Tło',
            {'fields': (
                ('background_plain', 'background_color'),
                'image',
                'image_title', 'image_author', 'image_link',
                'image_license', 'image_license_link'
            )},
        )
    )

    def nonempty_text(self, cite):
        if cite.text.strip():
            return cite.text
        return "(%s)" % (cite.image_title or cite.link or '-').strip()
    nonempty_text.short_description = 'tekst'

    def has_image(self, cite):
        return bool(cite.image)
    has_image.short_description = 'obraz'
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
    autocomplete_fields = ['banner']


class CarouselAdmin(admin.ModelAdmin):
    list_display = ['placement', 'priority', 'language']
    inlines = [CarouselItemInline]


admin.site.register(Carousel, CarouselAdmin)

