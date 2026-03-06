from django.contrib import admin
from . import models


class PriceLevelInline(admin.TabularInline):
    model = models.PriceLevel
    extra = 0


@admin.register(models.Partner)
class PartnerAdmin(admin.ModelAdmin):
    inlines = [
        PriceLevelInline,
    ]

