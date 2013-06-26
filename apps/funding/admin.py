from django.contrib import admin
from .models import Offer, Perk, Funding, Spent


class OfferAdmin(admin.ModelAdmin):
    model = Offer
    list_display = ['title', 'author', 'target', 'sum', 'is_win', 'start', 'end', 'due']
    search_fields = ['title', 'author']
    readonly_fields = ('cover_img_tag',)


class PerkAdmin(admin.ModelAdmin):
    model = Perk
    list_display = ['name', 'long_name', 'price', 'end_date', 'offer']


class FundingAdmin(admin.ModelAdmin):
    model = Funding
    list_display = ['payed_at', 'offer', 'amount', 'name', 'email']
    search_fields = ['name', 'email', 'offer__title', 'offer__author']


class SpentAdmin(admin.ModelAdmin):
    model = Spent
    list_display = ['book', 'amount', 'timestamp']
    search_fields = ['book__title']


admin.site.register(Offer, OfferAdmin)
admin.site.register(Perk, PerkAdmin)
admin.site.register(Funding, FundingAdmin)
admin.site.register(Spent, SpentAdmin)
