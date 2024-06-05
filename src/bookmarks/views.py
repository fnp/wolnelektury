from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators import cache
import catalogue.models
from wolnelektury.utils import is_ajax
from . import models
from lxml import html
import re


# login required

@cache.never_cache
def bookmarks(request):
    try:
        slug = request.headers['Referer'].rsplit('.', 1)[0].rsplit('/', 1)[-1]
    except:
        slug = 'w-80-dni-dookola-swiata'
#        raise Http404()            
    try:
        book = catalogue.models.Book.objects.get(slug=slug)
    except catalogue.models.Book.DoesNotExist:
        raise Http404()

    if request.method == 'POST':
        # TODO test
        bm, created = models.Bookmark.objects.update_or_create(
            user=request.user,
            book=book,
            anchor=request.POST.get('anchor', ''),
            defaults={
                'note': request.POST.get('note', ''),
            }
        )
        return JsonResponse(bm.get_for_json())
    else:
        return JsonResponse({
            bm.anchor: bm.get_for_json()
            for bm in models.Bookmark.objects.filter(
                    user=request.user,
                    book=book,
            )
        })


def bookmark(request, uuid):
    bm = get_object_or_404(models.Bookmark, user=request.user, uuid=uuid)
    if request.method == 'POST':
        bm.note = request.POST.get('note', '')
        bm.save()
    return JsonResponse(bm.get_for_json())


def bookmark_delete(request, uuid):
    models.Bookmark.objects.filter(user=request.user, uuid=uuid).delete()
    return JsonResponse({})




@cache.never_cache
def quotes(request):
    try:
        slug = request.headers['Referer'].rsplit('.', 1)[0].rsplit('/', 1)[-1]
    except:
        slug = 'w-80-dni-dookola-swiata'
#        raise Http404()            
    try:
        book = catalogue.models.Book.objects.get(slug=slug)
    except catalogue.models.Book.DoesNotExist:
        raise Http404()

    if request.method == 'POST':
        # TODO test
        # ensure unique? or no?

        text = request.POST.get('text', '')
        text = text.strip()

        stext = re.sub(r'\s+', ' ', text)
        ## verify
        print(text)
        

        # find out
        with book.html_file.open('r') as f:
            ht = f.read()
        tree = html.fromstring(ht)
        # TODO: clear
        for sel in ('.//a[@class="theme-begin"]',
                    './/a[@class="anchor"]',
                    ):
            for e in tree.xpath(sel):
                e.clear(keep_tail=True)
        htext = html.tostring(tree, encoding='unicode', method='text')
        htext = re.sub(r'\s+', ' ', htext)

        print(htext)

        otext = stext
        if stext not in htext:
            # raise 401
            raise Http404()            

        # paths?
        # start elem?
        q = models.Quote.objects.create(
            user=request.user,
            book=book,
            start_elem=request.POST.get('startElem', ''),
            end_elem=request.POST.get('startElem', ''),
            start_offset=request.POST.get('startOffset', None),
            end_offset=request.POST.get('startOffset', None),
            text=text,
        )
        return JsonResponse(q.get_for_json())
    else:
        return JsonResponse({
            q.start_elem: q.get_for_json()
            for q in models.Quote.objects.filter(
                    user=request.user,
                    book=book,
            )
        })



def quote(request, uuid):
    q = get_object_or_404(models.Quote, user=request.user, uuid=uuid)
    if is_ajax(request):
        return JsonResponse(q.get_for_json())
    else:
        return render(request, 'bookmarks/quote_detail.html', {
            'object': q,
        })


