# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.utils.translation import ugettext_lazy as _

from ajaxable.utils import AjaxableFormView
from suggest import forms


class PublishingSuggestionFormView(AjaxableFormView):
    form_class = forms.PublishingSuggestForm
    title = _('Report a bug or suggestion')
    template = "publishing_suggest.html"
    success_message = _('Report was sent successfully.')
    honeypot = True


class SuggestionFormView(AjaxableFormView):
    form_class = forms.SuggestForm
    title = _('Report a bug or suggestion')
    submit = _('Send report')
    success_message = _('Report was sent successfully.')
    honeypot = True
