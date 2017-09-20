# -*- coding: utf-8 -*-
from urllib import unquote

from django.contrib.auth.decorators import permission_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from fnpdjango.utils.views import serve_file
from honeypot.decorators import check_honeypot

from .forms import contact_forms
from .models import Attachment, Contact


@check_honeypot
def form(request, form_tag, force_enabled=False):
    try:
        form_class = contact_forms[form_tag]
    except KeyError:
        raise Http404
    if (getattr(form_class, 'disabled', False) and
            not (force_enabled and request.user.is_superuser)):
        template = getattr(form_class, 'disabled_template', None)
        if template:
            return render(request, template, {'title': form_class.form_title})
        raise Http404
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
    else:
        form = form_class(initial=request.GET)
    formset_classes = getattr(form, 'form_formsets', {})
    if request.method == 'POST':
        formsets = {
            prefix: formset_class(request.POST, request.FILES, prefix=prefix)
            for prefix, formset_class in formset_classes.iteritems()}
        if form.is_valid() and all(formset.is_valid() for formset in formsets.itervalues()):
            contact = form.save(request, formsets.values())
            if form.result_page:
                return redirect('contact_results', contact.id, contact.digest())
            else:
                return redirect('contact_thanks', form_tag)
    else:
        formsets = {prefix: formset_class(prefix=prefix) for prefix, formset_class in formset_classes.iteritems()}

    return render(
        request, ['contact/%s/form.html' % form_tag, 'contact/form.html'],
        {'form': form, 'formsets': formsets}
    )


def thanks(request, form_tag):
    try:
        form_class = contact_forms[form_tag]
    except KeyError:
        raise Http404

    return render(
        request, ['contact/%s/thanks.html' % form_tag, 'contact/thanks.html'],
        {'base_template': getattr(form_class, 'base_template', None)})


def results(request, contact_id, digest):
    contact = get_object_or_404(Contact, id=contact_id)
    if digest != contact.digest():
        raise Http404
    try:
        form_class = contact_forms[contact.form_tag]
    except KeyError:
        raise Http404

    return render(
        request, 'contact/%s/results.html' % contact.form_tag,
        {
            'results': form_class.results(contact),
            'base_template': getattr(form_class, 'base_template', None),
        }
    )


@permission_required('contact.change_attachment')
def attachment(request, contact_id, tag):
    attachment = get_object_or_404(Attachment, contact_id=contact_id, tag=tag)
    attachment_url = unquote(attachment.file.url)
    return serve_file(attachment_url)
