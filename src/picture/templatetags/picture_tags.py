# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import logging
from random import randint
from django import template
from django.urls import reverse
from django.utils.cache import add_never_cache_headers
import sorl.thumbnail.default
from catalogue.utils import split_tags
from ..engine import CustomCroppingEngine
from ..models import Picture


register = template.Library()

cropper = CustomCroppingEngine()


@register.simple_tag()
def area_thumbnail_url(area, geometry):
    def to_square(coords):
        w = coords[1][0] - coords[0][0]
        h = coords[1][1] - coords[0][1]
        if w == h:
            return coords
        elif w > h:
            return [[coords[0][0] + w/2 - h/2, coords[0][1]],
                    [coords[1][0] - w/2 + h/2, coords[1][1]]]
        else:
            return [[coords[0][0], coords[0][1] + h/2 - w/2],
                    [coords[1][0], coords[1][1] - h/2 + w/2, ]]

    # so much for sorl extensibility.
    # what to do about this?
    _engine = sorl.thumbnail.default.engine
    sorl.thumbnail.default.engine = cropper
    coords = to_square(area.get_area_json())

    try:
        th = sorl.thumbnail.default.backend.get_thumbnail(
            area.picture.image_file,
            geometry,
            crop="%dpx %dpx %dpx %dpx" % tuple(map(lambda d: max(0, d), tuple(coords[0] + coords[1]))))
    except ZeroDivisionError:
        return ''
    except Exception as e:
        logging.exception("Error creating a thumbnail for PictureArea")
        return ''

    sorl.thumbnail.default.engine = _engine

    return th.url


@register.simple_tag
def picture_random_picture(exclude_ids):
    queryset = Picture.objects.exclude(pk__in=exclude_ids).exclude(image_file='')
    count = queryset.count()
    if count:
        return queryset[randint(0, count - 1)]
    else:
        return None
