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
    ends_on = (2017, 11, 8)
    disabled_template = 'contact/disabled_contact_form.html'

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


class CoJaCzytamForm(ContactForm):
    form_tag = 'cojaczytam'
    form_title = u"#cojaczytam?"
    admin_list = ['opiekun_nazwisko', 'contact', 'nazwa_kampanii']
    ends_on = (2018, 11, 8)
    disabled_template = 'contact/disabled_contact_form.html'
    submit_label = u'Wyślij'

    opiekun_nazwisko = forms.CharField(label=u'Imię i nazwisko Opiekuna/ki', max_length=128)
    contact = forms.EmailField(label=u'Adres e-mail Opiekuna/ki', max_length=128)
    opiekun_tel = forms.CharField(label=u'Numer telefonu Opiekuna/ki', max_length=32)
    nazwa_dkk = forms.CharField(label=u'Nazwa szkoły/biblioteki publicznej', max_length=128)
    adres_dkk = forms.CharField(label=u'Adres szkoły/biblioteki publicznej', max_length=128)

    nazwa_kampanii = forms.CharField(label=u'Nazwa kampanii', max_length=255)

    wiek = forms.ChoiceField(label=u'Grupa wiekowa', choices=(
        ('9-14', u'uczniowie kl. IV-VIII szkół podstawowych w wieku 9-14 lat,'),
        ('15-19', u'uczniowie gimnazjum oraz wszystkich typów szkół ponadpodstawowych w wieku 15-19.'),
    ), widget=forms.RadioSelect)

    uczestnik1_header = HeaderField(label=u'Dane\xa0Uczestników (3 do 5)')
    uczestnik1_imie = forms.CharField(label=u'Imię', max_length=128)
    uczestnik1_nazwisko = forms.CharField(label=u'Nazwisko', max_length=128)
    uczestnik1_email = forms.EmailField(label=u'Adres e-mail', max_length=128)
    uczestnik2_header = HeaderField(label=u'')
    uczestnik2_imie = forms.CharField(label=u'Imię', max_length=128)
    uczestnik2_nazwisko = forms.CharField(label=u'Nazwisko', max_length=128)
    uczestnik2_email = forms.EmailField(label=u'Adres e-mail', max_length=128)
    uczestnik3_header = HeaderField(label=u'')
    uczestnik3_imie = forms.CharField(label=u'Imię', max_length=128)
    uczestnik3_nazwisko = forms.CharField(label=u'Nazwisko', max_length=128)
    uczestnik3_email = forms.EmailField(label=u'Adres e-mail', max_length=128)
    uczestnik4_header = HeaderField(label=u'')
    uczestnik4_imie = forms.CharField(label=u'Imię', max_length=128, required=False)
    uczestnik4_nazwisko = forms.CharField(label=u'Nazwisko', max_length=128, required=False)
    uczestnik4_email = forms.EmailField(label=u'Adres e-mail', max_length=128, required=False)
    uczestnik5_header = HeaderField(label=u'')
    uczestnik5_imie = forms.CharField(label=u'Imię', max_length=128, required=False)
    uczestnik5_nazwisko = forms.CharField(label=u'Nazwisko', max_length=128, required=False)
    uczestnik5_email = forms.EmailField(label=u'Adres e-mail', max_length=128, required=False)

    ankieta_header = HeaderField(label=u'')
    opis_kampanii = forms.CharField(
        label=u'Krótki opis realizacji oraz przebiegu kampanii', max_length=255, widget=forms.Textarea)
    co_sie_udalo = forms.CharField(label=u'Co udało Wam się zrealizować?', max_length=1024, widget=forms.Textarea)
    co_sie_nie_udalo = forms.CharField(
        label=u'Czy jest coś, co chcieliście zrealizować, a się nie udało? Jeśli tak, to dlaczego?', max_length=1024,
        widget=forms.Textarea)
    wnioski = forms.CharField(
        label=u'Jakie wnioski na przyszłość wyciągnęliście z tego, czego się nie udało zrealizować?', max_length=1024,
        widget=forms.Textarea)
    zasieg = forms.CharField(
        label=u'Do ilu odbiorców udało Wam się dotrzeć z Waszą kompanią? Podaj liczbę, może być szacunkowa.',
        max_length=1024, widget=forms.Textarea)
    grupy_odbiorcow = forms.CharField(
        label=u'Do jakich grup odbiorców dotarliście (np. uczniowie, nauczyciele, rodzice, seniorzy, inni)?',
        max_length=1024, widget=forms.Textarea)
    plik = forms.FileField(
        label=u'Plik .zip ze stworzonymi materiałami (np. zdjęcia, dokumenty tekstowe)')
    materialy = forms.CharField(
        label=u'Adresy stworzonych materiałów online (jeśli dotyczy)', max_length=1024, widget=forms.Textarea,
        required=False)

    agree_header = HeaderField(label=u'Oświadczenia')
    agree_terms = forms.BooleanField(
        label='Regulamin',
        help_text=mark_safe_lazy(
            u'Znam i akceptuję <a href="/media/chunks/attachment/Regulamin_konkursu_cojaczytam_edycja_2018.pdf">'
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
            u'Wyrażam zgodę oraz potwierdzam, że uczestnicy (lub ich przedstawiciele ustawowi – gdy dotyczy) '
            u'wyrazili zgodę na korzystanie ze stworzonych materiałów zgodnie z postanowieniami '
            u'<a href="http://freedomdefined.org/Definition/Pl">wolnej licencji</a>, takiej jak '
            u'<a href="https://creativecommons.org/licenses/by-sa/3.0/pl/">Creative Commons Uznanie autorstwa – '
            u'Na tych samych warunkach 3.0 PL</a>. Licencja pozwala każdemu na swobodne, nieodpłatne korzystanie '
            u'z utworu '
            u'w oryginale oraz w postaci opracowań do wszelkich celów wymagając poszanowania autorstwa i innych praw '
            u'osobistych oraz tego, aby ewentualne opracowania utworu były także udostępniane na tej samej licencji.'))
    agree_wizerunek = forms.BooleanField(
        label='Rozpowszechnianie wizerunku',
        help_text=u'Wyrażam zgodę oraz potwierdzam, że uczestnicy (lub ich przedstawiciele ustawowi – gdy dotyczy) '
                  u'wyrazili zgodę na fotografowanie oraz nagrywanie, a następnie rozpowszechnianie ich '
                  u'wizerunków w celach promocyjnych.')


class WorkshopsForm(ContactForm):
    form_tag = 'warsztaty'
    form_title = u"Wolne Lektury Fest"
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


class WLFest2018Form(ContactForm):
    form_tag = 'wlfest2018'
    form_title = u"Wolne Lektury Fest"
    nazwisko = forms.CharField(label=u'Imię i nazwisko uczestnika', max_length=128)
    instytucja = forms.CharField(label=u'Instytucja/organizacja', max_length=128, required=False)
    contact = forms.EmailField(label=u'Adres e-mail', max_length=128)
    tel = forms.CharField(label=u'Numer telefonu', max_length=32)
    warsztaty = forms.MultipleChoiceField(choices=(
        ('kim-sa-odbiorcy', u'Kim są odbiorcy zdigitalizowanych zasobów kultury w Polsce? (9:30-11:30)'),
        ('business-model-canvas', u'Business Model Canvas dla kultury (9:30-11:30)'),
        ('jak-byc-glam', u'Jak być GLAM? Współpraca pomiędzy instytucjami kultury a Wikipedią (12:00-14:00)'),
        ('wirtualne-muzea', u'Jak twórczo i zgodnie z prawem wykorzystywać zasoby dziedzictwa kulturowego '
                            u'na przykładzie portalu „Wirtualne Muzea Małopolski” (12:00-14:00)'),
        ('jak-legalnie-tworzyc', u'Jak legalnie tworzyć i korzystać z cudzej twórczości (15:00-17:00)'),
        ('aplikacje-w-dzialaniach', u'Aplikacje w działaniach kulturalnych (15:00-17:00)')),
        widget=forms.CheckboxSelectMultiple,
    )
    agree_header = HeaderField(label=mark_safe_lazy(u'<strong>Oświadczenia</strong>'))
    agree_data = forms.BooleanField(
        label='Przetwarzanie danych osobowych',
        help_text=u'Administratorem danych osobowych przetwarzanych w związku z organizacją wydarzenia '
                  u'„WOLNE LEKTURY FEST” jest Fundacja Nowoczesna Polska '
                  u'(ul. Marszałkowska 84/92 lok. 125, 00-514 Warszawa). Podanie danych osobowych jest konieczne '
                  u'do dokonania rejestracji na wydarzenie. Dane są przetwarzane w zakresie niezbędnym '
                  u'do przeprowadzenia wydarzenia, a także w celach prowadzenia statystyk, '
                  u'ewaluacji i sprawozdawczości. Osobom, których dane są zbierane, przysługuje prawo dostępu '
                  u'do treści swoich danych oraz ich poprawiania. Więcej informacji w polityce prywatności '
                  u'(https://nowoczesnapolska.org.pl/prywatnosc/).')
    agree_wizerunek = forms.BooleanField(
        label='Rozpowszechnianie wizerunku',
        help_text=u'Wyrażam zgodę na fotografowanie i nagrywanie podczas warsztatów „WOLNE LEKTURY FEST” '
                  u'28.11.2018 roku i następnie rozpowszechnianie mojego wizerunku w celach promocyjnych.')
    agree_gala = forms.BooleanField(
        label=u'Wezmę udział w spotkaniu z Julią Fiedorczuk o godz. 17:30.', required=False)
