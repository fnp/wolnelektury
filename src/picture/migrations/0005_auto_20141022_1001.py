# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.files.base import ContentFile
from django.db import models, migrations
from django.template.loader import render_to_string


def rebuild_extra_info(apps, schema_editor):
    Picture = apps.get_model("picture", "Picture")
    from librarian.picture import PictureInfo
    from librarian import dcparser
    for pic in Picture.objects.all():
        info = dcparser.parse(pic.xml_file.path, PictureInfo)
        pic.extra_info = info.to_dict()
        areas_json = pic.areas_json
        for field in areas_json[u'things'].values():
            field[u'object'] = field[u'object'].capitalize()
        pic.areas_json = areas_json
        html_text = render_to_string('picture/picture_info.html', {
                    'things': pic.areas_json['things'],
                    'themes': pic.areas_json['themes'],
                    })
        pic.html_file.save("%s.html" % pic.slug, ContentFile(html_text))
        pic.save()


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0004_auto_20141016_1337'),
    ]

    operations = [
        migrations.RunPython(rebuild_extra_info),
    ]
