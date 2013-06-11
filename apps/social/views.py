# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
#~ from django.utils.datastructures import SortedDict
from django.views.decorators.http import require_POST
#~ from django.contrib import auth
#~ from django.views.decorators import cache
from django.utils.translation import ugettext as _

from ajaxable.utils import LazyEncoder, JSONResponse, AjaxableFormView

from catalogue.models import Book, Tag
from social import forms
from social.utils import get_set, likes, set_sets


# ====================
# = Shelf management =
# ====================


@require_POST
def like_book(request, slug):
    if not request.user.is_authenticated():
        return HttpResponseForbidden('Login required.')
    book = get_object_or_404(Book, slug=slug)
    if not likes(request.user, book):
        tag = get_set(request.user, '')
        set_sets(request.user, book, [tag])

    if request.is_ajax():
        return JSONResponse({"success": True, "msg": "ok", "like": True})
    else:
        return redirect(book)


@login_required
def my_shelf(request):
    books = Book.tagged.with_any(request.user.tag_set.all())
    return render(request, 'social/my_shelf.html', locals())


class ObjectSetsFormView(AjaxableFormView):
    form_class = forms.ObjectSetsForm
    placeholdize = True
    template = 'social/sets_form.html'
    ajax_redirect = True
    POST_login = True

    def get_object(self, request, slug):
        return get_object_or_404(Book, slug=slug)

    def context_description(self, request, obj):
        return obj.pretty_title()

    def form_args(self, request, obj):
        return (obj, request.user), {}


@require_POST
def unlike_book(request, slug):
    if not request.user.is_authenticated():
        return HttpResponseForbidden('Login required.')
    book = get_object_or_404(Book, slug=slug)
    if likes(request.user, book):
        set_sets(request.user, book, [])

    if request.is_ajax():
        return JSONResponse({"success": True, "msg": "ok", "like": False})
    else:
        return redirect(book)
