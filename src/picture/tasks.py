# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
from celery import shared_task
from django.core.files.base import ContentFile
from django.template.loader import render_to_string


@shared_task
def generate_picture_html(picture_id):
    import picture.models
    pic = picture.models.Picture.objects.get(pk=picture_id)
    areas_json = json.loads(pic.areas_json)

    html_text = render_to_string('picture/picture_info.html', {
                'things': areas_json['things'],
                'themes': areas_json['themes'],
                })
    pic.html_file.save("%s.html" % pic.slug, ContentFile(html_text))
