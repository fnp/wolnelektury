"""
Models and managers for generic tagging.
"""
# Python 2.3 compatibility
if not hasattr(__builtins__, 'set'):
    from sets import Set as set

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import connection, models
from django.utils.translation import ugettext_lazy as _
from django.db.models.base import ModelBase

qn = connection.ops.quote_name

try:
    from django.db.models.query import parse_lookup
except ImportError:
    parse_lookup = None


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


############
# Managers #
############
class TagManager(models.Manager):
    def __init__(self, intermediary_table_model):
        super(TagManager, self).__init__()
        self.intermediary_table_model = intermediary_table_model
    
    def update_tags(self, obj, tags):
        """
        Update tags associated with an object.
        """
        content_type = ContentType.objects.get_for_model(obj)
        current_tags = list(self.filter(items__content_type__pk=content_type.pk,
                                        items__object_id=obj.pk))
        updated_tags = self.model.get_tag_list(tags)
    
        # Remove tags which no longer apply
        tags_for_removal = [tag for tag in current_tags \
                            if tag not in updated_tags]
        if len(tags_for_removal):
            self.intermediary_table_model._default_manager.filter(content_type__pk=content_type.pk,
                                               object_id=obj.pk,
                                               tag__in=tags_for_removal).delete()
        # Add new tags
        for tag in updated_tags:
            if tag not in current_tags:
                self.intermediary_table_model._default_manager.create(tag=tag, content_object=obj)
    
    def get_for_object(self, obj):
        """
        Create a queryset matching all tags associated with the given
        object.
        """
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(items__content_type__pk=ctype.pk,
                           items__object_id=obj.pk)
    
    def _get_usage(self, model, counts=False, min_count=None, extra_joins=None, extra_criteria=None, params=None, extra=None):
        """
        Perform the custom SQL query for ``usage_for_model`` and
        ``usage_for_queryset``.
        """
        if min_count is not None: counts = True

        model_table = qn(model._meta.db_table)
        model_pk = '%s.%s' % (model_table, qn(model._meta.pk.column))
        tag_columns = self._get_tag_columns()
        
        if extra is None: extra = {}
        extra_where = ''
        if 'where' in extra:
            extra_where = 'AND ' + ' AND '.join(extra['where'])
        
        query = """
        SELECT DISTINCT %(tag_columns)s%(count_sql)s
        FROM
            %(tag)s
            INNER JOIN %(tagged_item)s
                ON %(tag)s.id = %(tagged_item)s.tag_id
            INNER JOIN %(model)s
                ON %(tagged_item)s.object_id = %(model_pk)s
            %%s
        WHERE %(tagged_item)s.content_type_id = %(content_type_id)s
            %%s
            %(extra_where)s
        GROUP BY %(tag)s.id, %(tag)s.name
        %%s
        ORDER BY %(tag)s.%(ordering)s ASC""" % {
            'tag': qn(self.model._meta.db_table),
            'ordering': ', '.join(qn(field) for field in self.model._meta.ordering),
            'tag_columns': tag_columns,
            'count_sql': counts and (', COUNT(%s)' % model_pk) or '',
            'tagged_item': qn(self.intermediary_table_model._meta.db_table),
            'model': model_table,
            'model_pk': model_pk,
            'extra_where': extra_where,
            'content_type_id': ContentType.objects.get_for_model(model).pk,
        }

        min_count_sql = ''
        if min_count is not None:
            min_count_sql = 'HAVING COUNT(%s) >= %%s' % model_pk
            params.append(min_count)

        cursor = connection.cursor()
        cursor.execute(query % (extra_joins, extra_criteria, min_count_sql), params)
        tags = []
        for row in cursor.fetchall():
            t = self.model(*row[:len(self.model._meta.fields)])
            if counts:
                t.count = row[len(self.model._meta.fields)]
            tags.append(t)
        return tags

    def usage_for_model(self, model, counts=False, min_count=None, filters=None, extra=None):
        """
        Obtain a list of tags associated with instances of the given
        Model class.

        If ``counts`` is True, a ``count`` attribute will be added to
        each tag, indicating how many times it has been used against
        the Model class in question.

        If ``min_count`` is given, only tags which have a ``count``
        greater than or equal to ``min_count`` will be returned.
        Passing a value for ``min_count`` implies ``counts=True``.

        To limit the tags (and counts, if specified) returned to those
        used by a subset of the Model's instances, pass a dictionary
        of field lookups to be applied to the given Model as the
        ``filters`` argument.
        """
        if extra is None: extra = {}
        if filters is None: filters = {}

        if not parse_lookup:
            # post-queryset-refactor (hand off to usage_for_queryset)
            queryset = model._default_manager.filter()
            for f in filters.items():
                queryset.query.add_filter(f)
            usage = self.usage_for_queryset(queryset, counts, min_count, extra)
        else:
            # pre-queryset-refactor
            extra_joins = ''
            extra_criteria = ''
            params = []
            if len(filters) > 0:
                joins, where, params = parse_lookup(filters.items(), model._meta)
                extra_joins = ' '.join(['%s %s AS %s ON %s' % (join_type, table, alias, condition)
                                        for (alias, (table, join_type, condition)) in joins.items()])
                extra_criteria = 'AND %s' % (' AND '.join(where))
            usage = self._get_usage(model, counts, min_count, extra_joins, extra_criteria, params, extra)

        return usage

    def usage_for_queryset(self, queryset, counts=False, min_count=None, extra=None):
        """
        Obtain a list of tags associated with instances of a model
        contained in the given queryset.

        If ``counts`` is True, a ``count`` attribute will be added to
        each tag, indicating how many times it has been used against
        the Model class in question.

        If ``min_count`` is given, only tags which have a ``count``
        greater than or equal to ``min_count`` will be returned.
        Passing a value for ``min_count`` implies ``counts=True``.
        """
        if parse_lookup:
            raise AttributeError("'TagManager.usage_for_queryset' is not compatible with pre-queryset-refactor versions of Django.")

        extra_joins = ' '.join(queryset.query.get_from_clause()[0][1:])
        where, params = queryset.query.where.as_sql()
        if where:
            extra_criteria = 'AND %s' % where
        else:
            extra_criteria = ''
        return self._get_usage(queryset.model, counts, min_count, extra_joins, extra_criteria, params, extra)

    def related_for_model(self, tags, model, counts=False, min_count=None, extra=None):
        """
        Obtain a list of tags related to a given list of tags - that
        is, other tags used by items which have all the given tags.

        If ``counts`` is True, a ``count`` attribute will be added to
        each tag, indicating the number of items which have it in
        addition to the given list of tags.

        If ``min_count`` is given, only tags which have a ``count``
        greater than or equal to ``min_count`` will be returned.
        Passing a value for ``min_count`` implies ``counts=True``.
        """
        if min_count is not None: counts = True
        tags = self.model.get_tag_list(tags)
        tag_count = len(tags)
        tagged_item_table = qn(self.intermediary_table_model._meta.db_table)
        tag_columns = self._get_tag_columns()
        
        if extra is None: extra = {}
        extra_where = ''
        if 'where' in extra:
            extra_where = 'AND ' + ' AND '.join(extra['where'])
        
        # Temporary table in this query is a hack to prevent MySQL from executing
        # inner query as dependant query (which could result in severe performance loss)
        query = """
        SELECT %(tag_columns)s%(count_sql)s
        FROM %(tagged_item)s INNER JOIN %(tag)s ON %(tagged_item)s.tag_id = %(tag)s.id
        WHERE %(tagged_item)s.content_type_id = %(content_type_id)s
        AND %(tagged_item)s.object_id IN
        (
            SELECT temporary.object_id 
            FROM (
                SELECT %(tagged_item)s.object_id
                FROM %(tagged_item)s, %(tag)s
                WHERE %(tagged_item)s.content_type_id = %(content_type_id)s
                  AND %(tag)s.id = %(tagged_item)s.tag_id
                  AND %(tag)s.id IN (%(tag_id_placeholders)s)
                GROUP BY %(tagged_item)s.object_id
                HAVING COUNT(%(tagged_item)s.object_id) = %(tag_count)s
            ) AS temporary
        )
        %(extra_where)s
        GROUP BY %(tag_columns)s
        %(min_count_sql)s
        ORDER BY %(tag)s.%(ordering)s ASC""" % {
            'tag': qn(self.model._meta.db_table),
            'ordering': ', '.join(qn(field) for field in self.model._meta.ordering),
            'tag_columns': tag_columns,
            'count_sql': counts and ', COUNT(%s.object_id)' % tagged_item_table or '',
            'tagged_item': tagged_item_table,
            'content_type_id': ContentType.objects.get_for_model(model).pk,
            'tag_id_placeholders': ','.join(['%s'] * tag_count),
            'extra_where': extra_where,
            'tag_count': tag_count,
            'min_count_sql': min_count is not None and ('HAVING COUNT(%s.object_id) >= %%s' % tagged_item_table) or '',
        }

        params = [tag.pk for tag in tags] * 2
        if min_count is not None:
            params.append(min_count)

        cursor = connection.cursor()
        cursor.execute(query, params)
        related = []
        for row in cursor.fetchall():
            tag = self.model(*row[:len(self.model._meta.fields)])
            if counts is True:
                tag.count = row[len(self.model._meta.fields)]
            related.append(tag)
        return related

    def _get_tag_columns(self):
        tag_table = qn(self.model._meta.db_table)
        return ', '.join('%s.%s' % (tag_table, qn(field.column)) for field in self.model._meta.fields)


class TaggedItemManager(models.Manager):
    """
    FIXME There's currently no way to get the ``GROUP BY`` and ``HAVING``
          SQL clauses required by many of this manager's methods into
          Django's ORM.

          For now, we manually execute a query to retrieve the PKs of
          objects we're interested in, then use the ORM's ``__in``
          lookup to return a ``QuerySet``.

          Once the queryset-refactor branch lands in trunk, this can be
          tidied up significantly.
    """
    def __init__(self, tag_model):
        super(TaggedItemManager, self).__init__()
        self.tag_model = tag_model
    
    def get_by_model(self, queryset_or_model, tags):
        """
        Create a ``QuerySet`` containing instances of the specified
        model associated with a given tag or list of tags.
        """
        tags = self.tag_model.get_tag_list(tags)
        tag_count = len(tags)
        if tag_count == 0:
            # No existing tags were given
            queryset, model = get_queryset_and_model(queryset_or_model)
            return model._default_manager.none()
        elif tag_count == 1:
            # Optimisation for single tag - fall through to the simpler
            # query below.
            tag = tags[0]
        else:
            return self.get_intersection_by_model(queryset_or_model, tags)

        queryset, model = get_queryset_and_model(queryset_or_model)
        content_type = ContentType.objects.get_for_model(model)
        opts = self.model._meta
        tagged_item_table = qn(opts.db_table)
        return queryset.extra(
            tables=[opts.db_table],
            where=[
                '%s.content_type_id = %%s' % tagged_item_table,
                '%s.tag_id = %%s' % tagged_item_table,
                '%s.%s = %s.object_id' % (qn(model._meta.db_table),
                                          qn(model._meta.pk.column),
                                          tagged_item_table)
            ],
            params=[content_type.pk, tag.pk],
        )

    def get_intersection_by_model(self, queryset_or_model, tags):
        """
        Create a ``QuerySet`` containing instances of the specified
        model associated with *all* of the given list of tags.
        """
        tags = self.tag_model.get_tag_list(tags)
        tag_count = len(tags)
        queryset, model = get_queryset_and_model(queryset_or_model)

        if not tag_count:
            return model._default_manager.none()

        model_table = qn(model._meta.db_table)
        # This query selects the ids of all objects which have all the
        # given tags.
        query = """
        SELECT %(model_pk)s
        FROM %(model)s, %(tagged_item)s
        WHERE %(tagged_item)s.content_type_id = %(content_type_id)s
          AND %(tagged_item)s.tag_id IN (%(tag_id_placeholders)s)
          AND %(model_pk)s = %(tagged_item)s.object_id
        GROUP BY %(model_pk)s
        HAVING COUNT(%(model_pk)s) = %(tag_count)s""" % {
            'model_pk': '%s.%s' % (model_table, qn(model._meta.pk.column)),
            'model': model_table,
            'tagged_item': qn(self.model._meta.db_table),
            'content_type_id': ContentType.objects.get_for_model(model).pk,
            'tag_id_placeholders': ','.join(['%s'] * tag_count),
            'tag_count': tag_count,
        }

        cursor = connection.cursor()
        cursor.execute(query, [tag.pk for tag in tags])
        object_ids = [row[0] for row in cursor.fetchall()]
        if len(object_ids) > 0:
            return queryset.filter(pk__in=object_ids)
        else:
            return model._default_manager.none()

    def get_union_by_model(self, queryset_or_model, tags):
        """
        Create a ``QuerySet`` containing instances of the specified
        model associated with *any* of the given list of tags.
        """
        tags = self.tag_model.get_tag_list(tags)
        tag_count = len(tags)
        queryset, model = get_queryset_and_model(queryset_or_model)

        if not tag_count:
            return model._default_manager.none()

        model_table = qn(model._meta.db_table)
        # This query selects the ids of all objects which have any of
        # the given tags.
        query = """
        SELECT %(model_pk)s
        FROM %(model)s, %(tagged_item)s
        WHERE %(tagged_item)s.content_type_id = %(content_type_id)s
          AND %(tagged_item)s.tag_id IN (%(tag_id_placeholders)s)
          AND %(model_pk)s = %(tagged_item)s.object_id
        GROUP BY %(model_pk)s""" % {
            'model_pk': '%s.%s' % (model_table, qn(model._meta.pk.column)),
            'model': model_table,
            'tagged_item': qn(self.model._meta.db_table),
            'content_type_id': ContentType.objects.get_for_model(model).pk,
            'tag_id_placeholders': ','.join(['%s'] * tag_count),
        }

        cursor = connection.cursor()
        cursor.execute(query, [tag.pk for tag in tags])
        object_ids = [row[0] for row in cursor.fetchall()]
        if len(object_ids) > 0:
            return queryset.filter(pk__in=object_ids)
        else:
            return model._default_manager.none()

    def get_related(self, obj, queryset_or_model, num=None):
        """
        Retrieve a list of instances of the specified model which share
        tags with the model instance ``obj``, ordered by the number of
        shared tags in descending order.

        If ``num`` is given, a maximum of ``num`` instances will be
        returned.
        """
        queryset, model = get_queryset_and_model(queryset_or_model)
        model_table = qn(model._meta.db_table)
        content_type = ContentType.objects.get_for_model(obj)
        related_content_type = ContentType.objects.get_for_model(model)
        query = """
        SELECT %(model_pk)s, COUNT(related_tagged_item.object_id) AS %(count)s
        FROM %(model)s, %(tagged_item)s, %(tag)s, %(tagged_item)s related_tagged_item
        WHERE %(tagged_item)s.object_id = %%s
          AND %(tagged_item)s.content_type_id = %(content_type_id)s
          AND %(tag)s.id = %(tagged_item)s.tag_id
          AND related_tagged_item.content_type_id = %(related_content_type_id)s
          AND related_tagged_item.tag_id = %(tagged_item)s.tag_id
          AND %(model_pk)s = related_tagged_item.object_id"""
        if content_type.pk == related_content_type.pk:
            # Exclude the given instance itself if determining related
            # instances for the same model.
            query += """
          AND related_tagged_item.object_id != %(tagged_item)s.object_id"""
        query += """
        GROUP BY %(model_pk)s
        ORDER BY %(count)s DESC
        %(limit_offset)s"""
        query = query % {
            'model_pk': '%s.%s' % (model_table, qn(model._meta.pk.column)),
            'count': qn('count'),
            'model': model_table,
            'tagged_item': qn(self.model._meta.db_table),
            'tag': qn(self.model._meta.get_field('tag').rel.to._meta.db_table),
            'content_type_id': content_type.pk,
            'related_content_type_id': related_content_type.pk,
            'limit_offset': num is not None and connection.ops.limit_offset_sql(num) or '',
        }

        cursor = connection.cursor()
        cursor.execute(query, [obj.pk])
        object_ids = [row[0] for row in cursor.fetchall()]
        if len(object_ids) > 0:
            # Use in_bulk here instead of an id__in lookup, because id__in would
            # clobber the ordering.
            object_dict = queryset.in_bulk(object_ids)
            return [object_dict[object_id] for object_id in object_ids \
                    if object_id in object_dict]
        else:
            return []


##########
# Models #
##########
def create_intermediary_table_model(model):
    """Create an intermediary table model for the specific tag model"""
    name = model.__name__ + 'Relation'
     
    class Meta:
        db_table = '%s_relation' % model._meta.db_table
        unique_together = (('tag', 'content_type', 'object_id'),)

    def obj_unicode(self):
        return u'%s [%s]' % (self.content_type.get_object_for_this_type(pk=self.object_id), self.tag)
        
    # Set up a dictionary to simulate declarations within a class    
    attrs = {
        '__module__': model.__module__,
        'Meta': Meta,
        'tag': models.ForeignKey(model, verbose_name=_('tag'), related_name='items'),
        'content_type': models.ForeignKey(ContentType, verbose_name=_('content type')),
        'object_id': models.PositiveIntegerField(_('object id'), db_index=True),
        'content_object': generic.GenericForeignKey('content_type', 'object_id'),
        '__unicode__': obj_unicode,
    }

    return type(name, (models.Model,), attrs)


class TagMeta(ModelBase):
    "Metaclass for tag models (models inheriting from TagBase)."
    def __new__(cls, name, bases, attrs):
        model = super(TagMeta, cls).__new__(cls, name, bases, attrs)
        if not model._meta.abstract:
            # Create an intermediary table and register custom managers for concrete models
            model.intermediary_table_model = create_intermediary_table_model(model)
            TagManager(model.intermediary_table_model).contribute_to_class(model, 'objects')
            TaggedItemManager(model).contribute_to_class(model.intermediary_table_model, 'objects')
        return model


class TagBase(models.Model):
    """Abstract class to be inherited by model classes."""
    __metaclass__ = TagMeta
    
    class Meta:
        abstract = True
    
    @staticmethod
    def get_tag_list(tag_list):
        """
        Utility function for accepting tag input in a flexible manner.
        
        You should probably override this method in your subclass.
        """
        if isinstance(tag_list, TagBase):
            return [tag_list]
        else:
            return tag_list

