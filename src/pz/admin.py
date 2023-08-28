from django.contrib import admin
from django.contrib.admin.filters import FieldListFilter, SimpleListFilter
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from fnpdjango.actions import export_as_csv_action
from . import bank
from . import models


admin.site.register(models.Fundraiser)
admin.site.register(models.Campaign)


# Backport from Django 3.1.
class EmptyFieldListFilter(FieldListFilter):
    with_empty_str = False

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '%s__isempty' % field_path
        self.lookup_val = params.get(self.lookup_kwarg)
        super().__init__(field, request, params, model, model_admin, field_path)

    def queryset(self, request, queryset):
        if self.lookup_kwarg not in self.used_parameters:
            return queryset
        if self.lookup_val not in ('0', '1'):
            raise IncorrectLookupParameters

        lookup_condition = Q(**{'%s__isnull' % self.field_path: True})
        if self.with_empty_str:
            lookup_condition |= Q(**{self.field_path: ''})
        if self.lookup_val == '1':
            return queryset.filter(lookup_condition)
        return queryset.exclude(lookup_condition)

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def choices(self, changelist):
        for lookup, title in (
            (None, 'Wszystkie'),
            ('1', 'Puste'),
            ('0', 'Niepuste'),
        ):
            yield {
                'selected': self.lookup_val == lookup,
                'query_string': changelist.get_query_string({self.lookup_kwarg: lookup}),
                'display': title,
            }


class PayedListFilter(SimpleListFilter):
    title = 'pobrane'
    parameter_name = 'payed'
    def lookups(self, request, model_admin):
        return (
                ('yes', 'tak'),
                ('no', 'nie'),
                )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(payment__is_dd=True, payment__realised=True).distinct()
        if self.value() == 'no':
            return queryset.exclude(payment__is_dd=True, payment__realised=True).distinct()



class BankExportFeedbackLineInline(admin.TabularInline):
    model = models.BankExportFeedbackLine
    extra = 0

class BankPaymentInline(admin.TabularInline):
    model = models.Payment
    extra = 0

@admin.register(models.DirectDebit)
class DirectDebitAdmin(admin.ModelAdmin):
    #unpaginate

    list_display = [
        'payment_id', 'acquisition_date',
        'iban_valid',
        'latest_status',
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
        ('cancelled_at', EmptyFieldListFilter),
        'latest_status',
        'needs_redo',
        'optout',
        'amount',
        'sex',
        'is_consumer',
        ('fundraiser_commission', EmptyFieldListFilter),
        ('fundraiser_bonus', EmptyFieldListFilter),
        PayedListFilter,
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
                ('payment_id', 'latest_status'),
                'agree_contact',
                'agree_fundraising',
                'agree_newsletter',
                ('acquisition_date', 'amount'),
                'is_consumer',
                'fundraiser',
                'campaign',
            ]
        }),
        ('Przetwarzanie', {"fields": [
            ('cancelled_at', 'needs_redo', 'optout'),
            'submission_date',
            'fundraiser_commission',
            'fundraiser_bonus',
            'fundraiser_bill',
            'bank_submission_date',
            'bank_acceptance_date',
            'notes',
            ]
        })
    ]
    readonly_fields = ['agree_contact', 'iban_valid', 'iban_warning', 'latest_status']
    inlines = [BankExportFeedbackLineInline, BankPaymentInline]

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
        return 'obowiązkowo'
    agree_contact.short_description = 'zgoda na kontakt'

    def get_changeform_initial_data(self, request):
        return {
            'payment_id': models.DirectDebit.get_next_payment_id(),
        }


@admin.register(models.BankExportFeedback)
class BankExportFeedbackAdmin(admin.ModelAdmin):
    inlines = [BankExportFeedbackLineInline, BankPaymentInline]



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
            return bank.bank_order(
                order.payment_date,
                order.sent,
                order.debits.all()
            )
        except Exception as e:
            messages.error(request, str(e))
            return redirect('admin:pz_bankorder_change', pk)
