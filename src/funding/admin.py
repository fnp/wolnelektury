# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from fnpdjango.actions import export_as_csv_action
from .models import Offer, Perk, Funding, Spent


class OfferAdmin(TranslationAdmin):
    model = Offer
    list_display = ['title', 'author', 'target', 'sum', 'is_win', 'start', 'end']
    search_fields = ['title', 'author']
    readonly_fields = ('cover_img_tag',)
    autocomplete_fields = ['book']


class PerkAdmin(TranslationAdmin):
    model = Perk
    search_fields = ['name', 'long_name']
    list_display = ['name', 'long_name', 'price', 'end_date', 'offer']
    list_filter = ['offer']


class PayedFilter(admin.SimpleListFilter):
    title = 'płatność doszła do skutku'
    parameter_name = 'payed'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Tak'),
            ('no', 'Nie'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(completed_at=None)
        elif self.value() == 'no':
            return queryset.filter(completed_at=None)


class PerksFilter(admin.SimpleListFilter):
    title = 'prezenty'
    parameter_name = 'perks'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Tak'),
            ('no', 'Nie'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(perks=None)
        elif self.value() == 'no':
            return queryset.filter(perks=None)


class FundingAdmin(admin.ModelAdmin):
    model = Funding
    list_display = ['created_at', 'completed_at', 'offer', 'amount', 'name', 'email', 'perk_names']
    search_fields = ['name', 'email', 'offer__title', 'offer__author']
    list_filter = [PayedFilter, 'offer', PerksFilter]
    actions = [export_as_csv_action(
        fields=[
            'id', 'offer', 'name', 'email', 'amount', 'completed_at',
            'notifications', 'notify_key', 'wl_optout_url'
        ]
    )]


class SpentAdmin(admin.ModelAdmin):
    model = Spent
    list_display = ['book', 'amount', 'timestamp']
    search_fields = ['book__title']
    autocomplete_fields = ['book']


admin.site.register(Offer, OfferAdmin)
admin.site.register(Perk, PerkAdmin)
admin.site.register(Funding, FundingAdmin)
admin.site.register(Spent, SpentAdmin)
