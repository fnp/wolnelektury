# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from newsletter.forms import SubscribeForm, Newsletter


def subscribe_form(request, slug=''):
    newsletter = get_object_or_404(Newsletter, slug=slug)
    new_layout = request.EXPERIMENTS['layout'].value
    if request.POST:
        form = SubscribeForm(newsletter, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('subscribed'))
    else:
        form = SubscribeForm(newsletter)

    if new_layout:
        template_name = 'newsletter/2022/subscribe_form.html'
        form.template_name = '2022/form.html'
    else:
        template_name = 'newsletter/subscribe_form.html'
    return render(request, template_name, {
        'page_title': newsletter.page_title,
        'form': form,
    })


def subscribed(request):
    new_layout = request.EXPERIMENTS['layout'].value
    if new_layout:
        template_name = 'newsletter/2022/subscribed.html'
    else:
        template_name = 'newsletter/subscribed.html'
    return render(request, template_name, {
        'page_title': _('Subscribed'),
    })

