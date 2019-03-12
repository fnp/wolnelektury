# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
import re

register = template.Library()


@register.inclusion_tag('catalogue/book_searched.html', takes_context=True)
def book_searched(context, result):
    # We don't need hits which lead to sections but do not have
    # snippets.
    hits = filter(lambda idx, h:
                  result.snippets[idx] is not None or ('fragment' in h and h['themes_hit']),
                  enumerate(result.hits))
    # print "[tmpl: from %d hits selected %d]" % (len(result.hits), len(hits))

    for (idx, hit) in hits:
        # currently we generate one snipper per hit though.
        if len(result.snippets) <= idx:
            break
        if result.snippets[idx] is None:
            continue
        snip = result.snippets[idx]
        # fix some formattting
        snip = re.sub(r"[ \t\n]*\n[ \t\n]*", u"\n", snip)
        snip = re.sub(r"(^[ \t\n]+|[ \t\n]+$)", u"", snip)

        snip = snip.replace("\n", "<br />").replace('---', '&mdash;')
        hit['snippet'] = snip

    return {
        'request': context['request'],
        'book': result.book,
        'hits':  zip(*hits)[1] if hits else []
    }
