# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from ajaxable.utils import AjaxableFormView

from catalogue.models import Book
from social import forms


# ====================
# = Shelf management =
# ====================


@require_POST
def like_book(request, slug):
    if not request.user.is_authenticated:
        return HttpResponseForbidden('Login required.')
    book = get_object_or_404(Book, slug=slug)

    book.like(request.user)

    if request.is_ajax():
        return JsonResponse({"success": True, "msg": "ok", "like": True})
    else:
        return redirect(book)


@require_POST
def unlike_book(request, slug):
    if not request.user.is_authenticated:
        return HttpResponseForbidden('Login required.')
    book = get_object_or_404(Book, slug=slug)

    book.unlike(request.user)

    if request.is_ajax():
        return JsonResponse({"success": True, "msg": "ok", "like": False})
    else:
        return redirect(book)


@login_required
def my_shelf(request):
    return render(request, 'social/my_shelf.html', {
        'books': Book.tagged.with_any(request.user.tag_set.all())
    })


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
