import json
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators import cache
from django.views.generic import DetailView, UpdateView
from . import models
from .states import Level, states


def describe(value):
    if hasattr(value, '_meta'):
        meta = value._meta
        return _('''a <a href="%(docs_url)s">%(verbose_name)s</a> object.''') % {
               'docs_url': reverse('django-admindocs-models-detail', args=(meta.app_label, meta.model_name)),
               'verbose_name': meta.verbose_name,
            }
    else:
        return type(value).__name__


@cache.never_cache
def state_info(request, slug):
    for state in states:
        if state.slug == slug:
            break
    else:
        return JsonResponse({})

    contact = models.Contact()
    ctx = {
        "contact": contact,
    }
    ctx.update(state(test=True).get_context(contact))
    help_text = '%s:<br>' % _('Context')
    for k, v in ctx.items():
        help_text += '<br><code>{{ %s }}</code> — %s<br>' % (k, describe(v))

    return JsonResponse({
        "help": help_text,
    })


class OptOutView(UpdateView):
    model = models.Contact
    slug_url_kwarg = 'key'
    slug_field = 'key'
    fields = []

    def get_success_url(self):
        return reverse('messaging_optout_ok', args=[self.object.key])

    def form_valid(self, form):
        self.object.ascend(Level.OPT_OUT)
        return super().form_valid(form)


class OptOutOkView(DetailView):
    model = models.Contact
    slug_url_kwarg = 'key'
    slug_field = 'key'


