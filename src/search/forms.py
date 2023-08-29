# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.apps import apps
from django.conf import settings
from django.contrib.postgres.search import SearchHeadline, SearchQuery
from django import forms
from django.utils.translation import gettext_lazy as _
from catalogue.constants import LANGUAGES_3TO2
import catalogue.models
import pdcounter.models
import picture.models
from .fields import InlineRadioWidget
from .utils import UnaccentSearchQuery, UnaccentSearchVector


class SearchFilters(forms.Form):
    q = forms.CharField(
        required=False, widget=forms.HiddenInput(),
        min_length=2, max_length=256,
    )
    format = forms.ChoiceField(required=False, choices=[
        ('', _('wszystkie')),
        ('text', _('tekst')),
        ('audio', _('audiobook')),
        ('daisy', _('Daisy')),
        ('art', _('obraz')),
    ], widget=InlineRadioWidget())
    lang = forms.ChoiceField(required=False)
    epoch = forms.ChoiceField(required=False)
    genre = forms.ChoiceField(required=False)
    category = forms.ChoiceField(required=False, choices=[
        ('', _('wszystkie')),
        ('author', _('autor')),
        #('translator', _('tłumacz')),
        ('theme', _('motyw')),
        ('genre', _('gatunek')),
        ('book', _('tytuł')),
        ('art', _('obraz')),
        ('collection', _('kolekcja')),
        ('quote', _('cytat')),
    ], widget=InlineRadioWidget())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        langs = dict(settings.LANGUAGES)
        self.fields['lang'].choices = [('', _('wszystkie'))] + [
            (
                b,
                langs.get(LANGUAGES_3TO2.get(b, b), b)
            )
            for b in catalogue.models.Book.objects.values_list(
                    'language', flat=True
            ).distinct().order_by()
        ]
        self.fields['epoch'].choices = [('', _('wszystkie'))] + [
            (b.slug, b.name)
            for b in catalogue.models.Tag.objects.filter(category='epoch')
        ]
        self.fields['genre'].choices = [('', _('wszystkie'))] + [
            (b.slug, b.name)
            for b in catalogue.models.Tag.objects.filter(category='genre')
        ]

    def get_querysets(self):
        qs = {
            'author': catalogue.models.Tag.objects.filter(category='author'),
            'pdauthor': pdcounter.models.Author.objects.all(),
            'theme': catalogue.models.Tag.objects.filter(category='theme'),
            'genre': catalogue.models.Tag.objects.filter(category='genre'),
            'collection': catalogue.models.Collection.objects.all(),
            'book': catalogue.models.Book.objects.filter(findable=True),
            'pdbook': pdcounter.models.BookStub.objects.all(),
            'snippet': catalogue.models.Snippet.objects.filter(book__findable=True),
            'art': picture.models.Picture.objects.all(),
            # art pieces
        }
        if self.cleaned_data['category']:
            c = self.cleaned_data['category']
            if c != 'author':
                qs['author'] = qs['author'].none()
                qs['pdauthor'] = qs['pdauthor'].none()
            if c != 'theme': qs['theme'] = qs['theme'].none()
            if c != 'genre': qs['genre'] = qs['genre'].none()
            if c != 'collection': qs['collection'] = qs['collection'].none()
            if c != 'book':
                qs['book'] = qs['book'].none()
                qs['pdbook'] = qs['pdbook'].none()
            if c != 'quote': qs['snippet'] = qs['snippet'].none()
            if c != 'art': qs['art'] = qs['art'].none()
            qs['art'] = picture.models.Picture.objects.none()

        if self.cleaned_data['format']:
            c = self.cleaned_data['format']
            qs['author'] = qs['author'].none()
            qs['pdauthor'] = qs['pdauthor'].none()
            qs['theme'] = qs['theme'].none()
            qs['genre'] = qs['genre'].none()
            qs['collection'] = qs['collection'].none()
            if c == 'art':
                qs['book'] = qs['book'].none()
                qs['pdbook'] = qs['pdbook'].none()
                qs['snippet'] = qs['snippet'].none()
            if c in ('text', 'audio', 'daisy'):
                qs['art'] = qs['art'].none()
                if c == 'audio':
                    qs['book'] = qs['book'].filter(media__type='mp3')
                    qs['pdbook'] = qs['book'].none()
                    qs['snippet'] = qs['snippet'].filter(book__media__type='mp3')
                elif c == 'daisy':
                    qs['book'] = qs['book'].filter(media__type='daisy')
                    qs['snippet'] = qs['snippet'].filter(book__media__type='daisy')

        if self.cleaned_data['lang']:
            qs['author'] = qs['author'].none()
            qs['pdauthor'] = qs['pdauthor'].none()
            qs['theme'] = qs['theme'].none()
            qs['genre'] = qs['genre'].none()
            qs['art'] = qs['art'].none()
            qs['collection'] = qs['collection'].none()
            qs['book'] = qs['book'].filter(language=self.cleaned_data['lang'])
            qs['pdbook'] = qs['pdbook'].none()
            qs['snippet'] = qs['snippet'].filter(book__language=self.cleaned_data['lang'])

        for tag_cat in ('epoch', 'genre'):
            c = self.cleaned_data[tag_cat]
            if c:
                # FIXME nonexistent
                t = catalogue.models.Tag.objects.get(category=tag_cat, slug=c)
                qs['author'] = qs['author'].none()
                qs['pdauthor'] = qs['pdauthor'].none()
                qs['theme'] = qs['theme'].none()
                qs['genre'] = qs['genre'].none()
                qs['collection'] = qs['collection'].none()
                qs['book'] = qs['book'].filter(tag_relations__tag=t)
                qs['pdbook'] = qs['pdbook'].none()
                qs['snippet'] = qs['snippet'].filter(book__tag_relations__tag=t)
                qs['art'] = qs['art'].filter(tag_relations__tag=t)
            
        return qs

    def results(self):
        qs = self.get_querysets()
        query = self.cleaned_data['q']
        squery = UnaccentSearchQuery(query, config=settings.SEARCH_CONFIG)
        query = SearchQuery(query, config=settings.SEARCH_CONFIG)
        books = qs['book'].annotate(
            search_vector=UnaccentSearchVector('title')
        ).filter(search_vector=squery)
        books = books.exclude(ancestor__in=books).order_by('-popularity__count')

        snippets = qs['snippet'].filter(search_vector=squery).annotate(
                    headline=SearchHeadline(
                        'text',
                        query,
                        config=settings.SEARCH_CONFIG,
                        start_sel='<strong>',
                        stop_sel='</strong>',
                    )
                ).order_by('-book__popularity__count', 'sec')[:100]
        snippets_by_book = {}
        for snippet in snippets:
            snippet_list = snippets_by_book.setdefault(snippet.book, [])
            if len(snippet_list) < 3:
                snippet_list.append(snippet)

        return {
            'author': qs['author'].annotate(
                search_vector=UnaccentSearchVector('name_pl')
            ).filter(search_vector=squery),
            'theme': qs['theme'].annotate(
                search_vector=UnaccentSearchVector('name_pl')
            ).filter(search_vector=squery),
            'genre': qs['genre'].annotate(
                search_vector=UnaccentSearchVector('name_pl')
            ).filter(search_vector=squery),
            'collection': qs['collection'].annotate(
                search_vector=UnaccentSearchVector('title')
            ).filter(search_vector=squery),
            'book': books[:100],
            'art': qs['art'].annotate(
                search_vector=UnaccentSearchVector('title')
            ).filter(search_vector=squery)[:100],
            'snippet': snippets_by_book,
            'pdauthor': pdcounter.models.Author.search(squery, qs=qs['pdauthor']),
            'pdbook': pdcounter.models.BookStub.search(squery, qs=qs['pdbook']),
        }

