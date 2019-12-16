# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from django.contrib import admin
from django.http.response import HttpResponse
from django.views.decorators.cache import never_cache

from newsletter.models import Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'active')
    list_filter = ('active',)

    def get_urls(self):
        urls = super(SubscriptionAdmin, self).get_urls()
        my_urls = [
            path('extract/', self.extract_subscribers, name='extract_subscribers'),
        ]
        return my_urls + urls

    @never_cache
    def extract_subscribers(self, request):
        active_subscriptions = Subscription.objects.filter(active=True)
        return HttpResponse('\n'.join(active_subscriptions.values_list('email', flat=True)),
                            content_type='text/plain')


admin.site.register(Subscription, SubscriptionAdmin)
