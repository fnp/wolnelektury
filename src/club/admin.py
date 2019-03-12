from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from . import models


class PlanAdmin(admin.ModelAdmin):
    list_display = ['min_amount', 'interval']

admin.site.register(models.Plan, PlanAdmin)


class PaymentInline(admin.TabularInline):
    model = models.Payment
    extra = 0
    readonly_fields = ['payed_at']


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['email', 'started_at', 'expires_at', 'plan', 'amount', 'is_active', 'is_cancelled']
    list_search = ['email']
    list_filter = ['is_active', 'is_cancelled']
    date_hierarchy = 'started_at'
    raw_id_fields = ['membership']
    inlines = [PaymentInline]

admin.site.register(models.Schedule, ScheduleAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payed_at', 'schedule']

admin.site.register(models.Payment, PaymentAdmin)


class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user']
    raw_id_fields = ['user']
    search_fields = ['user__username', 'user__email']

admin.site.register(models.Membership, MembershipAdmin)


admin.site.register(models.ReminderEmail, TranslationAdmin)
