from django.contrib import admin
from .models import Offer, Perk, Funding, Spent

admin.site.register(Spent)
admin.site.register(Offer)
admin.site.register(Perk)
admin.site.register(Funding)
