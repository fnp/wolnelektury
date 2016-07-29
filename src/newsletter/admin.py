# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib import admin
from django.http.response import HttpResponse

from newsletter.models import Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super(SubscriptionAdmin, self).get_urls()
        my_urls = [
            url(r'^extract/$', self.extract_subscribers, name='extract_subscribers'),
        ]
        return my_urls + urls

    def extract_subscribers(self, request):
        return HttpResponse(',\n'.join(Subscription.objects.values_list('email', flat=True)), content_type='text/plain')


admin.site.register(Subscription, SubscriptionAdmin)
