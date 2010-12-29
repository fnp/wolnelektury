# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
#from datetime import datetime

from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from pdcounter import models
from catalogue import forms


def book_stub_detail(request, slug):
    book = get_object_or_404(models.BookStub, slug=slug)
    pd_counter = book.pd
    form = forms.SearchForm()

    return render_to_response('pdcounter/book_stub_detail.html', locals(),
        context_instance=RequestContext(request))


def author_detail(request, slug):
    author = get_object_or_404(models.Author, slug=slug)
    pd_counter = author.goes_to_pd()
    form = forms.SearchForm()

    return render_to_response('pdcounter/author_detail.html', locals(),
        context_instance=RequestContext(request))
