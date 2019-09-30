from django.contrib import admin
from .models import EmailTemplate, EmailSent


class EmailSentInline(admin.TabularInline):
    model = EmailSent
    fields = ['timestamp', 'email', 'subject']
    readonly_fields = ['timestamp', 'email', 'subject']
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj):
        return False


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['state', 'days', 'subject', 'hour']
    inlines = [EmailSentInline]


admin.site.register(EmailTemplate, EmailTemplateAdmin)


class EmailSentAdmin(admin.ModelAdmin):
    list_filter = ['template']
    list_display = ['timestamp', 'template', 'email', 'subject']
    fields = ['timestamp', 'template', 'email', 'subject', 'body', 'hash_value']
    readonly_fields = fields
    change_links = ['template']


admin.site.register(EmailSent, EmailSentAdmin)

