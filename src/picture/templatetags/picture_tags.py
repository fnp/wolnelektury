# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import logging
from random import randint
from django import template
from django.core.urlresolvers import reverse
from django.utils.cache import add_never_cache_headers
import sorl.thumbnail.default
from ssify import ssi_variable
from catalogue.utils import split_tags
from ..engine import CustomCroppingEngine
from ..models import Picture


register = template.Library()

cropper = CustomCroppingEngine()


@register.inclusion_tag('picture/picture_wide.html', takes_context=True)
def picture_wide(context, picture):
    context.update({
        'picture': picture,
        'main_link': reverse('picture_viewer', args=[picture.slug]),
        'request': context.get('request'),
        'tags': split_tags(picture.tags),
        })
    return context


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
    coords = to_square(area.area)

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


@ssi_variable(register, patch_response=[add_never_cache_headers])
def picture_random_picture(request, exclude_ids, unless=None):
    if unless:
        return None
    queryset = Picture.objects.exclude(pk__in=exclude_ids).exclude(image_file='')
    count = queryset.count()
    if count:
        return queryset[randint(0, count - 1)].pk
    else:
        return None
