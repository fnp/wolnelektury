# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from ajaxable.utils import AjaxableFormView
from suggest import forms


class PublishingSuggestionFormView(AjaxableFormView):
    form_class = forms.PublishingSuggestForm
    title = _("Nie ma utworu na stronie? Zgłoś sugestię.")
    template = "publishing_suggest.html"
    submit = _('Wyślij zgłoszenie')
    success_message = _('Zgłoszenie zostało wysłane.')
    honeypot = True
    action = reverse_lazy('suggest_publishing')


class SuggestionFormView(AjaxableFormView):
    form_class = forms.SuggestForm
    title = _('Zgłoś błąd lub sugestię')
    template = "suggest.html"
    submit = _('Wyślij zgłoszenie')
    success_message = _('Zgłoszenie zostało wysłane.')
    honeypot = True
    action = reverse_lazy('suggest')
