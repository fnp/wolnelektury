# -*- coding: utf-8 -*-
"""
Tagging utilities - from user tag input parsing to tag cloud
calculation.
"""


def get_queryset_and_model(queryset_or_model):
    """
    Given a ``QuerySet`` or a ``Model``, returns a two-tuple of
    (queryset, model).

    If a ``Model`` is given, the ``QuerySet`` returned will be created
    using its default manager.
    """
    try:
        return queryset_or_model, queryset_or_model.model
    except AttributeError:
        return queryset_or_model._default_manager.all(), queryset_or_model


def get_tag_list(tags):
    """
    Utility function for accepting tag input in a flexible manner.
    
    If a ``Tag`` object is given, it will be returned in a list as
    its single occupant.
    """
    from newtagging.models import TagBase
    if isinstance(tags, TagBase):
        return [tags]
    else:
        return tags

