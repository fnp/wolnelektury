# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
# import feedparser
# import datetime

from django import template
from django.template import Node, Variable
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.db.models import Q
from django.conf import settings
# from django.utils.translation import ugettext as _
from catalogue.templatetags.catalogue_tags import book_wide
from catalogue.models import Book
# from catalogue.forms import SearchForm
# from catalogue.utils import split_tags


register = template.Library()


@register.inclusion_tag('catalogue/book_searched.html', takes_context=True)
def book_searched(context, result):
    book = Book.objects.get(pk=result.book_id)

    # snippets = []
    # for hit in result.hits:
    #     if hit['snippets']:
    #         snippets.append(hit['snippets'])
    #     elif hit['fragment']:
    #         snippets.append(hit['fragment'].short_text)

    # We don't need hits which lead to sections but do not have
    # snippets.
    hits = filter(lambda (idx, h):
                  result.snippets[idx] is not None
                  or 'fragment' in h, enumerate(result.hits))
    print "[tmpl: from %d hits selected %d]" % (len(result.hits), len(hits))

    for (idx, hit) in hits:
        # currently we generate one snipper per hit though.
        if 'fragment' in hit:
            continue
        snip = result.snippets[idx]
        # fix some formattting
        snip = snip.replace("\n", "<br />").replace('---', '&mdash;')
        hit['snippet'] = snip

    return {
        'related': book.related_info(),
        'book': book,
        'main_link': book.get_absolute_url(),
        'request': context.get('request'),
        'hits': zip(*hits)[1],
        'main_link': book.get_absolute_url(),
    }
