import json
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from .states import states


def state_info(request, slug):
    for state in states:
        if state.slug == slug:
            break
    else:
        return JsonResponse({})

    meta = state().get_objects().model._meta


    help_text = _('''Context:<br>
       <code>{{ %(model_name)s }}</code> – a <a href="%(docs_url)s">%(verbose_name)s</a> object.<br>
       You can put it in in the fields <em>Subject</em> and <em>Body</em> using dot notation, like this:<br>
       <code>{{ %(model_name)s.id }}</code>.''') % {
               'model_name': meta.model_name,
               'docs_url': reverse('django-admindocs-models-detail', args=(meta.app_label, meta.model_name)),
               'verbose_name': meta.verbose_name,
            }

    return JsonResponse({
        "help": help_text,
    })

