# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django import template
from ..forms import PollForm


register = template.Library()


@register.inclusion_tag('polls/tags/poll.html', takes_context=True)
def poll(context, poll, show_results=True, redirect_to=''):
    form = None
    voted_already = poll.voted(context.get('request').session)
    if not voted_already:
        form = PollForm(poll=poll, initial=dict(redirect_to=redirect_to))
    return {'poll': poll, 'form': form, 'voted_already': voted_already, 'vote_count': poll.vote_count,
            'show_results': show_results, 'request': context.get('request')}
