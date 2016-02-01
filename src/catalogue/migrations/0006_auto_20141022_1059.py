# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def capitalize_objects(apps, schema_editor):
    """Capitalize Polish names of things."""
    Tag = apps.get_model('catalogue', 'Tag')
    for tag in Tag.objects.filter(category='thing'):
        tag.name = tag.name_pl = tag.name.capitalize()
        tag.save()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0005_auto_20141016_1337'),
    ]

    operations = [
        migrations.RunPython(capitalize_objects),
    ]
