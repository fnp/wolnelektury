# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators import cache
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext as _

from suggest import forms
from suggest.models import Suggestion

# FIXME - shouldn't be in catalogue
from catalogue.views import LazyEncoder 


#@require_POST
@cache.never_cache
def report(request):
    suggest_form = forms.SuggestForm(request.POST)
    if suggest_form.is_valid():
        contact = suggest_form.cleaned_data['contact']
        description = suggest_form.cleaned_data['description']

        suggestion = Suggestion(contact=contact,
            description=description, ip=request.META['REMOTE_ADDR'])
        if request.user.is_authenticated():
            suggestion.user = request.user
        suggestion.save()

        response_data = {'success': True, 'message': _('Report was sent successfully.')}
    else:
        response_data = {'success': False, 'errors': suggest_form.errors}
    print LazyEncoder(ensure_ascii=False).encode(response_data)
    return HttpResponse(LazyEncoder(ensure_ascii=False).encode(response_data))
