# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _

from newsletter.forms import SubscribeForm, Newsletter


def subscribe_form(request, slug=''):
    newsletter = get_object_or_404(Newsletter, slug=slug)
    if request.POST:
        form = SubscribeForm(newsletter, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('subscribed'))
    else:
        form = SubscribeForm(newsletter)

    template_name = 'newsletter/subscribe_form.html'
    return render(request, template_name, {
        'page_title': newsletter.page_title,
        'form': form,
    })


def subscribed(request):
    template_name = 'newsletter/subscribed.html'
    return render(request, template_name, {
        'page_title': _('Zapisano do newslettera'),
    })

