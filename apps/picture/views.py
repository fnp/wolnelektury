from picture.models import Picture
from django.utils.datastructures import SortedDict
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext


def picture_list(request, filter=None, template_name='catalogue/picture_list.html'):
    """ generates a listing of all books, optionally filtered with a test function """

    pictures_by_author, orphans = Picture.picture_list()
    books_nav = SortedDict()
    for tag in pictures_by_author:
        if pictures_by_author[tag]:
            books_nav.setdefault(tag.sort_key[0], []).append(tag)

            #    import pdb; pdb.set_trace()
    return render_to_response(template_name, locals(),
        context_instance=RequestContext(request))


def picture_detail(request, picture):
    picture = get_object_or_404(Picture, slug=picture)

    categories = SortedDict()
    for tag in picture.tags:
        categories.setdefault(tag.category, []).append(tag)

    picture_themes = []

    return render_to_response("catalogue/picture_detail.html", locals(),
                              context_instance=RequestContext(request))
