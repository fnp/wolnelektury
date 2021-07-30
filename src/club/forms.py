# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from decimal import Decimal
from django import forms
from django.utils.translation import ugettext as _
from newsletter.forms import NewsletterForm
from . import models, payment_methods
from .payu.forms import CardTokenForm


class ScheduleForm(forms.ModelForm, NewsletterForm):
    data_processing = '''Informacja o przetwarzaniu danych osobowych

<div class='more-expand'>Administratorem Twoich danych osobowych jest Fundacja Nowoczesna Polska z siedzibą w Warszawie, przy ul. Marszałkowskiej 84/92 lok.125, 00-514 Warszawa (dalej: Fundacja).

Z Fundacją można się kontaktować we wszystkich sprawach dotyczących przetwarzania danych osobowych oraz korzystania z praw związanych z przetwarzaniem danych, w szczególności w zakresie wycofania udzielonej zgody na przetwarzanie danych poprzez adres e-mail fundacja@nowoczesnapolska.org.pl, telefonicznie pod numerem +48 22 621 30 17 (w dni powszednie w godz. 9-17) lub listownie pisząc na adres siedziby Fundacji.
Podanie danych osobowych jest dobrowolne, jednak konieczne do przeprowadzenia płatności oraz realizacji innych celów wskazanych poniżej.

Twoje dane będą przetwarzane w celu:
    • rozliczeniowym, księgowym, i innych sprawach związanych z Twoją darowizną na podstawie art. 6 ust. 1 lit. b i c RODO,
    • kontaktu telefonicznego, przez media elektroniczne oraz listownie, celem informowania o działalności oraz prośby o wsparcie na podstawie art. 6 ust. 1 lit. a,
    • przesyłania e-mailem newslettera: regularnej informacji o działalności fundacji oraz próśb o wsparcie na podstawie art. 6 ust. 1 lit. a RODO,
    • ewentualnego ustalenia i dochodzenia roszczeń lub obrony przed nimi; zapewnienia bezpieczeństwa u Administratora oraz realizacji wewnętrznych celów administracyjnych, analitycznych i statystycznych na podstawie art. 6 ust. 1 lit. f RODO; uzasadnionym interesem Administratora jest możliwość obrony przed ewentualnymi roszczeniami, zapewnienia bezpieczeństwa u Administratora oraz możliwość realizacji wewnętrznych celów administracyjnych, analitycznych i statystycznych przez Fundację.

Fundacja nie udostępnia Twoich danych osobowych podmiotom trzecim. Fundacja może korzystać z usług podwykonawców w celu realizacji kontaktu w ramach wyrażonej zgody. W szczególności Twoje dane mogą być przekazywane podmiotom takim jak banki, firma obsługująca księgowość i firmy współpracujące przy prowadzeniu akcji informacyjnych i edukacyjnych – przy czym takie podmioty przetwarzają dane wyłącznie na podstawie umowy z administratorem, wyłącznie zgodnie z poleceniami administratora i wyłącznie zgodnie z zakresem udzielonej zgody.

Twoje dane osobowe będą przechowywane do momentu wycofania zgody, rozliczenia darowizn, a po tym okresie przez okres przedawnienia ewentualnych roszczeń lub przez okres, który wynika z przepisów prawa, w szczególności obowiązku przechowywania dokumentów księgowych (rachunkowych).

Przysługuje Ci prawo dostępu do Twoich danych oraz prawo żądania ich sprostowania, ich usunięcia lub ograniczenia ich przetwarzania. W zakresie, w jakim podstawą przetwarzania Twoich danych osobowych jest przesłanka prawnie uzasadnionego interesu administratora, przysługuje Ci prawo wniesienia sprzeciwu wobec przetwarzania Twoich danych osobowych. W zakresie, w jakim podstawą przetwarzania Twoich danych osobowych jest zgoda, masz prawo wycofania zgody. Wycofanie zgody nie ma wpływu na zgodność z prawem przetwarzania, którego dokonano na podstawie zgody przed jej wycofaniem. W celu skorzystania z powyższych praw należy skontaktować się z fundacją w dowolny wskazany powyżej sposób.

Masz prawo do wniesienia skargi do organu nadzorczego, jeżeli uważasz, że Twoje dane osobowe są przetwarzane w niewłaściwy sposób.

Twoje dane osobowe nie będą profilowane, ani przesyłane do państw trzecich i organizacji międzynarodowych.

</div>
'''.replace('\n', '<br>')

    class Meta:
        model = models.Schedule
        fields = ['monthly', 'amount',
                  'first_name', 'last_name',
                  'email', 'phone',
                  'postal',
                  'postal_code', 'postal_town', 'postal_country',
                  'method']
        widgets = {
            'amount': forms.HiddenInput,
            'monthly': forms.HiddenInput,
            'method': forms.HiddenInput,

            'first_name': forms.TextInput(attrs={"placeholder": _('first name')}),
            'last_name': forms.TextInput(attrs={"placeholder": _('last name')}),

            'postal': forms.Textarea(attrs={"placeholder": _("If you leave your address, we'll be able to send you a postcard and other gadgets.")}),
            'postal_code': forms.TextInput(attrs={"placeholder": _('postal code')}),
            'postal_town': forms.TextInput(attrs={"placeholder": _('town')}),
        }

    def __init__(self, referer=None, **kwargs):
        self.referer = referer
        super().__init__(**kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['phone'].required = True
        
        self.consent = []
        for c in models.Consent.objects.filter(active=True).order_by('order'):
            key = f'consent{c.id}'
            self.fields[key] = forms.BooleanField(
                label=c.text,
                required=c.required
            )
            self.consent.append((
                c, key, (lambda k: lambda: self[k])(key)
            ))

    def clean_amount(self):
        value = self.cleaned_data['amount']
        club = models.Club.objects.first()
        if club and value < club.min_amount:
            raise forms.ValidationError(
                _('Minimal amount is %(amount)d PLN.') % {
                    'amount': club.min_amount
                }
            )
        return value

    def clean_method(self):
        value = self.cleaned_data['method']
        monthly = self.cleaned_data['monthly']
        for m in payment_methods.methods:
            if m.slug == value:
                if (monthly and m.is_recurring) or (not monthly and m.is_onetime):
                    return value
        if monthly:
            return payment_methods.recurring_payment_method.slug
        else:
            return payment_methods.single_payment_method.slug
    
    def save(self, *args, **kwargs):
        NewsletterForm.save(self, *args, **kwargs)
        self.instance.source = self.referer or ''
        instance = super().save(*args, **kwargs)

        consents = []
        for consent, key, consent_field in self.consent:
            if self.cleaned_data[key]:
                instance.consent.add(consent)

        return instance


class PayUCardTokenForm(CardTokenForm):
    def get_queryset(self, view):
        return view.get_schedule().payucardtoken_set
