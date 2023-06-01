# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.apps import apps
from django.contrib.postgres.search import SearchHeadline, SearchRank, SearchQuery
from django import forms
from django.utils.translation import gettext_lazy as _

from .fields import JQueryAutoCompleteSearchField, InlineRadioWidget
from .utils import build_search_query


class SearchForm(forms.Form):
    q = JQueryAutoCompleteSearchField(label=_('Search'))
    # {'minChars': 2, 'selectFirst': True, 'cacheLength': 50, 'matchContains': "word"})

    def __init__(self, source, *args, **kwargs):
        kwargs['auto_id'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['q'].widget.attrs['id'] = 'search'
        self.fields['q'].widget.attrs['autocomplete'] = 'off'
        self.fields['q'].widget.attrs['data-source'] = source
        if 'q' not in self.data:
            self.fields['q'].widget.attrs['placeholder'] = _('title, author, epoch, kind, genre, phrase')


class SearchFilters(forms.Form):
    q = forms.CharField(required=False, widget=forms.HiddenInput())
    format = forms.ChoiceField(required=False, choices=[
        ('', 'wszystkie'),
        ('text', 'tekst'),
        ('audio', 'audiobook'),
        ('daisy', 'Daisy'),
        ('art', 'obraz'),
        #('theme', 'motywy'),
    ], widget=InlineRadioWidget())
    lang = forms.ChoiceField(required=False)
    epoch = forms.ChoiceField(required=False)
    genre = forms.ChoiceField(required=False)
    category = forms.ChoiceField(required=False, choices=[
        ('', 'wszystkie'),
        ('author', 'autor'),
        #('translator', 'tłumacz'),
        ('theme', 'motyw'),
        ('genre', 'gatunek'),
        ('book', 'tytuł'),
        ('art', 'obraz'),
        ('collection', 'kolekcja'),
        ('quote', 'cytat'),
    ], widget=InlineRadioWidget())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from catalogue.models import Book, Tag

        self.fields['lang'].choices = [('', 'wszystkie')] + [
            (b, b)
            for b in Book.objects.values_list(
                    'language', flat=True
            ).distinct().order_by()
        ]
        self.fields['epoch'].choices = [('', 'wszystkie')] + [
            (b.slug, b.name)
            for b in Tag.objects.filter(category='epoch')
        ]
        self.fields['genre'].choices = [('', 'wszystkie')] + [
            (b.slug, b.name)
            for b in Tag.objects.filter(category='genre')
        ]

    def get_querysets(self):
        Tag = apps.get_model('catalogue', 'Tag')
        Book = apps.get_model('catalogue', 'Book')
        Picture = apps.get_model('picture', 'Picture')
        Snippet = apps.get_model('catalogue', 'Snippet')
        Collection = apps.get_model('catalogue', 'Collection')
        qs = {
            'author': Tag.objects.filter(category='author'),
            'theme': Tag.objects.filter(category='theme'),
            'genre': Tag.objects.filter(category='genre'),
            'collection': Collection.objects.all(),
            'book': Book.objects.all(), #findable
            'snippet': Snippet.objects.all(),
            'art': Picture.objects.all(),
            # art pieces
            # pdbooks
            # pdauthors
        }
        if self.cleaned_data['category']:
            c = self.cleaned_data['category']
            if c != 'author': qs['author'] = Tag.objects.none()
            if c != 'theme': qs['theme'] = Tag.objects.none()
            if c != 'genre': qs['genre'] = Tag.objects.none()
            if c != 'collection': qs['collection'] = Collection.objects.none()
            if c != 'book': qs['book'] = Book.objects.none()
            if c != 'quote': qs['snippet'] = Snippet.objects.none()
            if c != 'art': qs['art'] = Picture.objects.none()
            qs['art'] = Picture.objects.none()

        if self.cleaned_data['format']:
            c = self.cleaned_data['format']
            qs['author'] = Tag.objects.none()
            qs['theme'] = Tag.objects.none()
            qs['genre'] = Tag.objects.none()
            qs['collection'] = Collection.objects.none()
            if c == 'art':
                qs['book'] = Book.objects.none()
                qs['snippet'] = Snippet.objects.none()
            if c in ('text', 'audio', 'daisy'):
                qs['art'] = Picture.objects.none()
                if c == 'audio':
                    qs['book'] = qs['book'].filter(media__type='mp3')
                    qs['snippet'] = qs['snippet'].filter(book__media__type='mp3')
                elif c == 'daisy':
                    qs['book'] = qs['book'].filter(media__type='daisy')
                    qs['snippet'] = qs['snippet'].filter(book__media__type='daisy')

        if self.cleaned_data['lang']:
            qs['author'] = Tag.objects.none()
            qs['theme'] = Tag.objects.none()
            qs['genre'] = Tag.objects.none()
            qs['art'] = Picture.objects.none()
            qs['collection'] = Collection.objects.none()
            qs['book'] = qs['book'].filter(language=self.cleaned_data['lang'])
            qs['snippet'] = qs['snippet'].filter(book__language=self.cleaned_data['lang'])

        for tag_cat in ('epoch', 'genre'):
            c = self.cleaned_data[tag_cat]
            if c:
                # FIXME nonexistent
                t = Tag.objects.get(category=tag_cat, slug=c)
                qs['author'] = Tag.objects.none()
                qs['theme'] = Tag.objects.none()
                qs['genre'] = Tag.objects.none()
                qs['collection'] = Collection.objects.none()
                qs['book'] = qs['book'].filter(tag_relations__tag=t)
                qs['snippet'] = qs['snippet'].filter(book__tag_relations__tag=t)
                qs['art'] = qs['art'].filter(tag_relations__tag=t)
            
        return qs

    def results(self):
        qs = self.get_querysets()
        query = self.cleaned_data['q']
        squery = build_search_query(query, config='polish')
        query = SearchQuery(query, config='polish')
        books = qs['book'].filter(title__search=query)
        books = books.exclude(ancestor__in=books)
        return {
            'author': qs['author'].filter(slug__search=query),
            'theme': qs['theme'].filter(slug__search=query),
            'genre': qs['genre'].filter(slug__search=query),
            'collection': qs['collection'].filter(title__search=query),
            'book': books[:100],
            'snippet': qs['snippet'].annotate(
                    rank=SearchRank('search_vector', squery)
                ).filter(rank__gt=0).order_by('-rank').annotate(
                    headline=SearchHeadline(
                        'text',
                        query,
                        config='polish',
                        start_sel='<strong>',
                        stop_sel='</strong>',
                        highlight_all=True
                    )
                )[:100],
            'art': qs['art'].filter(title__search=query)[:100],
        }

