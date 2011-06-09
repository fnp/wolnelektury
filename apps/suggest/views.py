# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.mail import send_mail, mail_managers
from django.core.urlresolvers import reverse
from django.core.validators import email_re
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.decorators import cache
from django.views.decorators.http import require_POST
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.template import RequestContext

from catalogue.forms import SearchForm
from suggest import forms
from suggest.models import Suggestion, PublishingSuggestion


# FIXME - shouldn't be in catalogue
from catalogue.views import LazyEncoder


class AjaxableFormView(object):
    formClass = None
    template = None
    ajax_template = None
    formname = None

    def __call__(self, request):
        """
            A view displaying a form, or JSON if `ajax' GET param is set.
        """
        ajax = request.GET.get('ajax', False)
        if request.method == "POST":
            form = self.formClass(request.POST)
            if form.is_valid():
                form.save(request)
                response_data = {'success': True, 'message': _('Report was sent successfully.')}
            else:
                response_data = {'success': False, 'errors': form.errors}
            if ajax:
                return HttpResponse(LazyEncoder(ensure_ascii=False).encode(response_data))
        else:
            form = self.formClass()
            response_data = None

        template = self.ajax_template if ajax else self.template
        return render_to_response(template, {
                self.formname: form, 
                "form": SearchForm(),
                "response_data": response_data,
            },
            context_instance=RequestContext(request))


class PublishingSuggestionFormView(AjaxableFormView):
    formClass = forms.PublishingSuggestForm
    ajax_template = "publishing_suggest.html"
    template = "publishing_suggest_full.html"
    formname = "pubsuggest_form"


@require_POST
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

        mail_managers(u'Nowa sugestia na stronie WolneLektury.pl', u'''\
Zgłoszono nową sugestię w serwisie WolneLektury.pl.
http://%(site)s%(url)s

Użytkownik: %(user)s
Kontakt: %(contact)s

%(description)s''' % {
            'site': Site.objects.get_current().domain,
            'url': reverse('admin:suggest_suggestion_change', args=[suggestion.id]),
            'user': str(request.user) if request.user.is_authenticated() else '',
            'contact': contact,
            'description': description,
            }, fail_silently=True)

        if email_re.match(contact):
            send_mail(u'[WolneLektury] ' + _(u'Thank you for your suggestion.'),
                    _(u"""\
Thank you for your comment on WolneLektury.pl.
The suggestion has been referred to the project coordinator.""") +
u"""

-- 
""" + _(u'''Message sent automatically. Please do not reply.'''),
                    'no-reply@wolnelektury.pl', [contact], fail_silently=True)

        response_data = {'success': True, 'message': _('Report was sent successfully.')}
    else:
        response_data = {'success': False, 'errors': suggest_form.errors}
    return HttpResponse(LazyEncoder(ensure_ascii=False).encode(response_data))
