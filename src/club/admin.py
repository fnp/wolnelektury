# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
from django.contrib import admin
from django.db.models.functions import Now
from django.db.models import Q
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from fnpdjango.actions import export_as_csv_action
from modeltranslation.admin import TranslationAdmin
from wolnelektury.utils import YesNoFilter
from . import models


admin.site.register(models.Club)


class PayUOrderInline(admin.TabularInline):
    model = models.PayUOrder
    fields = ['order_id', 'status', 'customer_ip']
    readonly_fields = fields
    extra = 0
    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


class PayUCardTokenInline(admin.TabularInline):
    model = models.PayUCardToken
    fields = ['created_at', 'disposable_token', 'reusable_token']
    readonly_fields = fields
    extra = 0
    show_change_link = True
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj):
        return False


class PayedFilter(YesNoFilter):
    title = _('payment complete')
    parameter_name = 'payed'
    q = ~Q(payed_at=None)


class ExpiredFilter(YesNoFilter):
    title = _('schedule expired')
    parameter_name = 'expired'
    q = Q(expires_at__isnull=False, expires_at__lt=Now())


class ScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'started_at', 'payed_at', 'expires_at', 'amount', 'monthly', 'yearly', 'is_cancelled',
        'method'
    ]
    search_fields = ['email']
    list_filter = ['is_cancelled', 'monthly', 'yearly', 'method', PayedFilter, ExpiredFilter, 'source']
    filter_horizontal = ['consent']
    date_hierarchy = 'started_at'
    raw_id_fields = ['membership']
    inlines = [PayUOrderInline, PayUCardTokenInline]
    actions = [export_as_csv_action()]

admin.site.register(models.Schedule, ScheduleAdmin)


class ScheduleInline(admin.TabularInline):
    model = models.Schedule
    fields = ['email', 'amount', 'is_cancelled', 'started_at', 'payed_at', 'expires_at', 'email_sent']
    readonly_fields = fields
    extra = 0
    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'manual', 'updated_at', 'notes']
    list_filter = ['manual']
    date_hierarchy = 'updated_at'
    raw_id_fields = ['user']
    search_fields = ['user__username', 'user__email', 'schedule__email', 'notes']
    inlines = [ScheduleInline]

admin.site.register(models.Membership, MembershipAdmin)


admin.site.register(models.ReminderEmail, TranslationAdmin)


class PayUNotificationAdmin(admin.ModelAdmin):
    list_display = ['received_at', 'order']
    fields = ['received_at', 'order', 'body_']
    readonly_fields = ['received_at', 'body_']
    raw_id_fields = ['order']

    def body_(self, obj):
        return mark_safe(
                "<pre>" +
                conditional_escape(json.dumps(json.loads(obj.body), indent=4))
                + "</pre>")


admin.site.register(models.PayUNotification, PayUNotificationAdmin)


class PayUNotificationInline(admin.TabularInline):
    model = models.PayUNotification
    fields = ['received_at', 'body_']
    readonly_fields = fields
    extra = 0
    show_change_link = True
    can_delete = False

    def body_(self, obj):
        return mark_safe(
                "<pre>" +
                conditional_escape(json.dumps(json.loads(obj.body), indent=4))
                + "</pre>")

    def has_add_permission(self, request, obj):
        return False


class PayUOrderAdmin(admin.ModelAdmin):
    list_display = ['schedule']
    raw_id_fields = ['schedule']
    inlines = [PayUNotificationInline]


admin.site.register(models.PayUOrder, PayUOrderAdmin)


admin.site.register(models.Ambassador)


    

@admin.register(models.Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ['text', 'order', 'active', 'required']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['text']
        else:
            return []
