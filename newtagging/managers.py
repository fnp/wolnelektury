"""
Custom managers for Django models registered with the tagging
application.
"""
from django.contrib.contenttypes.models import ContentType
from django.db import models


class ModelTagManager(models.Manager):
    """
    A manager for retrieving tags for a particular model.
    """
    def __init__(self, tag_model):
        super(ModelTagManager, self).__init__()
        self.tag_model = tag_model
    
    def get_query_set(self):
        content_type = ContentType.objects.get_for_model(self.model)
        return self.tag_model.objects.filter(
            items__content_type__pk=content_type.pk).distinct()
    
    def related(self, tags, *args, **kwargs):
        return self.tag_model.objects.related_for_model(tags, self.model, *args, **kwargs)
    
    def usage(self, *args, **kwargs):
        return self.tag_model.objects.usage_for_model(self.model, *args, **kwargs)


class ModelTaggedItemManager(models.Manager):
    """
    A manager for retrieving model instances based on their tags.
    """
    def __init__(self, tag_model):
        super(ModelTaggedItemManager, self).__init__()
        self.intermediary_table_model = tag_model.objects.intermediary_table_model

    def related_to(self, obj, queryset=None, num=None):
        if queryset is None:
            return self.intermediary_table_model.objects.get_related(obj, self.model, num=num)
        else:
            return self.intermediary_table_model.objects.get_related(obj, queryset, num=num)

    def with_all(self, tags, queryset=None):
        if queryset is None:
            return self.intermediary_table_model.objects.get_by_model(self.model, tags)
        else:
            return self.intermediary_table_model.objects.get_by_model(queryset, tags)

    def with_any(self, tags, queryset=None):
        if queryset is None:
            return self.intermediary_table_model.objects.get_union_by_model(self.model, tags)
        else:
            return self.intermediary_table_model.objects.get_union_by_model(queryset, tags)


class TagDescriptor(object):
    """
    A descriptor which provides access to a ``ModelTagManager`` for
    model classes and simple retrieval, updating and deletion of tags
    for model instances.
    """
    def __init__(self, tag_model):
        self.tag_model = tag_model
    
    def __get__(self, instance, owner):
        if not instance:
            tag_manager = ModelTagManager(self.tag_model)
            tag_manager.model = owner
            return tag_manager
        else:
            return self.tag_model.objects.get_for_object(instance)

    def __set__(self, instance, value):
        self.tag_model.objects.update_tags(instance, value)

    def __del__(self, instance):
        self.tag_model.objects.update_tags(instance, [])

