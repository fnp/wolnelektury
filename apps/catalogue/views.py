# -*- coding: utf-8 -*-
import tempfile
import zipfile

from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import SortedDict
from django.views.decorators.http import require_POST
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import simplejson
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from django.views.decorators import cache
from django.core.servers.basehttp import FileWrapper

from catalogue import models
from catalogue import forms
from catalogue.utils import split_tags
from newtagging import views as newtagging_views


class LazyEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj


@cache.cache_control(must_revalidate=True, max_age=3600)
def main_page(request):    
    if request.user.is_authenticated():
        shelves = models.Tag.objects.filter(category='set', user=request.user)
        new_set_form = forms.NewSetForm()
    extra_where = 'NOT catalogue_tag.category = "set"'
    tags = models.Tag.objects.usage_for_model(models.Book, counts=True, extra={'where': [extra_where]})
    fragment_tags = models.Tag.objects.usage_for_model(models.Fragment, counts=True,
        extra={'where': ['catalogue_tag.category = "theme"'] + [extra_where]})
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


@cache.cache_control(must_revalidate=True, max_age=3600)
def tagged_object_list(request, tags=''):
    # Prevent DoS attacks on our database
    if len(tags.split('/')) > 6:
        raise Http404
        
    try:
        tags = models.Tag.get_tag_list(tags)
    except models.Tag.DoesNotExist:
        raise Http404
    
    model = models.Book
    shelf_is_set = (len(tags) == 1 and tags[0].category == 'set')
    theme_is_set = len([tag for tag in tags if tag.category == 'theme']) > 0
    if theme_is_set:
        model = models.Fragment

    extra_where = 'NOT catalogue_tag.category = "set"'
    related_tags = models.Tag.objects.related_for_model(tags, model, counts=True, extra={'where': [extra_where]})
    categories = split_tags(related_tags)

    if not theme_is_set:
        model=models.Book.objects.filter(parent=None)
    
    return newtagging_views.tagged_object_list(
        request,
        tag_model=models.Tag,
        queryset_or_model=model,
        tags=tags,
        template_name='catalogue/tagged_object_list.html',
        extra_context = {'categories': categories, 'shelf_is_set': shelf_is_set },
    )


def book_detail(request, slug):
    book = get_object_or_404(models.Book, slug=slug)
    tags = list(book.tags.filter(~Q(category='set')))
    categories = split_tags(tags)
    book_children = book.children.all().order_by('parent_number')
    
    form = forms.SearchForm()
    return render_to_response('catalogue/book_detail.html', locals(),
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
def search(request):
    query = request.GET.get('q', '')
    tags = request.GET.get('tags', '')
    if tags == '':
        tags = []

    try:
        tag_list = models.Tag.get_tag_list(tags)
        tag = models.Tag.objects.get(name=query)
    except models.Tag.DoesNotExist:
        try:
            book = models.Book.objects.get(title=query)
            return HttpResponseRedirect(book.get_absolute_url())
        except models.Book.DoesNotExist:
            return HttpResponseRedirect(reverse('catalogue.views.main_page'))
    else:
        tag_list.append(tag)
        return HttpResponseRedirect(reverse('catalogue.views.tagged_object_list', 
            kwargs={'tags': '/'.join(tag.slug for tag in tag_list)}
        ))


def tags_starting_with(request):
    try:
        prefix = request.GET['q']
        if len(prefix) < 2:
            raise KeyError

        books = models.Book.objects.filter(title__icontains=prefix)
        tags = models.Tag.objects.filter(name__icontains=prefix)
        if request.user.is_authenticated():
            tags = tags.filter(~Q(category='set') | Q(user=request.user))
        else:
            tags = tags.filter(~Q(category='set'))

        completions = [book.title for book in books] + [tag.name for tag in tags]

        return HttpResponse('\n'.join(completions))    

    except KeyError:
        return HttpResponse('')


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
            book.tags = ([models.Tag.objects.get(pk=id) for id in form.cleaned_data['set_ids']] +
                list(book.tags.filter(~Q(category='set') | ~Q(user=request.user))))
            if request.is_ajax():
                return HttpResponse('<p>Półki zostały zapisane.</p>')
            else:
                return HttpResponseRedirect('/')
    else:
        form = forms.ObjectSetsForm(book, request.user)
        new_set_form = forms.NewSetForm()
    
    return render_to_response('catalogue/book_sets.html', locals(),
        context_instance=RequestContext(request))


@cache.cache_control(must_revalidate=True, max_age=1800)
def download_shelf(request, slug):
    """"
    Create a ZIP archive on disk and transmit it in chunks of 8KB,
    without loading the whole file into memory. A similar approach can
    be used for large dynamic PDF files.                                        
    """
    shelf = get_object_or_404(models.Tag, slug=slug, category='set')
    
    # Create a ZIP archive
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
    for book in models.Book.tagged.with_all(shelf):
        if book.pdf_file:
            filename = book.pdf_file.path
            archive.write(filename, str('%s.pdf' % book.slug))
        if book.odt_file:
            filename = book.odt_file.path
            archive.write(filename, str('%s.odt' % book.slug))
        if book.txt_file:
            filename = book.txt_file.path
            archive.write(filename, str('%s.txt' % book.slug))
    archive.close()
    
    # Write file to archive in small chunks
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % shelf.sort_key
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response


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

    return render_to_response('catalogue/book_sets.html', locals(),
            context_instance=RequestContext(request))


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

