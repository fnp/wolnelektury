# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def rebuild_extra_info(apps, schema_editor):
    Picture = apps.get_model("picture", "Picture")
    from librarian.picture import PictureInfo
    from librarian import dcparser
    for pic in Picture.objects.all():
        info = dcparser.parse(pic.xml_file.path, PictureInfo)
        pic.extra_info = info.to_dict()
        pic.save()


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0004_auto_20141016_1337'),
    ]

    operations = [
        migrations.RunPython(rebuild_extra_info),
    ]
