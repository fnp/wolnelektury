from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from fnpdjango.actions import export_as_csv_action
from . import bank
from . import models


admin.site.register(models.Fundraiser)
admin.site.register(models.Campaign)

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

    def set_bank_submission(m,r,q):
        q.update(bank_submission_date=now())
    actions = [
        bank.bank_export,
        set_bank_submission,
        export_as_csv_action(),
    ]

    def agree_contact(self, obj):
        return _('obligatory')
    agree_contact.short_description = _('agree contact')

    def get_changeform_initial_data(self, request):
        return {
            'payment_id': models.DirectDebit.get_next_payment_id(),
        }
