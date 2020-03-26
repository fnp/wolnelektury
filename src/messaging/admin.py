from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from fnpdjango.actions import export_as_csv_action
from . import models


class EmailSentInline(admin.TabularInline):
    model = models.EmailSent
    fields = ['timestamp', 'contact', 'subject']
    readonly_fields = ['timestamp', 'contact', 'subject']
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

    def _test_email(self, request, obj):
        if request.user.email:
            obj.send_test_email(request.user.email)
            messages.info(request, _('Test e-mail has been sent to %(email)s.') % {"email": request.user.email})
        else:
            messages.warning(request, _('You have no email set. Test e-mail not sent.'))

    def response_add(self, request, obj):
        self._test_email(request, obj)
        return super().response_add(request, obj)

    def response_change(self, request, obj):
        self._test_email(request, obj)
        return super().response_change(request, obj)


admin.site.register(models.EmailTemplate, EmailTemplateAdmin)


class EmailSentAdmin(admin.ModelAdmin):
    list_filter = ['template']
    list_display = ['timestamp', 'template', 'contact', 'subject']
    fields = ['timestamp', 'template', 'contact', 'subject', 'body']
    readonly_fields = fields
    change_links = ['template']


admin.site.register(models.EmailSent, EmailSentAdmin)


class ContactEmailSentInline(admin.TabularInline):
    model = models.EmailSent
    fields = ['timestamp', 'template', 'subject']
    readonly_fields = ['timestamp', 'template', 'subject']
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj):
        return False


class ContactAdmin(admin.ModelAdmin):
    inlines = [ContactEmailSentInline]
    list_filter = ['level']
    list_display = ['email', 'level', 'since', 'expires_at']
    search_fields = ['email']
    date_hierarchy = 'since'
    actions = [export_as_csv_action(fields=['id', 'email', 'get_level_display', 'since', 'expires_at'])]


admin.site.register(models.Contact, ContactAdmin)
