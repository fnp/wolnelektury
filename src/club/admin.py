# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from . import models


class PlanAdmin(admin.ModelAdmin):
    list_display = ['min_amount', 'interval']

admin.site.register(models.Plan, PlanAdmin)


class PayUOrderInline(admin.TabularInline):
    model = models.PayUOrder
    extra = 0
    show_change_link = True


class PayUCardTokenInline(admin.TabularInline):
    model = models.PayUCardToken
    extra = 0
    show_change_link = True


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['email', 'started_at', 'expires_at', 'plan', 'amount', 'is_cancelled']
    list_search = ['email']
    list_filter = ['is_cancelled']
    date_hierarchy = 'started_at'
    raw_id_fields = ['membership']
    inlines = [PayUOrderInline, PayUCardTokenInline]

admin.site.register(models.Schedule, ScheduleAdmin)


class ScheduleInline(admin.TabularInline):
    model = models.Schedule
    extra = 0
    show_change_link = True

class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user']
    raw_id_fields = ['user']
    search_fields = ['user__username', 'user__email', 'schedule__email']
    inlines = [ScheduleInline]

admin.site.register(models.Membership, MembershipAdmin)


admin.site.register(models.ReminderEmail, TranslationAdmin)


admin.site.register(models.PayUNotification)
