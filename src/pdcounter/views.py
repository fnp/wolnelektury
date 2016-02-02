# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import datetime
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators import cache
from suggest.forms import PublishingSuggestForm
from . import models


@cache.never_cache
def book_stub_detail(request, slug):
    book = get_object_or_404(models.BookStub, slug=slug)
    if book.pd and not book.in_pd():
        pd_counter = datetime(book.pd, 1, 1)
    else:
        pd_counter = None

    form = PublishingSuggestForm(initial={"books": u"%s — %s, \n" % (book.author, book.title)})

    return render_to_response('pdcounter/book_stub_detail.html', {
        'book': book,
        'pd_counter': pd_counter,
        'form': form,
    }, context_instance=RequestContext(request))


@cache.never_cache
def author_detail(request, slug):
    author = get_object_or_404(models.Author, slug=slug)
    if not author.alive():
        pd_counter = datetime(author.goes_to_pd(), 1, 1)
    else:
        pd_counter = None

    form = PublishingSuggestForm(initial={"books": author.name + ", \n"})

    return render_to_response('pdcounter/author_detail.html', {
        'author': author,
        'pd_counter': pd_counter,
        'form': form,
    }, context_instance=RequestContext(request))
