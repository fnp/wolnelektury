# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from traceback import print_exc

from celery.task import task
from django.core.files.base import ContentFile
from django.template.loader import render_to_string


@task
def generate_picture_html(picture_id):
    import picture.models
    pic = picture.models.Picture.objects.get(pk=picture_id)

    html_text = unicode(render_to_string('picture/picture_info.html', {
                'things': pic.areas_json['things'],
                'themes': pic.areas_json['themes'],
                }))
    pic.html_file.save("%s.html" % pic.slug, ContentFile(html_text))


@task
def index_picture(picture_id, picture_info=None, **kwargs):
    from picture.models import Picture
    try:
        return Picture.objects.get(id=picture_id).search_index(picture_info, **kwargs)
    except Exception, e:
        print "Exception during index: %s" % e
        print_exc()
        raise e
