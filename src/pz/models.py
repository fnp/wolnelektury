import re
from django.db import models
from django.utils.timezone import now
from .bank import parse_export_feedback, parse_payment_feedback


class Campaign(models.Model):
    name = models.CharField('nazwa', max_length=255, unique=True)
    description = models.TextField('opis', blank=True)

    class Meta:
        verbose_name = 'kampania'
        verbose_name_plural = 'kampanie'

    def __str__(self):
        return self.name


class Fundraiser(models.Model):
    name = models.CharField('imię i nazwisko', max_length=255, unique=True)

    class Meta:
        verbose_name = 'fundraiser'
        verbose_name_plural = 'fundraiserki i fundraiserzy'

    def __str__(self):
        return self.name


class DirectDebit(models.Model):
    first_name = models.CharField('imię', max_length=255, blank=True)
    last_name = models.CharField('nazwisko', max_length=255, blank=True)
    sex = models.CharField('płeć', max_length=1, blank=True, choices=[
        ('M', 'M'),
        ('F', 'K'),
    ])
    date_of_birth = models.DateField('data urodzenia', null=True, blank=True)
    street = models.CharField('ulica', max_length=255, blank=True)
    building = models.CharField('nr domu', max_length=255, blank=True)
    flat = models.CharField('nr mieszkania', max_length=255, blank=True)
    town = models.CharField('miejscowość', max_length=255, blank=True)
    postal_code = models.CharField('kod pocztowy', max_length=255, blank=True)
    phone = models.CharField('telefon', max_length=255, blank=True)
    email = models.CharField('e-mail', max_length=255, blank=True)
    iban = models.CharField('nr rachunku', max_length=255, blank=True)
    iban_valid = models.BooleanField('prawidłowy IBAN', default=False, null=True)
    is_consumer = models.BooleanField('konsument', default=True)
    payment_id = models.CharField('identyfikator płatności', max_length=255, blank=True, unique=True)
    agree_fundraising = models.BooleanField('zgoda na kontakt fundraisingowy', default=False)
    agree_newsletter = models.BooleanField('zgoda na newsletter', default=False)

    acquisition_date = models.DateField(
        'data pozyskania', help_text='Data z formularza',
        null=True, blank=True)
    submission_date = models.DateField(
        'data dostarczenia', null=True, blank=True,
        help_text='Data złożenia formularza przez fundraisera')
    bank_submission_date = models.DateField(
        'data złożenia do banku', null=True, blank=True,
        help_text='Data przesłania danych z formularza do banku')
    bank_acceptance_date = models.DateField(
        'data akceptacji przez bank', null=True, blank=True,
        help_text='Data kiedy bank przekazał informację o akceptacji danych z formularza')

    fundraiser = models.ForeignKey(Fundraiser, models.PROTECT, blank=True, null=True, verbose_name='fundraiser')
    fundraiser_commission = models.IntegerField('prowizja fundraisera', null=True, blank=True)
    fundraiser_bonus = models.IntegerField('bonus fundraisera', null=True, blank=True)
    fundraiser_bill = models.CharField('nr rachunku wystawionego przez fundraisera', max_length=255, blank=True)

    amount = models.IntegerField('kwota', null=True, blank=True)

    notes = models.TextField('uwagi', blank=True)

    needs_redo = models.BooleanField('do powtórki', default=False)
    cancelled_at = models.DateTimeField('anulowane', null=True, blank=True)
    optout = models.BooleanField('optout', default=False)

    campaign = models.ForeignKey(Campaign, models.PROTECT, null=True, blank=True, verbose_name='kampania')

    latest_status = models.CharField(max_length=255, blank=True)

    nosignature = models.BooleanField('Bez podpisu', default=False)
    
    class Meta:
        verbose_name = 'polecenie zapłaty'
        verbose_name_plural = 'polecenia zapłaty'

    def __str__(self):
        return "{} {}".format(self.payment_id, self.latest_status)

    def get_latest_status(self):
        line = self.bankexportfeedbackline_set.order_by('-feedback__created_at').first()
        if line is None: return ""
        return line.comment

    def save(self, **kwargs):
        self.iban_valid = not self.iban_warning() if self.iban else None
        self.latest_status = self.get_latest_status()
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
        try:
            self.save_payment_items()
        except AssertionError:
            self.save_export_feedback_items()

    def save_payment_items(self):
        for payment_id, booking_date, is_dd, realised, reject_code in parse_payment_feedback(self.csv.open()):
            debit = DirectDebit.objects.get(payment_id = payment_id)
            b, created = self.payment_set.get_or_create(
                debit=debit,
                defaults={
                    'booking_date': booking_date,
                    'is_dd': is_dd,
                    'realised': realised,
                    'reject_code': reject_code,
                }
            )
            if not created:
                b.booking_date = booking_date
                b.is_dd = is_dd
                b.realised = realised
                b.reject_code = reject_code
                b.save()
        
    def save_export_feedback_items(self):
        for payment_id, status, comment in parse_export_feedback(self.csv.open()):
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


class Payment(models.Model):
    feedback = models.ForeignKey(BankExportFeedback, models.CASCADE)
    debit = models.ForeignKey(DirectDebit, models.CASCADE)
    booking_date = models.DateField()
    is_dd = models.BooleanField()
    realised = models.BooleanField()
    reject_code = models.CharField(max_length=128, blank=True)

    

class BankOrder(models.Model):
    payment_date = models.DateField(null=True, blank=True)
    sent = models.DateTimeField(null=True, blank=True)
    debits = models.ManyToManyField(DirectDebit, blank=True)
