# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import SortedDict
from django.views.decorators.http import require_POST

from catalogue import models
from catalogue import forms
from catalogue.utils import split_tags


def catalogue_redirect(request, tags=''):
    if len(request.GET['q']) > 0:
        try:
            tag = models.Tag.objects.get(name=request.GET['q'])
            if len(tags):
                tags += '/'
            tags = tags + tag.slug
        except models.Tag.DoesNotExist:
            book = get_object_or_404(models.Book, title=request.GET['q'])
            return HttpResponseRedirect(book.get_absolute_url())
    if len(tags) > 0:
        return HttpResponseRedirect(reverse('catalogue.views.tagged_book_list', kwargs=dict(tags=tags)))
    else:
        return HttpResponseRedirect(reverse('catalogue.views.main_page'))


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


def main_page(request):
    if 'q' in request.GET:
        return catalogue_redirect(request)
    
    if request.user.is_authenticated():
        extra_where = '(NOT catalogue_tag.category = "set" OR catalogue_tag.user_id = %d)' % request.user.id
    else:
        extra_where = 'NOT catalogue_tag.category = "set"'
    tags = models.Tag.objects.usage_for_model(models.Book, counts=True, extra={'where': [extra_where]})
    categories = split_tags(tags)
    
    form = forms.SearchForm()
    return render_to_response('catalogue/main_page.html', locals(),
        context_instance=RequestContext(request))


def book_list(request):
    if 'q' in request.GET:
        return catalogue_redirect(request)
        
    books = models.Book.objects.all()
    form = forms.SearchForm()
    
    books_by_first_letter = SortedDict()
    for book in books:
        books_by_first_letter.setdefault(book.title[0], []).append(book)
    
    return render_to_response('catalogue/book_list.html', locals(),
        context_instance=RequestContext(request))


def tagged_book_list(request, tags=''):
    if 'q' in request.GET:
        return catalogue_redirect(request, tags)
    
    choices_split = tags.split('/')
    tags = []
    for tag in choices_split:
        tag = get_object_or_404(models.Tag, slug=tag)
        if tag.category == 'set' and (not request.user.is_authenticated() or request.user != tag.user):
            raise Http404
        tags.append(tag)
        
    books = models.Book.objects.with_all(tags)
    
    if request.user.is_authenticated():
        extra_where = '(NOT catalogue_tag.category = "set" OR catalogue_tag.user_id = %d)' % request.user.id
    else:
        extra_where = 'NOT catalogue_tag.category = "set"'
    related_tags = models.Tag.objects.related_for_model(tags, models.Book, counts=True, extra={'where': [extra_where]})
    categories = split_tags(related_tags)
    
    form = forms.SearchForm()
    
    return render_to_response('catalogue/tagged_book_list.html', dict(
        tags=tags,
        form=form,
        books=books,
        categories=categories,
    ), context_instance=RequestContext(request))


def book_detail(request, slug):
    book = get_object_or_404(models.Book, slug=slug)
    tags = list(book.tags.filter(~Q(category='set')))
    categories = split_tags(tags)
    search_form = forms.SearchForm()
    
    return render_to_response('catalogue/book_detail.html', locals(),
        context_instance=RequestContext(request))


@login_required
def book_sets(request, slug):
    book = get_object_or_404(models.Book, slug=slug)
    user_sets = models.Tag.objects.filter(category='set', user=request.user)
    book_sets = book.tags.filter(category='set', user=request.user)
    
    if request.method == 'POST':
        form = forms.BookSetsForm(book, request.user, request.POST)
        if form.is_valid():
            book.tags = ([models.Tag.objects.get(pk=id) for id in form.cleaned_data['set_ids']] +
                list(book.tags.filter(~Q(category='set') | ~Q(user=request.user))))
            if request.is_ajax():
                return HttpResponse('<p>Zestawy zostały zapisane</p>')
            else:
                return HttpResponseRedirect('/')
    else:
        form = forms.BookSetsForm(book, request.user)
        new_set_form = forms.NewSetForm()
    
    return render_to_response('catalogue/book_sets.html', locals(),
        context_instance=RequestContext(request))

@login_required
@require_POST
def new_set(request):
    new_set_form = forms.NewSetForm(request.POST)
    if new_set_form.is_valid():
        new_set = new_set_form.save(request.user)
        return HttpResponse('<p>Zestaw <strong>%s</strong> został utworzony</p>' % new_set)
    
    return render_to_response('catalogue/book_sets.html', locals(),
            context_instance=RequestContext(request))

