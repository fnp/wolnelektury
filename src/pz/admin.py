from django.contrib import admin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from fnpdjango.actions import export_as_csv_action
from . import bank
from . import models


admin.site.register(models.Fundraiser)
admin.site.register(models.Campaign)


class BankExportFeedbackLineInline(admin.TabularInline):
    model = models.BankExportFeedbackLine
    extra = 0


@admin.register(models.DirectDebit)
class DirectDebitAdmin(admin.ModelAdmin):
    list_display = [
        'payment_id', 'acquisition_date',
        'iban_valid',
        'bank_submission_date',
        'bank_acceptance_date',
        'amount', 'first_name', 'last_name',
    ]
    date_hierarchy = 'acquisition_date'
    search_fields = [
        'payment_id', 'first_name', 'last_name', 'street', 'building', 'town', 'flat',
        'phone', 'email', 'iban',
        'notes',
        'fundraiser_bill',
    ]
    list_filter = [
        'iban_valid',
        'agree_fundraising',
        'agree_newsletter',
        'fundraiser',
        'campaign',
        'is_cancelled',
        'needs_redo',
        'optout',
        'amount',
        'sex',
        'is_consumer',
    ]
    fieldsets = [
        (None, {
            "fields": [
                ('first_name', 'sex', 'date_of_birth'),
                'last_name',
                ('street', 'building'),
                ('town', 'flat'),
                ('postal_code', 'phone'),
                'email',
                ('iban', 'iban_valid', 'iban_warning'),
                'payment_id',
                'agree_contact',
                'agree_fundraising',
                'agree_newsletter',
                ('acquisition_date', 'amount'),
                'is_consumer',
                'fundraiser',
                'campaign',
            ]
        }),
        (_('Processing'), {"fields": [
            ('is_cancelled', 'needs_redo', 'optout'),
            'submission_date',
            'fundraiser_commission',
            'fundraiser_bill',
            'bank_submission_date',
            'bank_acceptance_date',
            'notes',
            ]
        })
    ]
    readonly_fields = ['agree_contact', 'iban_valid', 'iban_warning']
    inlines = [BankExportFeedbackLineInline]

    def set_bank_submission(m, r, q):
        q.update(bank_submission_date=now())

    def create_bank_order(m, request, queryset):
        bo = models.BankOrder.objects.create()
        bo.debits.set(queryset)
        messages.info(request, mark_safe(
            '<a href="{}">Bank order</a> created.'.format(
                reverse('admin:pz_bankorder_change', args=[bo.pk])
            )
        ))


    actions = [
        bank.bank_export,
        set_bank_submission,
        create_bank_order,
        export_as_csv_action(),
    ]

    def agree_contact(self, obj):
        return _('obligatory')
    agree_contact.short_description = _('agree contact')

    def get_changeform_initial_data(self, request):
        return {
            'payment_id': models.DirectDebit.get_next_payment_id(),
        }


@admin.register(models.BankExportFeedback)
class BankExportFeedbackAdmin(admin.ModelAdmin):
    inlines = [BankExportFeedbackLineInline]



@admin.register(models.BankOrder)
class BankOrderAdmin(admin.ModelAdmin):
    fields = ['payment_date', 'debits', 'sent', 'download']
    filter_horizontal = ['debits']

    def get_readonly_fields(self, request, obj=None):
        fields = ['download']
        if obj is not None and obj.sent:
            fields += ['debits', 'payment_date']
        return fields

    def download(self, obj):
        if obj is not None and obj.pk:
            return mark_safe('<a href="{}">Download</a>'.format(
                reverse('admin:pz_bankorder_download', args=[obj.pk])
            ))
        else:
            return ''

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                '<int:pk>/download/',
                self.admin_site.admin_view(self.download_view),
                name='pz_bankorder_download',
            ),
        ]
        return my_urls + urls

    def download_view(self, request, pk):
        order = get_object_or_404(
            models.BankOrder, pk=pk)
        try:
            return bank.bank_order(order.payment_date, order.debits.all())
        except Exception as e:
            messages.error(request, str(e))
            return redirect('admin:pz_bankorder_change', pk)
