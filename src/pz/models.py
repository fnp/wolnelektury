import re
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from .bank import parse_export_feedback


class Campaign(models.Model):
    name = models.CharField(_('name'), max_length=255, unique=True)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        verbose_name = _('campaign')
        verbose_name_plural = _('campaigns')

    def __str__(self):
        return self.name


class Fundraiser(models.Model):
    name = models.CharField(_('name'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('fundraiser')
        verbose_name_plural = _('fundraisers')

    def __str__(self):
        return self.name


class DirectDebit(models.Model):
    first_name = models.CharField(_('first name'), max_length=255, blank=True)
    last_name = models.CharField(_('last name'), max_length=255, blank=True)
    sex = models.CharField(_('sex'), max_length=1, blank=True, choices=[
        ('M', _('M')),
        ('F', _('F')),
    ])
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    street = models.CharField(_('street'), max_length=255, blank=True)
    building = models.CharField(_('building'), max_length=255, blank=True)
    flat = models.CharField(_('flat'), max_length=255, blank=True)
    town = models.CharField(_('town'), max_length=255, blank=True)
    postal_code = models.CharField(_('postal code'),  max_length=255, blank=True)
    phone = models.CharField(_('phone'), max_length=255, blank=True)
    email = models.CharField(_('e-mail'), max_length=255, blank=True)
    iban = models.CharField(_('IBAN'), max_length=255, blank=True)
    iban_valid = models.NullBooleanField(_('IBAN valid'), default=False)
    is_consumer = models.BooleanField(_('is a consumer'), default=True)
    payment_id = models.CharField(_('payment identifier'), max_length=255, blank=True, unique=True)
    agree_fundraising = models.BooleanField(_('agree fundraising'), default=False)
    agree_newsletter = models.BooleanField(_('agree newsletter'), default=False)

    acquisition_date = models.DateField(_('acquisition date'), help_text=_('Date from the form'), null=True, blank=True)
    submission_date = models.DateField(_('submission date'), null=True, blank=True, help_text=_('Date the fundaiser submitted the form'))
    bank_submission_date = models.DateField(_('bank submission date'), null=True, blank=True, help_text=_('Date when the form data is submitted to the bank'))
    bank_acceptance_date = models.DateField(_('bank accepted date'), null=True, blank=True, help_text=_('Date when bank accepted the form'))

    fundraiser = models.ForeignKey(Fundraiser, models.PROTECT, blank=True, null=True, verbose_name=_('fundraiser'))
    fundraiser_commission = models.IntegerField(_('fundraiser commission'), null=True, blank=True)
    fundraiser_bill = models.CharField(_('fundaiser bill number'), max_length=255, blank=True)

    amount = models.IntegerField(_('amount'), null=True, blank=True)

    notes = models.TextField(_('notes'), blank=True)

    needs_redo = models.BooleanField(_('needs redo'), default=False)
    cancelled_at = models.DateTimeField(_('cancelled at'), null=True, blank=True)
    optout = models.BooleanField(_('optout'), default=False)

    campaign = models.ForeignKey(Campaign, models.PROTECT, null=True, blank=True, verbose_name=_('campaign'))

    class Meta:
        verbose_name = _('direct debit')
        verbose_name_plural = _('direct debits')

    def __str__(self):
        return self.payment_id

    def save(self, **kwargs):
        self.iban_valid = not self.iban_warning() if self.iban else None
        super().save(**kwargs)

    @classmethod
    def get_next_payment_id(cls):
        # Find the last object added.
        last = cls.objects.order_by('-id').first()
        if last is None:
            return ''
        match = re.match(r'^(.*?)(\d+)$', last.payment_id)
        if match is None:
            return ''
        prefix = match.group(1)
        number = int(match.group(2))
        number_length = len(match.group(2))
        while True:
            number += 1
            payment_id = f'{prefix}{number:0{number_length}}'
            if not cls.objects.filter(payment_id=payment_id).exists():
                break
        return payment_id

    @property
    def full_name(self):
        return ' '.join((self.first_name, self.last_name)).strip()

    @property
    def street_address(self):
        street_addr = self.street
        if self.building:
            street_addr += ' ' + self.building
        if self.flat:
            street_addr += ' m. ' + self.flat
        street_addr = street_addr.strip()
        return street_addr

    def iban_warning(self):
        if not self.iban:
            return 'No IBAN'
        if len(self.iban) != 26:
            return 'Bad IBAN length'
        if int(self.iban[2:] + '2521' + self.iban[:2]) % 97 != 1:
            return 'This IBAN number looks invalid'
        return ''
    iban_warning.short_description = ''


class BankExportFeedback(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    csv = models.FileField(upload_to='pz/feedback/')

    def save(self, **kwargs):
        super().save(**kwargs)
        for payment_id, status, comment in parse_export_feedback(self.csv):
            debit = DirectDebit.objects.get(payment_id = payment_id)
            b, created = self.bankexportfeedbackline_set.get_or_create(
                debit=debit,
                defaults={
                    "status": status,
                    "comment": comment,
                }
            )
            if not created:
                b.status = status
                b.comment = comment
                b.save()
            if status == 1 and not debit.bank_acceptance_date:
                debit.bank_acceptance_date = now().date()
                debit.save()


class BankExportFeedbackLine(models.Model):
    feedback = models.ForeignKey(BankExportFeedback, models.CASCADE)
    debit = models.ForeignKey(DirectDebit, models.CASCADE)
    status = models.SmallIntegerField()
    comment = models.CharField(max_length=255)



class BankOrder(models.Model):
    payment_date = models.DateField(null=True, blank=True)
    sent = models.DateTimeField(null=True, blank=True)
    debits = models.ManyToManyField(DirectDebit, blank=True)
