# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.auth.decorators import permission_required
from django.utils.datastructures import SortedDict
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator
from picture.models import Picture
from catalogue.utils import split_tags

# was picture/picture_list.html list (without thumbs)
def picture_list(request, filter=None, get_filter=None, template_name='catalogue/picture_list.html', cache_key=None, context=None):
    """ generates a listing of all books, optionally filtered with a test function """

    if get_filter:
        filt = get_filter()
    pictures_by_author, orphans = Picture.picture_list(filt)
    books_nav = SortedDict()
    for tag in pictures_by_author:
        if pictures_by_author[tag]:
            books_nav.setdefault(tag.sort_key[0], []).append(tag)

    return render_to_response(template_name, locals(),
        context_instance=RequestContext(request))


def picture_list_thumb(request, filter=None, get_filter=None, template_name='picture/picture_list_thumb.html', cache_key=None, context=None):
    book_list = Picture.objects.all()
    if filter:
        book_list = book_list.filter(filter)
    if get_filter:
        book_list = book_list.filter(get_filter())
    book_list = book_list.order_by('sort_key_author')
    book_list = list(book_list)
    return render_to_response(template_name, locals(),
                              context_instance=RequestContext(request))

def picture_detail(request, slug):
    picture = get_object_or_404(Picture, slug=slug)

    theme_things = split_tags(picture.related_themes())

    # categories = SortedDict()
    # for tag in picture.tags.iterator():
    #     categories.setdefault(tag.category, []).append(tag)

    themes = theme_things.get('theme', [])
    things = theme_things.get('thing', [])

    extra_info = picture.extra_info

    return render_to_response("picture/picture_detail.html", locals(),
                              context_instance=RequestContext(request))


def picture_viewer(request, slug):
    picture = get_object_or_404(Picture, slug=slug)
    return render_to_response("picture/picture_viewer.html", locals(),
                              context_instance=RequestContext(request))
                              

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
            return HttpResponse(_("An error occurred: %(exception)s\n\n%(tb)s") % {'exception':exception, 'tb':tb}, mimetype='text/plain')
        return HttpResponse(_("Picture imported successfully"))
    else:
        return HttpResponse(_("Error importing file: %r") % import_form.errors)


