# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext
from picture.models import Picture, PictureArea
from catalogue.utils import split_tags
from ssify import ssi_included
from sponsors.models import Sponsor


# WTF/unused
# # was picture/picture_list.html list (without thumbs)
# def picture_list(request, filter=None, get_filter=None, template_name='catalogue/picture_list.html',
#                  cache_key=None, context=None):
#     """ generates a listing of all books, optionally filtered with a test function """
#
#     if get_filter:
#         filt = get_filter()
#     pictures_by_author, orphans = Picture.picture_list(filt)
#     books_nav = OrderedDict()
#     for tag in pictures_by_author:
#         if pictures_by_author[tag]:
#             books_nav.setdefault(tag.sort_key[0], []).append(tag)
#
#     return render_to_response(template_name, locals(), context_instance=RequestContext(request))
from wolnelektury.utils import ajax


def picture_list_thumb(request, filter=None, get_filter=None, template_name='picture/picture_list_thumb.html',
                       cache_key=None, context=None):
    pictures = Picture.objects.all()
    if filter:
        pictures = pictures.filter(filter)
    if get_filter:
        pictures = pictures.filter(get_filter())
    return render_to_response(template_name, {'book_list': list(pictures)}, context_instance=RequestContext(request))


def picture_detail(request, slug):
    picture = get_object_or_404(Picture, slug=slug)

    theme_things = split_tags(picture.related_themes())

    # categories = SortedDict()
    # for tag in picture.tags.iterator():
    #     categories.setdefault(tag.category, []).append(tag)

    return render_to_response("picture/picture_detail.html", {
        'picture': picture,
        'themes': theme_things.get('theme', []),
        'things': theme_things.get('thing', []),
    }, context_instance=RequestContext(request))


def picture_viewer(request, slug):
    picture = get_object_or_404(Picture, slug=slug)
    sponsors = []
    for sponsor in picture.extra_info.get('sponsors', []):
        have_sponsors = Sponsor.objects.filter(name=sponsor)
        if have_sponsors.exists():
            sponsors.append(have_sponsors[0])
    return render_to_response("picture/picture_viewer.html", {
        'picture': picture,
        'sponsors': sponsors,
    }, context_instance=RequestContext(request))


@ajax(method='get')
def picture_page(request, key=None):
    pictures = Picture.objects.order_by('-id')
    if key is not None:
        pictures = pictures.filter(id__lt=key)
    pictures = pictures[:settings.PICTURE_PAGE_SIZE]
    picture_data = [
        {
            'id': picture.id,
            'title': picture.title,
            'author': picture.author_unicode(),
            'epoch': picture.tag_unicode('epoch'),
            'kind': picture.tag_unicode('kind'),
            'genre': picture.tag_unicode('genre'),
            'style': picture.extra_info['style'],
            'image_url': picture.image_file.url,
            'width': picture.width,
            'height': picture.height,
        }
        for picture in pictures
    ]
    return {
        'pictures': picture_data,
        'count': Picture.objects.count(),
    }


# =========
# = Admin =
# =========
@permission_required('picture.add_picture')
def import_picture(request):
    """docstring for import_book"""
    from django.http import HttpResponse
    from picture.forms import PictureImportForm
    from django.utils.translation import ugettext as _

    import_form = PictureImportForm(request.POST, request.FILES)
    if import_form.is_valid():
        try:
            import_form.save()
        except:
            import sys
            import pprint
            import traceback
            info = sys.exc_info()
            exception = pprint.pformat(info[1])
            tb = '\n'.join(traceback.format_tb(info[2]))
            return HttpResponse(_("An error occurred: %(exception)s\n\n%(tb)s") %
                                {'exception': exception, 'tb': tb}, mimetype='text/plain')
        return HttpResponse(_("Picture imported successfully"))
    else:
        return HttpResponse(_("Error importing file: %r") % import_form.errors)


@ssi_included
def picture_mini(request, pk, with_link=True):
    picture = get_object_or_404(Picture, pk=pk)
    return render(request, 'picture/picture_mini_box.html', {
        'picture': picture,
        'author': picture.author_unicode(),
        'with_link': with_link,
    })


@ssi_included
def picture_short(request, pk):
    picture = get_object_or_404(Picture, pk=pk)

    return render(request, 'picture/picture_short.html', {
        'picture': picture,
        'main_link': picture.get_absolute_url(),
        'request': request,
        'tags': split_tags(picture.tags),
        })


@ssi_included
def picturearea_short(request, pk):
    area = get_object_or_404(PictureArea, pk=pk)
    themes = area.tags.filter(category='theme')
    things = area.tags.filter(category='thing')
    return render(request, 'picture/picturearea_short.html', {
        'area': area,
        'theme': themes[0] if themes else None,
        'thing': things[0] if things else None,
    })
