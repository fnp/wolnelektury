# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
#~ from django.utils.datastructures import SortedDict
from django.views.decorators.http import require_POST
#~ from django.contrib import auth
#~ from django.views.decorators import cache
from django.utils.translation import ugettext as _

from ajaxable.utils import LazyEncoder, JSONResponse, AjaxableFormView

from catalogue.models import Book, Tag
from social import forms
from social.utils import get_set, likes, set_sets


# ====================
# = Shelf management =
# ====================


@require_POST
def like_book(request, slug):
    if not request.user.is_authenticated():
        return HttpResponseForbidden('Login required.')
    book = get_object_or_404(Book, slug=slug)
    if not likes(request.user, book):
        tag = get_set(request.user, '')
        set_sets(request.user, book, [tag])

    if request.is_ajax():
        return JSONResponse({"success": True, "msg": "ok", "like": True})
    else:
        return redirect(book)


@login_required
def my_shelf(request):
    books = Book.tagged.with_any(request.user.tag_set.all())
    return render(request, 'social/my_shelf.html', locals())


class ObjectSetsFormView(AjaxableFormView):
    form_class = forms.ObjectSetsForm
    placeholdize = True
    template = 'social/sets_form.html'
    ajax_redirect = True
    POST_login = True

    def get_object(self, request, slug):
        return get_object_or_404(Book, slug=slug)

    def context_description(self, request, obj):
        return obj.pretty_title()

    def form_args(self, request, obj):
        return (obj, request.user), {}


def unlike_book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if likes(request.user, book):
        set_sets(request.user, book, [])

    if request.is_ajax():
        return JSONResponse({"success": True, "msg": "ok", "like": False})
    else:
        return redirect(book)


#~ @login_required
#~ @cache.never_cache
#~ def user_shelves(request):
    #~ shelves = models.Tag.objects.filter(category='set', user=request.user)
    #~ new_set_form = forms.NewSetForm()
    #~ return render_to_response('social/user_shelves.html', locals(),
            #~ context_instance=RequestContext(request))
#~ 
#~ @cache.never_cache
#~ def book_sets(request, slug):
    #~ if not request.user.is_authenticated():
        #~ return HttpResponse(_('<p>To maintain your shelves you need to be logged in.</p>'))
#~ 
    #~ book = get_object_or_404(models.Book, slug=slug)
#~ 
    #~ user_sets = models.Tag.objects.filter(category='set', user=request.user)
    #~ book_sets = book.tags.filter(category='set', user=request.user)
#~ 
    #~ if request.method == 'POST':
        #~ form = forms.ObjectSetsForm(book, request.user, request.POST)
        #~ if form.is_valid():
            #~ DONE!
            #~ if request.is_ajax():
                #~ return JSONResponse('{"msg":"'+_("<p>Shelves were sucessfully saved.</p>")+'", "after":"close"}')
            #~ else:
                #~ return HttpResponseRedirect('/')
    #~ else:
        #~ form = forms.ObjectSetsForm(book, request.user)
        #~ new_set_form = forms.NewSetForm()
#~ 
    #~ return render_to_response('social/book_sets.html', locals(),
        #~ context_instance=RequestContext(request))
#~ 
#~ 
#~ @login_required
#~ @require_POST
#~ @cache.never_cache
#~ def remove_from_shelf(request, shelf, slug):
    #~ book = get_object_or_404(models.Book, slug=slug)
#~ 
    #~ shelf = get_object_or_404(models.Tag, slug=shelf, category='set', user=request.user)
#~ 
    #~ if shelf in book.tags:
        #~ models.Tag.objects.remove_tag(book, shelf)
        #~ touch_tag(shelf)
#~ 
        #~ return HttpResponse(_('Book was successfully removed from the shelf'))
    #~ else:
        #~ return HttpResponse(_('This book is not on the shelf'))
#~ 
#~ 
#~ def collect_books(books):
    #~ """
    #~ Returns all real books in collection.
    #~ """
    #~ result = []
    #~ for book in books:
        #~ if len(book.children.all()) == 0:
            #~ result.append(book)
        #~ else:
            #~ result += collect_books(book.children.all())
    #~ return result
#~ 
#~ 
#~ @cache.never_cache
#~ def download_shelf(request, slug):
    #~ """"
    #~ Create a ZIP archive on disk and transmit it in chunks of 8KB,
    #~ without loading the whole file into memory. A similar approach can
    #~ be used for large dynamic PDF files.
    #~ """
    #~ from slughifi import slughifi
    #~ import tempfile
    #~ import zipfile
#~ 
    #~ shelf = get_object_or_404(models.Tag, slug=slug, category='set')
#~ 
    #~ formats = []
    #~ form = forms.DownloadFormatsForm(request.GET)
    #~ if form.is_valid():
        #~ formats = form.cleaned_data['formats']
    #~ if len(formats) == 0:
        #~ formats = models.Book.ebook_formats
#~ 
    #~ # Create a ZIP archive
    #~ temp = tempfile.TemporaryFile()
    #~ archive = zipfile.ZipFile(temp, 'w')
#~ 
    #~ for book in collect_books(models.Book.tagged.with_all(shelf)):
        #~ for ebook_format in models.Book.ebook_formats:
            #~ if ebook_format in formats and book.has_media(ebook_format):
                #~ filename = book.get_media(ebook_format).path
                #~ archive.write(filename, str('%s.%s' % (book.slug, ebook_format)))
    #~ archive.close()
#~ 
    #~ response = HttpResponse(content_type='application/zip', mimetype='application/x-zip-compressed')
    #~ response['Content-Disposition'] = 'attachment; filename=%s.zip' % slughifi(shelf.name)
    #~ response['Content-Length'] = temp.tell()
#~ 
    #~ temp.seek(0)
    #~ response.write(temp.read())
    #~ return response
#~ 
#~ 
#~ @cache.never_cache
#~ def shelf_book_formats(request, shelf):
    #~ """"
    #~ Returns a list of formats of books in shelf.
    #~ """
    #~ shelf = get_object_or_404(models.Tag, slug=shelf, category='set')
#~ 
    #~ formats = {}
    #~ for ebook_format in models.Book.ebook_formats:
        #~ formats[ebook_format] = False
#~ 
    #~ for book in collect_books(models.Book.tagged.with_all(shelf)):
        #~ for ebook_format in models.Book.ebook_formats:
            #~ if book.has_media(ebook_format):
                #~ formats[ebook_format] = True
#~ 
    #~ return HttpResponse(LazyEncoder().encode(formats))
#~ 
#~ 
#~ @login_required
#~ @require_POST
#~ @cache.never_cache
#~ def new_set(request):
    #~ new_set_form = forms.NewSetForm(request.POST)
    #~ if new_set_form.is_valid():
        #~ new_set = new_set_form.save(request.user)
#~ 
        #~ if request.is_ajax():
            #~ return JSONResponse('{"id":"%d", "name":"%s", "msg":"<p>Shelf <strong>%s</strong> was successfully created</p>"}' % (new_set.id, new_set.name, new_set))
        #~ else:
            #~ return HttpResponseRedirect('/')
#~ 
    #~ return HttpResponseRedirect('/')
#~ 
#~ 
#~ @login_required
#~ @require_POST
#~ @cache.never_cache
#~ def delete_shelf(request, slug):
    #~ user_set = get_object_or_404(models.Tag, slug=slug, category='set', user=request.user)
    #~ user_set.delete()
#~ 
    #~ if request.is_ajax():
        #~ return HttpResponse(_('<p>Shelf <strong>%s</strong> was successfully removed</p>') % user_set.name)
    #~ else:
        #~ return HttpResponseRedirect('/')
