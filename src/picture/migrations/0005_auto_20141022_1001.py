import json
from django.core.files.base import ContentFile
from django.db import models, migrations
from django.template.loader import render_to_string


def rebuild_extra_info(apps, schema_editor):
    Picture = apps.get_model("picture", "Picture")
    from librarian.picture import PictureInfo
    from librarian import dcparser
    for pic in Picture.objects.all():
        info = dcparser.parse(pic.xml_file.path, PictureInfo)
        pic.extra_info = json.dumps(info.to_dict())
        areas_json = json.loads(pic.areas_json)
        for field in areas_json['things'].values():
            field['object'] = field['object'].capitalize()
        pic.areas_json = json.dumps(areas_json)
        html_text = render_to_string('picture/picture_info.html', {
                    'things': areas_json['things'],
                    'themes': areas_json['themes'],
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
