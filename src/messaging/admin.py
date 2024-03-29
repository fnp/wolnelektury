from django.contrib import admin
from django.contrib import messages
from fnpdjango.actions import export_as_csv_action
from . import models


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['state', 'min_days_since', 'subject', 'min_hour', 'is_active']
    fieldsets = [
        (None, {"fields": [
            'state',
            ('min_days_since', 'max_days_since'),
            'is_active',
            ]}),
        ('Zawartość e-maila', {"fields": [
            'subject', 'body'
        ]}),
        ('Ograniczenia wysyłki', {"fields": [
            ('min_day_of_month', 'max_day_of_month'),
            ('dow_1', 'dow_2', 'dow_3', 'dow_4', 'dow_5', 'dow_6', 'dow_7'),
            ('min_hour', 'max_hour'),
        ]}),
    ]

    def _test_email(self, request, obj):
        if request.user.email:
            obj.send_test_email(request.user.email)
            messages.info(
                request,
                'Na adres %(email)s została wysłana testowa wiadomość.' % {
                    "email": request.user.email
                }
            )
        else:
            messages.warning(
                request,
                'Nie masz ustawionego adresu e-mail. Wiadomość testowa nie została wysłana.'
            )

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
    actions = [
#        export_as_csv_action(fields=['id', 'email', 'get_level_display', 'since', 'expires_at']),
        export_as_csv_action('Eksport dla PHPList', fields=['email', 'wl_optout_url'])
    ]


admin.site.register(models.Contact, ContactAdmin)
