# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404, render
from picture.models import Picture
from catalogue.utils import split_tags
from sponsors.models import Sponsor
from wolnelektury.utils import ajax


def picture_list_thumb(request, filter=None, get_filter=None, template_name='picture/picture_list_thumb.html',
                       cache_key=None, context=None):
    pictures = Picture.objects.all()
    if filter:
        pictures = pictures.filter(filter)
    if get_filter:
        pictures = pictures.filter(get_filter())
    return render(request, template_name, {'picture_list': list(pictures)})


def picture_detail(request, slug):
    picture = get_object_or_404(Picture, slug=slug)

    theme_things = split_tags(picture.related_themes())

    return render(request, "picture/picture_detail.html", {
        'picture': picture,
        'themes': theme_things.get('theme', []),
        'things': theme_things.get('thing', []),
        'active_menu_item': 'gallery',
    })


def picture_viewer(request, slug):
    picture = get_object_or_404(Picture, slug=slug)
    sponsors = []
    for sponsor in picture.get_extra_info_json().get('sponsors', []):
        have_sponsors = Sponsor.objects.filter(name=sponsor)
        if have_sponsors.exists():
            sponsors.append(have_sponsors[0])
    return render(request, "picture/picture_viewer.html", {
        'picture': picture,
        'sponsors': sponsors,
    })


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
            'style': picture.get_extra_info_json()['style'],
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
                                {'exception': exception, 'tb': tb}, content_type='text/plain')
        return HttpResponse(_("Picture imported successfully"))
    else:
        return HttpResponse(_("Error importing file: %r") % import_form.errors)
