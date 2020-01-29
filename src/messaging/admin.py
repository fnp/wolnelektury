from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from . import models


class EmailSentInline(admin.TabularInline):
    model = models.EmailSent
    fields = ['timestamp', 'email', 'subject']
    readonly_fields = ['timestamp', 'email', 'subject']
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj):
        return False


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['state', 'min_days_since', 'subject', 'min_hour']
    inlines = [EmailSentInline]
    fieldsets = [
        (None, {"fields": [
            'state',
            ('min_days_since', 'max_days_since'),
            'is_active',
            ]}),
        (_('E-mail content'), {"fields": [
            'subject', 'body'
        ]}),
        (_('Sending constraints'), {"fields": [
            ('min_day_of_month', 'max_day_of_month'),
            ('dow_1', 'dow_2', 'dow_3', 'dow_4', 'dow_5', 'dow_6', 'dow_7'),
            ('min_hour', 'max_hour'),
        ]}),
    ]


admin.site.register(models.EmailTemplate, EmailTemplateAdmin)


class EmailSentAdmin(admin.ModelAdmin):
    list_filter = ['template']
    list_display = ['timestamp', 'template', 'email', 'subject']
    fields = ['timestamp', 'template', 'email', 'subject', 'body', 'hash_value']
    readonly_fields = fields
    change_links = ['template']


admin.site.register(models.EmailSent, EmailSentAdmin)


class ContactAdmin(admin.ModelAdmin):
    list_filter = ['level']
    list_display = ['email', 'level', 'since', 'expires_at']
    search_fields = ['email']
    date_hierarchy = 'since'


admin.site.register(models.Contact, ContactAdmin)
