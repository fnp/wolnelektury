# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.views.generic.edit import FormView

from catalogue.models import Book, Tag
import catalogue.models.tag
from social import forms, models
from wolnelektury.utils import is_ajax


# ====================
# = Shelf management =
# ====================


@login_required
def like_book(request, slug):
    book = get_object_or_404(Book, slug=slug)

    if request.method != 'POST':
        return redirect(book)

    book.like(request.user)

    if is_ajax(request):
        return JsonResponse({"success": True, "msg": "ok", "like": True})
    else:
        return redirect(book)


class AddSetView(FormView):
    form_class = forms.AddSetForm
    template_name = 'forms/form_detail.html'

    def form_valid(self, form):
        book, tag = form.save(self.request.user)

        if is_ajax(self.request):
            return JsonResponse(get_sets_for_book_ids([book.id], self.request.user))
        else:
            return redirect(book)


class RemoveSetView(AddSetView):
    form_class = forms.RemoveSetForm


@login_required
def unlike_book(request, slug):
    book = get_object_or_404(Book, slug=slug)

    if request.method != 'POST':
        return redirect(book)

    book.unlike(request.user)

    if is_ajax(request):
        return JsonResponse({"success": True, "msg": "ok", "like": False})
    else:
        return redirect(book)


@login_required
def my_shelf(request):
    template_name = 'social/my_shelf.html'
    tags = list(request.user.tag_set.all())
    suggest = [t for t in tags if t.name]
    print(suggest)
        
    return render(request, template_name, {
        'tags': tags,
        'books': Book.tagged.with_any(tags),
        'suggest': suggest,
    })


def get_sets_for_book_ids(book_ids, user):
    data = {}
    tagged = catalogue.models.tag.TagRelation.objects.filter(
        tag__user=user,
        #content_type= # for books,
        object_id__in=book_ids
    ).order_by('tag__sort_key')
    for t in tagged:
        # related?
        item = data.setdefault(t.object_id, [])
        if t.tag.name:
            item.append({
                "slug": t.tag.slug,
                "url": t.tag.get_absolute_url(),
                "name": t.tag.name,
            })
    for b in book_ids:
        if b not in data:
            data[b] = None
    return data
    
    


@never_cache
def my_liked(request):
    if not request.user.is_authenticated:
        return JsonResponse({})
    try:
        ids = [int(x) for x in request.GET.get('ids', '').split(',')]
    except:
        return JsonResponse({})
    return JsonResponse(get_sets_for_book_ids(ids, request.user))


@never_cache
@login_required
def my_tags(request):
    term = request.GET.get('term', '')
    tags =             Tag.objects.filter(user=request.user).order_by('sort_key')
    if term:
        tags = tags.filter(name__icontains=term)
    return JsonResponse(
        [
            t.name for t in tags
        ], safe=False
    )


def confirm_user(request, key):
    uc = get_object_or_404(models.UserConfirmation, key=key)
    user = uc.user
    uc.use()
    return render(request, 'social/user_confirmation.html', {
        'user': user,
    })
