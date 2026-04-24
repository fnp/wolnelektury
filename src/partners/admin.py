from django.contrib import admin
from . import models


class PriceLevelInline(admin.TabularInline):
    model = models.PriceLevel
    extra = 0

class AudioPriceLevelInline(admin.TabularInline):
    model = models.AudioPriceLevel
    extra = 0

@admin.register(models.Partner)
class PartnerAdmin(admin.ModelAdmin):
    inlines = [
        PriceLevelInline,
        AudioPriceLevelInline,
    ]

