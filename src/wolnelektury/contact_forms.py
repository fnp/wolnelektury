# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.utils.functional import lazy
from django.utils.safestring import mark_safe

from contact.forms import ContactForm
from contact.fields import HeaderField
from django import forms

mark_safe_lazy = lazy(mark_safe, unicode)


class KonkursForm(ContactForm):
    form_tag = 'konkurs'
    form_title = u"Konkurs Trzy strony"
    admin_list = ['podpis', 'contact', 'temat']

    opiekun_header = HeaderField(label=u'Dane\xa0Opiekuna/Opiekunki')
    opiekun_nazwisko = forms.CharField(label=u'Imię i nazwisko', max_length=128)
    contact = forms.EmailField(label=u'Adres e-mail', max_length=128)
    opiekun_tel = forms.CharField(label=u'Numer telefonu', max_length=32)
    nazwa_dkk = forms.CharField(label=u'Nazwa DKK', max_length=128)
    adres_dkk = forms.CharField(label=u'Adres DKK', max_length=128)

    uczestnik_header = HeaderField(label=u'Dane\xa0Uczestnika/Uczestniczki')
    uczestnik_imie = forms.CharField(label=u'Imię', max_length=128)
    uczestnik_nazwisko = forms.CharField(label=u'Nazwisko', max_length=128)
    uczestnik_email = forms.EmailField(label=u'Adres e-mail', max_length=128)
    wiek = forms.ChoiceField(label=u'Kategoria wiekowa', choices=(
        ('0-11', 'do 11 lat'),
        ('12-15', '12–15 lat'),
        ('16-19', '16–19 lat'),
    ))
    tytul = forms.CharField(label=u'Tytuł opowiadania', max_length=255)
    plik = forms.FileField(
        label=u'Plik z opowiadaniem',
        help_text=u'Prosimy o nazwanie pliku imieniem i nazwiskiem autora.')

    agree_header = HeaderField(label=u'Oświadczenia')
    agree_terms = forms.BooleanField(
        label='Regulamin',
        help_text=mark_safe_lazy(
            u'Znam i akceptuję <a href="/media/chunks/attachment/Regulamin_konkursu_Trzy_strony.pdf">'
            u'Regulamin Konkursu</a>.'),
    )
    agree_data = forms.BooleanField(
        label='Przetwarzanie danych osobowych',
        help_text=u'Oświadczam, że wyrażam zgodę na przetwarzanie danych osobowych zawartych w niniejszym formularzu '
              u'zgłoszeniowym przez Fundację Nowoczesna Polska (administratora danych) z siedzibą w Warszawie (00-514) '
              u'przy ul. Marszałkowskiej 84/92 lok. 125 na potrzeby organizacji Konkursu. Jednocześnie oświadczam, '
              u'że zostałam/em poinformowana/y o tym, że mam prawo wglądu w treść swoich danych i możliwość ich '
              u'poprawiania oraz że ich podanie jest dobrowolne, ale niezbędne do dokonania zgłoszenia.')
    agree_license = forms.BooleanField(
        label='Licencja',
        help_text=mark_safe_lazy(
            u'Wyrażam zgodę oraz potwierdzam, że autor/ka (lub ich przedstawiciele ustawowi – gdy dotyczy) '
            u'wyrazili zgodę na korzystanie z opowiadania zgodnie z postanowieniami wolnej licencji '
            u'<a href="https://creativecommons.org/licenses/by-sa/3.0/pl/">Creative Commons Uznanie autorstwa – '
            u'Na tych samych warunkach 3.0</a>. Licencja pozwala każdemu na swobodne, nieodpłatne korzystanie z utworu '
            u'w oryginale oraz w postaci opracowań do wszelkich celów wymagając poszanowania autorstwa i innych praw '
            u'osobistych oraz tego, aby ewentualne opracowania utworu były także udostępniane na tej samej licencji.'))
    agree_wizerunek = forms.BooleanField(
        label='Rozpowszechnianie wizerunku',
        help_text=u'Wyrażam zgodę oraz potwierdzam, że autor/ka opowiadania (lub ich przedstawiciele ustawowi – '
              u'gdy dotyczy) wyrazili zgodę na fotografowanie i nagrywanie podczas gali wręczenia nagród i następnie '
              u'rozpowszechnianie ich wizerunków.')


class WorkshopsForm(ContactForm):
    form_tag = 'warsztaty'
    form_title = u"Formularz zgłoszeniowy"
    nazwisko = forms.CharField(label=u'Imię i nazwisko uczestnika', max_length=128)
    instytucja = forms.CharField(label=u'Instytucja/organizacja', max_length=128, required=False)
    contact = forms.EmailField(label=u'Adres e-mail', max_length=128)
    tel = forms.CharField(label=u'Numer telefonu', max_length=32)
    warsztat = forms.ChoiceField(choices=(
        ('skad-i-jak', u'Skąd i jak bezpiecznie korzystać z darmowych i wolnych wideo i zdjęć w sieci? '
                       u'Jak wykorzystać wolne licencje by zwiększyć zasięg Twoich publikacji?'),
        ('jak-badac', u'Jak badać wykorzystanie zbiorów domeny publicznej?'),
        ('kultura', u'Kultura dostępna dla wszystkich')),
        widget=forms.RadioSelect,
    )
    agree_header = HeaderField(label=mark_safe_lazy(u'<strong>Oświadczenia</strong>'))
    agree_data = forms.BooleanField(
        label='Przetwarzanie danych osobowych',
        help_text=u'Oświadczam, że wyrażam zgodę na przetwarzanie danych osobowych zawartych w niniejszym formularzu '
              u'zgłoszeniowym przez Fundację Nowoczesna Polska (administratora danych) z siedzibą w Warszawie (00-514) '
              u'przy ul. Marszałkowskiej 84/92 lok. 125 na potrzeby organizacji warsztatów w ramach wydarzenia '
              u'„WOLNE LEKTURY FEST”. Jednocześnie oświadczam, że zostałam/em poinformowana/y o tym, że mam prawo '
              u'wglądu w treść swoich danych i możliwość ich poprawiania oraz że ich podanie jest dobrowolne, '
              u'ale niezbędne do dokonania zgłoszenia.')
    agree_wizerunek = forms.BooleanField(
        label='Rozpowszechnianie wizerunku',
        help_text=u'Wyrażam zgodę na fotografowanie i nagrywanie podczas warsztatów „WOLNE LEKTURY FEST” '
                  u'24.11.2017 roku i następnie rozpowszechnianie mojego wizerunku w celach promocyjnych.')
    agree_gala = forms.BooleanField(
        label=u'Wezmę udział w uroczystej gali o godz. 19.00.', required=False)
