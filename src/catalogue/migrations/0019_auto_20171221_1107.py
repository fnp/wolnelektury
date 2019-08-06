# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


def init_tag_for_books_pictures(apps, schema_editor):
    Tag = apps.get_model('catalogue', 'Tag')
    db_alias = schema_editor.connection.alias
    tag_objects = Tag.objects.using(db_alias).exclude(category='set')
    tags_for_books = tag_objects.filter(items__content_type__model__in=('book', 'fragment')).distinct()
    tags_for_books.update(for_books=True)
    tags_for_pictures = tag_objects.filter(items__content_type__model__in=('picture', 'picturearea')).distinct()
    tags_for_pictures.update(for_pictures=True)


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0018_auto_20171221_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='for_books',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tag',
            name='for_pictures',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(init_tag_for_books_pictures, migrations.RunPython.noop)
    ]
