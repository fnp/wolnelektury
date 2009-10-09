from django.db import models
from django.contrib import admin

from sponsors.models import Sponsor, SponsorGroup
from sponsors.widgets import OrderedSelectMultiple

class SponsorGroupAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CommaSeparatedIntegerField: {'widget': OrderedSelectMultiple},
    }   
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

admin.site.register(SponsorGroup, SponsorGroupAdmin)
admin.site.register(Sponsor, SponsorAdmin)
