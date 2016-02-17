# -*- coding: utf-8 -*-
"""
Tagging related views.
"""
from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic import ListView


def tagged_object_list(request, queryset_or_model, tag_model, tags, related_tags=False,
                       related_tag_counts=True, **kwargs):
    """
    A thin wrapper around
    ``django.views.generic.list_detail.object_list`` which creates a
    ``QuerySet`` containing instances of the given queryset or model
    tagged with the given tag.

    In addition to the context variables set up by ``object_list``, a
    ``tag`` context variable will contain the ``Tag`` instance for the
    tag.

    If ``related_tags`` is ``True``, a ``related_tags`` context variable
    will contain tags related to the given tag for the given model.
    Additionally, if ``related_tag_counts`` is ``True``, each related
    tag will have a ``count`` attribute indicating the number of items
    which have it in addition to the given tag.
    """

    tag_instances = tag_model.get_tag_list(tags)
    if tag_instances is None:
        raise Http404(_('No tags found matching "%s".') % tags)
    queryset = tag_model.intermediary_table_model.objects.get_by_model(queryset_or_model, tag_instances)
    if 'extra_context' not in kwargs:
        kwargs['extra_context'] = {}
    kwargs['extra_context']['tags'] = tag_instances
    if related_tags:
        kwargs['extra_context']['related_tags'] = \
            tag_model.objects.related_for_model(tag_instances, queryset_or_model, counts=related_tag_counts)
    return ListView.as_view(queryset=queryset)(request, **kwargs)
