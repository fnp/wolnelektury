# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators import cache
from django.views.decorators.http import require_http_methods

from .models import Poll, PollItem
from .forms import PollForm


@cache.never_cache
@require_http_methods(['GET', 'POST'])
def poll(request, slug):
    poll = get_object_or_404(Poll, slug=slug, open=True)

    if request.method == 'POST':
        redirect_to = reverse('poll', args=[slug])
        form = PollForm(request.POST, poll=poll)
        if form.is_valid():
            if not poll.voted(request.session):
                try:
                    poll_item = PollItem.objects.filter(pk=form.cleaned_data['vote'], poll=poll).get()
                except PollItem.DoesNotExist:
                    pass
                else:
                    poll_item.vote(request.session)
        return redirect(redirect_to)
    elif request.method == 'GET':
        context = RequestContext(request)
        context['poll'] = poll
        context['voted_already'] = poll.voted(request.session)
        return render_to_response('polls/poll.html', context)
