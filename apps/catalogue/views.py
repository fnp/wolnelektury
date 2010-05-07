# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import tempfile
import zipfile
import sys
import pprint
import traceback

from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.datastructures import SortedDict
from django.views.decorators.http import require_POST
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import simplejson
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from django.views.decorators import cache

from catalogue import models
from catalogue import forms
from catalogue.utils import split_tags
from newtagging import views as newtagging_views


staff_required = user_passes_test(lambda user: user.is_staff)


class LazyEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj


def main_page(request):    
    if request.user.is_authenticated():
        shelves = models.Tag.objects.filter(category='set', user=request.user)
        new_set_form = forms.NewSetForm()
    extra_where = "NOT catalogue_tag.category = 'set'"
    tags = models.Tag.objects.usage_for_model(models.Book, counts=True, extra={'where': [extra_where]})
    fragment_tags = models.Tag.objects.usage_for_model(models.Fragment, counts=True,
        extra={'where': ["catalogue_tag.category = 'theme'"] + [extra_where]})
    categories = split_tags(tags)
    
    form = forms.SearchForm()
    return render_to_response('catalogue/main_page.html', locals(),
        context_instance=RequestContext(request))


def book_list(request):
    books = models.Book.objects.all()
    form = forms.SearchForm()
    
    books_by_first_letter = SortedDict()
    for book in books:
        books_by_first_letter.setdefault(book.title[0], []).append(book)
    
    return render_to_response('catalogue/book_list.html', locals(),
        context_instance=RequestContext(request))


def tagged_object_list(request, tags=''):
    # Prevent DoS attacks on our database
    if len(tags.split('/')) > 6:
        raise Http404
        
    try:
        tags = models.Tag.get_tag_list(tags)
    except models.Tag.DoesNotExist:
        raise Http404
    
    if len([tag for tag in tags if tag.category == 'book']):
        raise Http404
    
    model = models.Book
    shelf = [tag for tag in tags if tag.category == 'set']
    shelf_is_set = (len(tags) == 1 and tags[0].category == 'set')
    theme_is_set = len([tag for tag in tags if tag.category == 'theme']) > 0
    if theme_is_set:
        model = models.Fragment
    only_author = len(tags) == 1 and tags[0].category == 'author'
    pd_counter = only_author and tags[0].goes_to_pd()

    user_is_owner = (len(shelf) and request.user.is_authenticated() and request.user == shelf[0].user)
    
    extra_where = "catalogue_tag.category NOT IN ('set', 'book')"
    related_tags = models.Tag.objects.related_for_model(tags, model, counts=True, extra={'where': [extra_where]})
    categories = split_tags(related_tags)

    if not (theme_is_set or shelf_is_set):
        model=models.Book.objects.filter(parent=None)
    
    return newtagging_views.tagged_object_list(
        request,
        tag_model=models.Tag,
        queryset_or_model=model,
        tags=tags,
        template_name='catalogue/tagged_object_list.html',
        extra_context = {
            'categories': categories,
            'shelf_is_set': shelf_is_set,
            'only_author': only_author,
            'pd_counter': pd_counter,
            'user_is_owner': user_is_owner,
            'formats_form': forms.DownloadFormatsForm(),
        },
    )


def book_fragments(request, book_slug, theme_slug):
    book = get_object_or_404(models.Book, slug=book_slug)
    book_tag = get_object_or_404(models.Tag, slug='l-' + book_slug)
    theme = get_object_or_404(models.Tag, slug=theme_slug)
    fragments = models.Fragment.tagged.with_all([book_tag, theme])
    
    form = forms.SearchForm()
    return render_to_response('catalogue/book_fragments.html', locals(),
        context_instance=RequestContext(request))


def book_detail(request, slug):
    try:
        book = models.Book.objects.get(slug=slug)
    except models.Book.DoesNotExist:
        return book_stub_detail(request, slug)

    book_tag = get_object_or_404(models.Tag, slug = 'l-' + slug)
    tags = list(book.tags.filter(~Q(category='set')))
    categories = split_tags(tags)
    book_children = book.children.all().order_by('parent_number')
    extra_where = "catalogue_tag.category = 'theme'"
    book_themes = models.Tag.objects.related_for_model(book_tag, models.Fragment, counts=True, extra={'where': [extra_where]})
    extra_info = book.get_extra_info_value()
    
    form = forms.SearchForm()
    return render_to_response('catalogue/book_detail.html', locals(),
        context_instance=RequestContext(request))


def book_stub_detail(request, slug):
    book = get_object_or_404(models.BookStub, slug=slug)
    pd_counter = book.pd
    form = forms.SearchForm()
    
    return render_to_response('catalogue/book_stub_detail.html', locals(),
        context_instance=RequestContext(request))
    

def book_text(request, slug):
    book = get_object_or_404(models.Book, slug=slug)
    book_themes = {}
    for fragment in book.fragments.all():
        for theme in fragment.tags.filter(category='theme'):
            book_themes.setdefault(theme, []).append(fragment)
    
    book_themes = book_themes.items()
    book_themes.sort(key=lambda s: s[0].sort_key)
    return render_to_response('catalogue/book_text.html', locals(),
        context_instance=RequestContext(request))


# ==========
# = Search =
# ==========
def _word_starts_with(name, prefix):
    """returns a Q object gettings models having `name` contain a word
    starting with `prefix`
    """
    kwargs = {}
    if settings.DATABASE_ENGINE in ('mysql', 'postgresql_psycopg2', 'postgresql'):
        # we must escape `prefix` so that it only matches literally
        for special in r'\^$.*+?|(){}[]':
            prefix = prefix.replace(special, '\\' + special)
        
        # we could use a [[:<:]] (word start), 
        # but we want both `xy` and `(xy` to catch `(xyz)`
        kwargs['%s__iregex' % name] = u"(^|[^[:alpha:]])%s" % prefix
    else:
        # don't know how to do a generic regex
        # checking for simple icontain instead
        kwargs['%s__icontains' % name] = prefix
    return Q(**kwargs)


def _tags_starting_with(prefix, user):
    book_stubs = models.BookStub.objects.filter(_word_starts_with('title', prefix))
    books = models.Book.objects.filter(_word_starts_with('title', prefix))
    book_stubs = filter(lambda x: x not in books, book_stubs)
    tags = models.Tag.objects.filter(_word_starts_with('name', prefix))
    if user.is_authenticated():
        tags = tags.filter(~Q(category='book') & (~Q(category='set') | Q(user=user)))
    else:
        tags = tags.filter(~Q(category='book') & ~Q(category='set'))

    return list(books) + list(tags) + list(book_stubs)
        

def search(request):
    tags = request.GET.get('tags', '')
    prefix = request.GET.get('q', '')
    # Prefix must have at least 2 characters
    if len(prefix) < 2:
        return HttpResponse('')
    
    try:
        tag_list = models.Tag.get_tag_list(tags)
    except:
        tag_list = []
    
    result = _tags_starting_with(prefix, request.user)
    if len(result) > 0:
        tag = result[0]
        if isinstance(tag, models.Book) or isinstance(tag, models.BookStub):
            return HttpResponseRedirect(tag.get_absolute_url())
        else:
            tag_list.append(tag)
            
            return HttpResponseRedirect(reverse('catalogue.views.tagged_object_list', 
                kwargs={'tags': '/'.join(tag.slug for tag in tag_list)}
            ))
    else:
        return render_to_response('catalogue/search_no_hits.html', {'query':prefix, 'tags':tag_list},
            context_instance=RequestContext(request))


def tags_starting_with(request):
    prefix = request.GET.get('q', '')
    # Prefix must have at least 2 characters
    if len(prefix) < 2:
        return HttpResponse('')
    
    return HttpResponse('\n'.join(tag.name for tag in _tags_starting_with(prefix, request.user)))


# ====================
# = Shelf management =
# ====================
@login_required
@cache.never_cache
def user_shelves(request):
    shelves = models.Tag.objects.filter(category='set', user=request.user)
    new_set_form = forms.NewSetForm()
    return render_to_response('catalogue/user_shelves.html', locals(),
            context_instance=RequestContext(request))

@cache.never_cache
def book_sets(request, slug):
    book = get_object_or_404(models.Book, slug=slug)
    user_sets = models.Tag.objects.filter(category='set', user=request.user)
    book_sets = book.tags.filter(category='set', user=request.user)
    
    if not request.user.is_authenticated():
        return HttpResponse('<p>Aby zarządzać swoimi półkami, musisz się zalogować.</p>')
    
    if request.method == 'POST':
        form = forms.ObjectSetsForm(book, request.user, request.POST)
        if form.is_valid():
            old_shelves = list(book.tags.filter(category='set'))
            new_shelves = [models.Tag.objects.get(pk=id) for id in form.cleaned_data['set_ids']]
            
            for shelf in [shelf for shelf in old_shelves if shelf not in new_shelves]:
                shelf.book_count -= 1
                shelf.save()
                
            for shelf in [shelf for shelf in new_shelves if shelf not in old_shelves]:
                shelf.book_count += 1
                shelf.save()
            
            book.tags = new_shelves + list(book.tags.filter(~Q(category='set') | ~Q(user=request.user)))
            if request.is_ajax():
                return HttpResponse('<p>Półki zostały zapisane.</p>')
            else:
                return HttpResponseRedirect('/')
    else:
        form = forms.ObjectSetsForm(book, request.user)
        new_set_form = forms.NewSetForm()
    
    return render_to_response('catalogue/book_sets.html', locals(),
        context_instance=RequestContext(request))


@login_required
@require_POST
@cache.never_cache
def remove_from_shelf(request, shelf, book):
    book = get_object_or_404(models.Book, slug=book)
    shelf = get_object_or_404(models.Tag, slug=shelf, category='set', user=request.user)
    
    models.Tag.objects.remove_tag(book, shelf)
    
    shelf.book_count -= 1
    shelf.save()
    
    return HttpResponse('Usunieto')


def collect_books(books):
    """
    Returns all real books in collection.
    """
    result = []
    for book in books:
        if len(book.children.all()) == 0:
            result.append(book)
        else:
            result += collect_books(book.children.all())
    return result


@cache.never_cache
def download_shelf(request, slug):
    """"
    Create a ZIP archive on disk and transmit it in chunks of 8KB,
    without loading the whole file into memory. A similar approach can
    be used for large dynamic PDF files.                                        
    """
    shelf = get_object_or_404(models.Tag, slug=slug, category='set')
    
    formats = []
    form = forms.DownloadFormatsForm(request.GET)
    if form.is_valid():
        formats = form.cleaned_data['formats']
    if len(formats) == 0:
        formats = ['pdf', 'odt', 'txt', 'mp3', 'ogg']
    
    # Create a ZIP archive
    temp = temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w')
    
    for book in collect_books(models.Book.tagged.with_all(shelf)):
        if 'pdf' in formats and book.pdf_file:
            filename = book.pdf_file.path
            archive.write(filename, str('%s.pdf' % book.slug))
        if 'odt' in formats and book.odt_file:
            filename = book.odt_file.path
            archive.write(filename, str('%s.odt' % book.slug))
        if 'txt' in formats and book.txt_file:
            filename = book.txt_file.path
            archive.write(filename, str('%s.txt' % book.slug))
        if 'mp3' in formats and book.mp3_file:
            filename = book.mp3_file.path
            archive.write(filename, str('%s.mp3' % book.slug))
        if 'ogg' in formats and book.ogg_file:
            filename = book.ogg_file.path
            archive.write(filename, str('%s.ogg' % book.slug))
    archive.close()
    
    response = HttpResponse(content_type='application/zip', mimetype='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % shelf.sort_key
    response['Content-Length'] = temp.tell()
    
    temp.seek(0)
    response.write(temp.read())
    return response


@cache.never_cache
def shelf_book_formats(request, shelf):
    """"
    Returns a list of formats of books in shelf.
    """
    shelf = get_object_or_404(models.Tag, slug=shelf, category='set')

    formats = {'pdf': False, 'odt': False, 'txt': False, 'mp3': False, 'ogg': False}
    
    for book in collect_books(models.Book.tagged.with_all(shelf)):
        if book.pdf_file:
            formats['pdf'] = True
        if book.odt_file:
            formats['odt'] = True
        if book.txt_file:
            formats['txt'] = True
        if book.mp3_file:
            formats['mp3'] = True
        if book.ogg_file:
            formats['ogg'] = True

    return HttpResponse(LazyEncoder().encode(formats))


@login_required
@require_POST
@cache.never_cache
def new_set(request):
    new_set_form = forms.NewSetForm(request.POST)
    if new_set_form.is_valid():
        new_set = new_set_form.save(request.user)

        if request.is_ajax():
            return HttpResponse(u'<p>Półka <strong>%s</strong> została utworzona</p>' % new_set)
        else:
            return HttpResponseRedirect('/')

    return HttpResponseRedirect('/')


@login_required
@require_POST
@cache.never_cache
def delete_shelf(request, slug):
    user_set = get_object_or_404(models.Tag, slug=slug, category='set', user=request.user)
    user_set.delete()

    if request.is_ajax():
        return HttpResponse(u'<p>Półka <strong>%s</strong> została usunięta</p>' % user_set.name)
    else:
        return HttpResponseRedirect('/')


# ==================
# = Authentication =
# ==================
@require_POST
@cache.never_cache
def login(request):
    form = AuthenticationForm(data=request.POST, prefix='login')
    if form.is_valid():
        auth.login(request, form.get_user())
        response_data = {'success': True, 'errors': {}}
    else:
        response_data = {'success': False, 'errors': form.errors}
    return HttpResponse(LazyEncoder(ensure_ascii=False).encode(response_data))


@require_POST
@cache.never_cache
def register(request):
    registration_form = UserCreationForm(request.POST, prefix='registration')
    if registration_form.is_valid():
        user = registration_form.save()
        user = auth.authenticate(
            username=registration_form.cleaned_data['username'], 
            password=registration_form.cleaned_data['password1']
        )
        auth.login(request, user)
        response_data = {'success': True, 'errors': {}}
    else:
        response_data = {'success': False, 'errors': registration_form.errors}
    return HttpResponse(LazyEncoder(ensure_ascii=False).encode(response_data))


@cache.never_cache
def logout_then_redirect(request):
    auth.logout(request)
    return HttpResponseRedirect(request.GET.get('next', '/'))



# =========
# = Admin =
# =========
@login_required
@staff_required
def import_book(request):
    """docstring for import_book"""
    book_import_form = forms.BookImportForm(request.POST, request.FILES)
    if book_import_form.is_valid():
        try:
            book_import_form.save()
        except:
            info = sys.exc_info()
            exception = pprint.pformat(info[1])
            tb = '\n'.join(traceback.format_tb(info[2]))
            return HttpResponse("An error occurred: %s\n\n%s" % (exception, tb), mimetype='text/plain')
        return HttpResponse("Book imported successfully")
    else:
        return HttpResponse("Error importing file: %r" % book_import_form.errors)



def clock(request):
    """ Provides server time for jquery.countdown,
    in a format suitable for Date.parse()
    """
    from datetime import datetime
    return HttpResponse(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
