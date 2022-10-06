# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from ajaxable.utils import AjaxableFormView
from suggest import forms


class PublishingSuggestionFormView(AjaxableFormView):
    form_class = forms.PublishingSuggestForm
    title = _("Didn't find a book? Make a suggestion.")
    template = "publishing_suggest.html"
    submit = _('Send report')
    success_message = _('Report was sent successfully.')
    honeypot = True
    action = reverse_lazy('suggest_publishing')


class SuggestionFormView(AjaxableFormView):
    form_class = forms.SuggestForm
    title = _('Report a bug or suggestion')
    template = "suggest.html"
    submit = _('Send report')
    success_message = _('Report was sent successfully.')
    honeypot = True
    action = reverse_lazy('suggest')
