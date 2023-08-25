# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import datetime
from django.shortcuts import render, get_object_or_404
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

    form = PublishingSuggestForm(initial={"books": "%s — %s, \n" % (book.author, book.title)})

    template_name = 'pdcounter/book_detail.html'

    return render(request, template_name, {
        'book': book,
        'pd_counter': pd_counter,
        'form': form,
    })


@cache.never_cache
def author_detail(request, slug):
    author = get_object_or_404(models.Author, slug=slug)
    if not author.alive():
        pd_counter = datetime(author.goes_to_pd(), 1, 1)
    else:
        pd_counter = None

    form = PublishingSuggestForm(initial={"books": author.name + ", \n"})

    template_name = 'pdcounter/author_detail.html'

    return render(request, template_name, {
        'author': author,
        'pd_counter': pd_counter,
        'form': form,
    })
