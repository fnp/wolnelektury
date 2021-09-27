from django.db import models
from django.utils.translation import ugettext_lazy as _


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
    is_consumer = models.BooleanField(_('is a consumer'), default=True)
    payment_id = models.CharField(_('payment identifier'), max_length=255, blank=True, unique=True)
    agree_fundraising = models.BooleanField(_('agree fundraising'))
    agree_newsletter = models.BooleanField(_('agree newsletter'))

    acquisition_date = models.DateField(_('acquisition date'), help_text=_('Date from the form'))
    submission_date = models.DateField(_('submission date'), null=True, blank=True, help_text=_('Date the fundaiser submitted the form'))
    bank_submission_date = models.DateField(_('bank submission date'), null=True, blank=True, help_text=_('Date when the form data is submitted to the bank'))
    bank_acceptance_date = models.DateField(_('bank accepted date'), null=True, blank=True, help_text=_('Date when bank accepted the form'))

    fundraiser = models.ForeignKey(Fundraiser, models.PROTECT, blank=True, null=True, verbose_name=_('fundraiser'))
    fundraiser_commission = models.IntegerField(_('fundraiser commission'), null=True, blank=True)
    fundraiser_bill = models.CharField(_('fundaiser bill number'), max_length=255, blank=True)

    amount = models.IntegerField(_('amount'))

    notes = models.TextField(_('notes'), blank=True)

    needs_redo = models.BooleanField(_('needs redo'), default=False)
    is_cancelled = models.BooleanField(_('is cancelled'), default=False)
    optout = models.BooleanField(_('optout'), default=False)

    campaign = models.ForeignKey(Campaign, models.PROTECT, null=True, blank=True, verbose_name=_('campaign'))

    class Meta:
        verbose_name = _('direct debit')
        verbose_name_plural = _('direct debits')

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

