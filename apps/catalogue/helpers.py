from django.db import connection
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import get_language
from picture.models import Picture, PictureArea
from catalogue.models import Fragment, Tag, Book


def _get_tag_relations_sql(tags):
    select = """
        SELECT Rx.object_id, Rx.content_type_id
        FROM catalogue_tag_relation Rx"""
    joins = []
    where = ['WHERE Rx.tag_id = %d' % tags[0].pk]
    for i, tag in enumerate(tags[1:]):
        joins.append('INNER JOIN catalogue_tag_relation TR%(i)d '
            'ON TR%(i)d.object_id = Rx.object_id '
            'AND TR%(i)d.content_type_id = Rx.content_type_id' % {'i': i})
        where.append('AND TR%d.tag_id = %d' % (i, tag.pk))
    return " ".join([select] + joins + where)



def get_related_tags(tags):
    # Get Tag fields for constructing tags in a raw query.
    tag_fields = ('id', 'category', 'slug', 'sort_key', 'name_%s' % get_language())
    tag_fields = ', '.join(
            'T.%s' % connection.ops.quote_name(field)
        for field in tag_fields)
    tag_ids = tuple(t.pk for t in tags)

    # This is based on fragments/areas sharing their works tags
    qs = Tag.objects.raw('''
        SELECT ''' + tag_fields + ''', COUNT(T.id) count
        FROM (
            -- R: TagRelations of all objects tagged with the given tags.
            WITH R AS (
                ''' + _get_tag_relations_sql(tags) + '''
            )

            SELECT ''' + tag_fields + ''', MAX(R4.object_id) ancestor

            FROM R R1

            -- R2: All tags of the found objects.
            JOIN catalogue_tag_relation R2
                ON R2.object_id = R1.object_id
                    AND R2.content_type_id = R1.content_type_id

            -- Tag data for output.
            JOIN catalogue_tag T
                ON T.id=R2.tag_id

            -- Special case for books:
            -- We want to exclude from output all the relations
            -- between a book and a tag, if there's a relation between
            -- the the book's ancestor and the tag in the result.
            LEFT JOIN catalogue_book_ancestor A
                ON A.from_book_id = R1.object_id
                    AND R1.content_type_id = %s
            LEFT JOIN catalogue_tag_relation R3
                ON R3.tag_id = R2.tag_id
                    AND R3.content_type_id = R1.content_type_id
                    AND R3.object_id = A.to_book_id
            LEFT JOIN R R4
                ON R4.object_id = R3.object_id
                AND R4.content_type_id = R3.content_type_id

            WHERE
                -- Exclude from the result the tags we started with.
                R2.tag_id NOT IN %s
                -- Special case for books: exclude descendants.
                -- AND R4.object_id IS NULL
                AND (
                    -- Only count fragment tags on fragments
                    -- and book tags for books.
                    (R2.content_type_id IN %s AND T.category IN %s)
                    OR
                    (R2.content_type_id IN %s AND T.category IN %s)
                )

            GROUP BY T.id, R2.object_id, R2.content_type_id

        ) T
        -- Now group by tag and count occurencies.
        WHERE ancestor IS NULL
        GROUP BY ''' + tag_fields + '''
        ORDER BY T.sort_key
        ''', params=(
            ContentType.objects.get_for_model(Book).pk,
            tag_ids,
            tuple(ContentType.objects.get_for_model(model).pk
                for model in (Fragment, PictureArea)),
            ('theme', 'object'),
            tuple(ContentType.objects.get_for_model(model).pk
                for model in (Book, Picture)),
            ('author', 'epoch', 'genre', 'kind'),
        ))
    return qs


def get_fragment_related_tags(tags):
    tag_fields = ', '.join(
        'T.%s' % (connection.ops.quote_name(field.column))
        for field in Tag._meta.fields)

    tag_ids = tuple(t.pk for t in tags)
        # This is based on fragments/areas sharing their works tags
    return Tag.objects.raw('''
        SELECT T.*, COUNT(T.id) count
        FROM (

            SELECT T.*

            -- R1: TagRelations of all objects tagged with the given tags.
            FROM (
                ''' + _get_tag_relations_sql(tags) + '''
            ) R1

            -- R2: All tags of the found objects.
            JOIN catalogue_tag_relation R2
                ON R2.object_id = R1.object_id
                    AND R2.content_type_id = R1.content_type_id

            -- Tag data for output.
            JOIN catalogue_tag T
                ON T.id = R2.tag_id

            WHERE
                -- Exclude from the result the tags we started with.
                R2.tag_id NOT IN %s
            GROUP BY T.id, R2.object_id, R2.content_type_id

        ) T
        -- Now group by tag and count occurencies.
        GROUP BY ''' + tag_fields + '''
        ORDER BY T.sort_key
        ''', params=(
            tag_ids,
        ))


def tags_usage_for_books(categories):
    tag_fields = ', '.join(
            'T.%s' % (connection.ops.quote_name(field.column))
        for field in Tag._meta.fields)

    # This is based on fragments/areas sharing their works tags
    return Tag.objects.raw('''
        SELECT T.*, COUNT(T.id) count
        FROM (
            SELECT T.*

            FROM catalogue_tag_relation R1

            -- Tag data for output.
            JOIN catalogue_tag T
                ON T.id=R1.tag_id

            -- We want to exclude from output all the relations
            -- between a book and a tag, if there's a relation between
            -- the the book's ancestor and the tag in the result.
            LEFT JOIN catalogue_book_ancestor A
                ON A.from_book_id=R1.object_id
            LEFT JOIN catalogue_tag_relation R3
                ON R3.tag_id = R1.tag_id
                    AND R3.content_type_id = R1.content_type_id
                    AND R3.object_id = A.to_book_id

            WHERE
                R1.content_type_id = %s
                -- Special case for books: exclude descendants.
                AND R3.object_id IS NULL
                AND T.category IN %s

            -- TODO:
            -- Shouldn't it just be 'distinct'?
            -- Maybe it's faster this way.
            GROUP BY T.id, R1.object_id, R1.content_type_id

        ) T
        -- Now group by tag and count occurencies.
        GROUP BY ''' + tag_fields + '''
        ORDER BY T.sort_key
        ''', params=(
            ContentType.objects.get_for_model(Book).pk,
            tuple(categories),
        ))


def tags_usage_for_works(categories):
    tag_fields = ', '.join(
            'T.%s' % (connection.ops.quote_name(field.column))
        for field in Tag._meta.fields)

    return Tag.objects.raw('''
        SELECT T.*, COUNT(T.id) count
        FROM (

            SELECT T.*

            FROM catalogue_tag_relation R1

            -- Tag data for output.
            JOIN catalogue_tag T
                ON T.id = R1.tag_id

            -- Special case for books:
            -- We want to exclude from output all the relations
            -- between a book and a tag, if there's a relation between
            -- the the book's ancestor and the tag in the result.
            LEFT JOIN catalogue_book_ancestor A
                ON A.from_book_id = R1.object_id
                    AND R1.content_type_id = %s
            LEFT JOIN catalogue_tag_relation R3
                ON R3.tag_id = R1.tag_id
                    AND R3.content_type_id = R1.content_type_id
                    AND R3.object_id = A.to_book_id

            WHERE
                R1.content_type_id IN %s
                -- Special case for books: exclude descendants.
                AND R3.object_id IS NULL
                AND T.category IN %s

            -- TODO:
            -- Shouldn't it just be 'distinct'?
            -- Maybe it's faster this way.
            GROUP BY T.id, R1.object_id, R1.content_type_id

        ) T
        -- Now group by tag and count occurencies.
        GROUP BY ''' + tag_fields + '''
        ORDER BY T.sort_key
       
        ''', params=(
            ContentType.objects.get_for_model(Book).pk,
            tuple(ContentType.objects.get_for_model(model).pk for model in (Book, Picture)),
            categories,
        ))


def tags_usage_for_fragments(categories):
    return Tag.objects.raw('''
        SELECT t.*, count(t.id)
        from catalogue_tag_relation r
        join catalogue_tag t
            on t.id = r.tag_id
        where t.category IN %s
        group by t.id
        order by t.sort_key
        ''', params=(
            categories,
        ))
