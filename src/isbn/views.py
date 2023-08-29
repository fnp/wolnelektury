# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.contrib.auth.decorators import permission_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from isbn.forms import WLISBNForm, WLConfirmForm, FNPISBNForm
from isbn.models import ONIXRecord
from isbn.utils import PRODUCT_FORMATS, PRODUCT_FORMS


@permission_required('add_onixrecord')
def add_isbn_wl(request):
    form = WLISBNForm()
    return render(request, 'isbn/add_isbn.html', {
        'form': form,
        'next_view': reverse('confirm_isbn_wl'),
    })


@require_POST
@permission_required('add_onixrecord')
def confirm_isbn_wl(request):
    form = WLConfirmForm(data=request.POST)
    if not form.is_valid():
        # komunikat?
        return HttpResponseRedirect(reverse('add_isbn_wl'))
    data = form.prepare_data()
    if ONIXRecord.objects.filter(dc_slug=data['dc_slug']).exists():
        return HttpResponseRedirect(reverse('wl_dc_tags', kwargs={'slug': data['dc_slug']}))
    return render(request, 'isbn/confirm_isbn_wl.html', {
        'data': data,
        'form': form,
    })


@require_POST
@permission_required('add_onixrecord')
def save_wl_onix(request):
    form = WLConfirmForm(data=request.POST)
    if not form.is_valid():
        return HttpResponseRedirect(reverse('add_isbn_wl'))
    data = form.save()
    return HttpResponseRedirect(reverse('wl_dc_tags', kwargs={'slug': data['dc_slug']}))


@permission_required('add_onixrecord')
def wl_dc_tags(request, slug):
    records = ONIXRecord.objects.filter(dc_slug=slug)
    isbn_formats = []
    for record in records:
        file_format, content_type = PRODUCT_FORMATS[record.product_form_detail]
        isbn_formats.append((file_format, content_type, record.isbn(dashes=True)))
    return render(request, 'isbn/wl_dc_tags.html', {
        'slug': slug,
        'isbn_formats': isbn_formats,
        'title': records[0].title,
    })


@permission_required('add_onixrecord')
def add_isbn_fnp(request):
    if request.POST:
        form = FNPISBNForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('assigned_isbn', kwargs={'slug': form.slug()}))
    else:
        form = FNPISBNForm()
    return render(request, 'isbn/add_isbn.html', {
        'form': form,
        'next_view': '',
    })


def get_format(record):
    if record.product_form_detail:
        return PRODUCT_FORMATS[record.product_form_detail][0]
    else:
        return [key for key, value in PRODUCT_FORMS.items() if value == record.product_form][0]


@permission_required('add_onixrecord')
def assigned_isbn(request, slug):
    records = ONIXRecord.objects.filter(dc_slug=slug)
    isbn_formats = [
        (get_format(record), record.isbn(dashes=True)) for record in records]
    return render(request, 'isbn/assigned_isbn.html', {
        'title': records[0].title,
        'isbn_formats': isbn_formats,
    })
