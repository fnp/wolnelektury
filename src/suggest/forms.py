# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, mail_managers
from django.core.validators import validate_email
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from newsletter.forms import NewsletterForm
from suggest.models import PublishingSuggestion, Suggestion
from wolnelektury.utils import send_noreply_mail


class SuggestForm(NewsletterForm):
    email_field = 'contact'
    contact = forms.CharField(label=_('Contact'), max_length=120, required=False)
    description = forms.CharField(label=_('Description'), widget=forms.Textarea, required=True)

    data_processing_part2 = u'''\
Dane są przetwarzane w zakresie niezbędnym do obsługi zgłoszenia. W przypadku wyrażenia dodatkowej zgody \
adres e-mail zostanie wykorzystany także w celu przesyłania newslettera Wolnych Lektur.'''

    def save(self, request):
        super(SuggestForm, self).save()
        contact = self.cleaned_data['contact']
        description = self.cleaned_data['description']

        suggestion = Suggestion(contact=contact, description=description, ip=request.META['REMOTE_ADDR'])
        if request.user.is_authenticated:
            suggestion.user = request.user
        suggestion.save()

        mail_managers(u'Nowa sugestia na stronie WolneLektury.pl', u'''\
Zgłoszono nową sugestię w serwisie WolneLektury.pl.
http://%(site)s%(url)s

Użytkownik: %(user)s
Kontakt: %(contact)s

%(description)s''' % {
            'site': Site.objects.get_current().domain,
            'url': reverse('admin:suggest_suggestion_change', args=[suggestion.id]),
            'user': str(request.user) if request.user.is_authenticated else '',
            'contact': contact,
            'description': description,
            }, fail_silently=True)

        try:
            validate_email(contact)
        except ValidationError:
            pass
        else:
            send_noreply_mail(
                ugettext(u'Thank you for your suggestion.'),
                ugettext(u"""\
Thank you for your comment on WolneLektury.pl.
The suggestion has been referred to the project coordinator."""),
                [contact], fail_silently=True)


class PublishingSuggestForm(NewsletterForm):
    email_field = 'contact'
    contact = forms.CharField(label=_('Contact'), max_length=120, required=False)
    books = forms.CharField(label=_('books'), widget=forms.Textarea, required=True)
    ebook = forms.BooleanField(label=_('ebook'), required=False, initial=True)
    audiobook = forms.BooleanField(label=_('audiobook'), required=False)

    data_processing_part2 = SuggestForm.data_processing_part2

    def clean(self):
        if not self.cleaned_data['ebook'] and not self.cleaned_data['audiobook']:
            msg = ugettext(u"One of these options is required.")
            self._errors['ebook'] = self.error_class([msg])
            self._errors['audiobook'] = self.error_class([msg])
        return super(PublishingSuggestForm, self).clean()

    def save(self, request):
        super(PublishingSuggestForm, self).save()
        contact = self.cleaned_data['contact']
        suggestion_text = self.cleaned_data['books'].strip(', \n\r')

        books = suggestion_text if self.cleaned_data['ebook'] else ''
        audiobooks = suggestion_text if self.cleaned_data['audiobook'] else ''

        suggestion = PublishingSuggestion(
            contact=contact, books=books,
            audiobooks=audiobooks, ip=request.META['REMOTE_ADDR'])
        if request.user.is_authenticated:
            suggestion.user = request.user
        suggestion.save()

        if not suggestion.is_spam():
            mail_managers(u'Konsultacja planu wydawniczego na WolneLektury.pl', u'''\
    Zgłoszono nową sugestię nt. planu wydawniczego w serwisie WolneLektury.pl.
    %(url)s

    Użytkownik: %(user)s
    Kontakt: %(contact)s

    Książki:
    %(books)s

    Audiobooki:
    %(audiobooks)s''' % {
                'url': request.build_absolute_uri(reverse('admin:suggest_suggestion_change', args=[suggestion.id])),
                'user': str(request.user) if request.user.is_authenticated else '',
                'contact': contact,
                'books': books,
                'audiobooks': audiobooks,
            }, fail_silently=True)

            try:
                validate_email(contact)
            except ValidationError:
                pass
            else:
                send_noreply_mail(
                    ugettext(u'Thank you for your suggestion.'),
                    ugettext(u"""\
Thank you for your comment on WolneLektury.pl.
The suggestion has been referred to the project coordinator."""),
                    [contact], fail_silently=True)
