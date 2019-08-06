# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models

from sortify import sortify


def update_sort_keys(apps, schema_editor):
    Tag = apps.get_model('catalogue', 'Tag')
    Book = apps.get_model('catalogue', 'Book')
    Picture = apps.get_model('picture', 'Picture')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    for author in Tag.objects.filter(category='author'):
        name_parts = author.name.split()
        sort_key = ' '.join([name_parts[-1]] + name_parts[:-1])
        author.sort_key = sortify(sort_key.lower())
        author.save()
    for model in Book, Picture:
        ct = ContentType.objects.get_for_model(model)
        for obj in model.objects.all():
            authors = Tag.objects.filter(category='author', items__content_type=ct, items__object_id=obj.id)
            author = authors[0]
            obj.sort_key_author = author.sort_key
            obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0008_auto_20151221_1225'),
        ('picture', '0007_auto_20160125_1709'),
    ]

    operations = [
        migrations.RunPython(update_sort_keys),
    ]
