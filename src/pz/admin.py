from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from . import models


admin.site.register(models.Fundraiser)
admin.site.register(models.Campaign)

@admin.register(models.DirectDebit)
class DirectDebitAdmin(admin.ModelAdmin):
    list_display = ['acquisition_date', 'amount', 'first_name', 'last_name']
    fieldsets = [
        (None, {
            "fields": [
                ('first_name', 'sex', 'date_of_birth'),
                'last_name',
                ('street', 'building'),
                ('town', 'flat'),
                ('postal_code', 'phone'),
                'email',
                'iban',
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
    readonly_fields = ['agree_contact']

    def agree_contact(self, obj):
        return _('obligatory')
    agree_contact.short_description = _('agree contact')

    def get_changeform_initial_data(self, request):
        return {
            'payment_id': models.DirectDebit.get_next_payment_id(),
        }
