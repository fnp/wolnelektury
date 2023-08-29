# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
"""
Models and managers for generic tagging.
"""

from django.contrib.contenttypes.models import ContentType
from django.db import connection, models
from django.db.models.base import ModelBase
from django.dispatch import Signal

qn = connection.ops.quote_name

tags_updated = Signal()


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
        return queryset_or_model.objects.all(), queryset_or_model


############
# Managers #
############
class TagManager(models.Manager):
    def __init__(self):
        super(TagManager, self).__init__()
        models.signals.pre_delete.connect(self.target_deleted)

    @property
    def intermediary_table_model(self):
        return self.model.intermediary_table_model

    def target_deleted(self, instance, **kwargs):
        """ clear tag relations before deleting an object """
        try:
            int(instance.pk)
        except ValueError:
            return

        self.update_tags(instance, [])

    def update_tags(self, obj, tags):
        """
        Update tags associated with an object.
        """
        content_type = ContentType.objects.get_for_model(obj)
        current_tags = list(self.filter(items__content_type__pk=content_type.pk,
                                        items__object_id=obj.pk))
        updated_tags = tags

        # Remove tags which no longer apply
        tags_for_removal = [tag for tag in current_tags if tag not in updated_tags]
        if len(tags_for_removal):
            self.intermediary_table_model.objects.filter(
                content_type__pk=content_type.pk,
                object_id=obj.pk,
                tag__in=tags_for_removal).delete()
        # Add new tags
        tags_to_add = [tag for tag in updated_tags if tag not in current_tags]
        for tag in tags_to_add:
            existing = self.intermediary_table_model.objects.filter(
                content_type__pk=content_type.pk, object_id=obj.pk, tag=tag)
            if not existing:
                self.intermediary_table_model.objects.create(tag=tag, content_object=obj)

        tags_updated.send(sender=type(obj), instance=obj, affected_tags=tags_to_add + tags_for_removal)

    def remove_tag(self, obj, tag):
        """
        Remove tag from an object.
        """
        content_type = ContentType.objects.get_for_model(obj)
        self.intermediary_table_model.objects.filter(
            content_type__pk=content_type.pk, object_id=obj.pk, tag=tag).delete()

    def add_tag(self, obj, tag):
        """
        Add tag to an object.
        """
        content_type = ContentType.objects.get_for_model(obj)
        relations = self.intermediary_table_model.objects.filter(
            content_type__pk=content_type.pk, object_id=obj.pk, tag=tag)
        if not relations:
            self.intermediary_table_model.objects.create(tag=tag, content_object=obj)

    def get_for_object(self, obj):
        """
        Create a queryset matching all tags associated with the given
        object.
        """
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(items__content_type__pk=ctype.pk,
                           items__object_id=obj.pk)

    def usage_for_model(self, model, counts=False, filters=None):
        """
        Obtain a list of tags associated with instances of the given
        Model class.

        If ``counts`` is True, a ``count`` attribute will be added to
        each tag, indicating how many times it has been used against
        the Model class in question.

        To limit the tags (and counts, if specified) returned to those
        used by a subset of the Model's instances, pass a dictionary
        of field lookups to be applied to the given Model as the
        ``filters`` argument.
        """
        # TODO: Do we really need this filters stuff?
        if filters is None:
            filters = {}

        queryset = model.objects.filter()
        for f in filters.items():
            queryset.query.add_filter(f)
        usage = self.usage_for_queryset(queryset, counts)
        return usage

    def usage_for_queryset(self, queryset, counts=False):
        """
        Obtain a list of tags associated with instances of a model
        contained in the given queryset.

        If ``counts`` is True, a ``count`` attribute will be added to
        each tag, indicating how many times it has been used against
        the Model class in question.
        """
        usage = self.model.objects.filter(
            items__content_type=ContentType.objects.get_for_model(queryset.model),
            items__object_id__in=queryset)
        if counts:
            usage = usage.annotate(count=models.Count('id'))
        else:
            usage = usage.distinct()
        return usage

    def related_for_model(self, tags, model, counts=False):
        """
        Obtain a list of tags related to a given list of tags - that
        is, other tags used by items which have all the given tags.

        If ``counts`` is True, a ``count`` attribute will be added to
        each tag, indicating the number of items which have it in
        addition to the given list of tags.
        """
        objs = self.model.intermediary_table_model.objects.get_by_model(model, tags)
        qs = self.usage_for_queryset(objs, counts)
        qs = qs.exclude(pk__in=[tag.pk for tag in tags])
        return qs


class TaggedItemManager(models.Manager):
    @property
    def tag_model(self):
        return self.model.tag_model

    def get_by_model(self, queryset_or_model, tags):
        """
        Create a ``QuerySet`` containing instances of the specified
        model associated with a given tag or list of tags.
        """
        queryset, model = get_queryset_and_model(queryset_or_model)
        if not tags:
            # No existing tags were given
            return queryset.none()

        # TODO: presumes reverse generic relation
        # Multiple joins are WAY faster than having-count, at least on Postgres 9.1.
        for tag in tags:
            queryset = queryset.filter(tag_relations__tag=tag)
        return queryset

    def get_union_by_model(self, queryset_or_model, tags):
        """
        Create a ``QuerySet`` containing instances of the specified
        model associated with *any* of the given list of tags.
        """
        queryset, model = get_queryset_and_model(queryset_or_model)
        if not tags:
            return queryset.none()
        # TODO: presumes reverse generic relation
        return queryset.filter(tag_relations__tag__in=tags).distinct()

    def get_related(self, obj, queryset_or_model):
        """
        Retrieve a list of instances of the specified model which share
        tags with the model instance ``obj``, ordered by the number of
        shared tags in descending order.
        """
        queryset, model = get_queryset_and_model(queryset_or_model)
        # TODO: presumes reverse generic relation.
        # Do we know it's 'tags'?
        return queryset.filter(tag_relations__tag__in=obj.tags).annotate(
            count=models.Count('pk')).order_by('-count').exclude(pk=obj.pk)
