# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import datetime
import feedparser
import re

from django import template
from django.template import Node, Variable
from django.utils.encoding import smart_str
from django.core.cache import get_cache
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.translation import ugettext as _

from catalogue import forms
from catalogue.utils import split_tags
from catalogue.models import Book, Fragment, Tag

register = template.Library()


class RegistrationForm(UserCreationForm):
    def as_ul(self):
        "Returns this form rendered as HTML <li>s -- excluding the <ul></ul>."
        return self._html_output(u'<li>%(errors)s%(label)s %(field)s<span class="help-text">%(help_text)s</span></li>', u'<li>%s</li>', '</li>', u' %s', False)


class LoginForm(AuthenticationForm):
    def as_ul(self):
        "Returns this form rendered as HTML <li>s -- excluding the <ul></ul>."
        return self._html_output(u'<li>%(errors)s%(label)s %(field)s<span class="help-text">%(help_text)s</span></li>', u'<li>%s</li>', '</li>', u' %s', False)


def iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def capfirst(text):
    try:
        return '%s%s' % (text[0].upper(), text[1:])
    except IndexError:
        return ''



def simple_title(tags):
    title = []
    for tag in tags:
        title.append("%s: %s" % (_(tag.category), tag.name))
    return capfirst(', '.join(title))


@register.simple_tag
def book_title(book, html_links=False):
    return book.pretty_title(html_links)


@register.simple_tag
def book_title_html(book):
    return book_title(book, html_links=True)


@register.simple_tag
def title_from_tags(tags):
    def split_tags(tags):
        result = {}
        for tag in tags:
            result[tag.category] = tag
        return result

    # TODO: Remove this after adding flection mechanism
    return simple_title(tags)

    class Flection(object):
        def get_case(self, name, flection):
            return name
    flection = Flection()

    self = split_tags(tags)

    title = u''

    # Specjalny przypadek oglądania wszystkich lektur na danej półce
    if len(self) == 1 and 'set' in self:
        return u'Półka %s' % self['set']

    # Specjalny przypadek "Twórczość w pozytywizmie", wtedy gdy tylko epoka
    # jest wybrana przez użytkownika
    if 'epoch' in self and len(self) == 1:
        text = u'Twórczość w %s' % flection.get_case(unicode(self['epoch']), u'miejscownik')
        return capfirst(text)

    # Specjalny przypadek "Dramat w twórczości Sofoklesa", wtedy gdy podane
    # są tylko rodzaj literacki i autor
    if 'kind' in self and 'author' in self and len(self) == 2:
        text = u'%s w twórczości %s' % (unicode(self['kind']),
            flection.get_case(unicode(self['author']), u'dopełniacz'))
        return capfirst(text)

    # Przypadki ogólniejsze
    if 'theme' in self:
        title += u'Motyw %s' % unicode(self['theme'])

    if 'genre' in self:
        if 'theme' in self:
            title += u' w %s' % flection.get_case(unicode(self['genre']), u'miejscownik')
        else:
            title += unicode(self['genre'])

    if 'kind' in self or 'author' in self or 'epoch' in self:
        if 'genre' in self or 'theme' in self:
            if 'kind' in self:
                title += u' w %s ' % flection.get_case(unicode(self['kind']), u'miejscownik')
            else:
                title += u' w twórczości '
        else:
            title += u'%s ' % unicode(self.get('kind', u'twórczość'))

    if 'author' in self:
        title += flection.get_case(unicode(self['author']), u'dopełniacz')
    elif 'epoch' in self:
        title += flection.get_case(unicode(self['epoch']), u'dopełniacz')

    return capfirst(title)


@register.simple_tag
def book_tree(book_list, books_by_parent):
    text = "".join("<li><a href='%s'>%s</a>%s</li>" % (
        book.get_absolute_url(), book.title, book_tree(books_by_parent.get(book, ()), books_by_parent)
        ) for book in book_list)

    if text:
        return "<ol>%s</ol>" % text
    else:
        return ''

@register.simple_tag
def book_tree_texml(book_list, books_by_parent, depth=1):
    return "".join("""
            <cmd name='hspace'><parm>%(depth)dem</parm></cmd>%(title)s
            <spec cat='align' /><cmd name="note"><parm>%(audiences)s</parm></cmd>
            <spec cat='align' /><cmd name="note"><parm>%(audiobook)s</parm></cmd>
            <ctrl ch='\\' />
            %(children)s
            """ % {
                "depth": depth,
                "title": book.title, 
                "audiences": ", ".join(book.audiences_pl()),
                "audiobook": "audiobook" if book.has_media('mp3') else "",
                "children": book_tree_texml(books_by_parent.get(book.id, ()), books_by_parent, depth + 1)
            } for book in book_list)


@register.simple_tag
def all_editors(extra_info):
    editors = []
    if 'editors' in extra_info:
        editors += extra_info['editors']
    if 'technical_editors' in extra_info:
        editors += extra_info['technical_editors']
    # support for extra_info-s from librarian<1.2
    if 'editor' in extra_info:
        editors.append(extra_info['editor'])
    if 'technical_editor' in extra_info:
        editors.append(extra_info['technical_editor'])
    return ', '.join(
                     ' '.join(p.strip() for p in person.rsplit(',', 1)[::-1])
                     for person in sorted(set(editors)))


@register.simple_tag
def user_creation_form():
    return RegistrationForm(prefix='registration').as_ul()


@register.simple_tag
def authentication_form():
    return LoginForm(prefix='login').as_ul()


@register.tag
def catalogue_url(parser, token):
    bits = token.split_contents()
    tag_name = bits[0]

    tags_to_add = []
    tags_to_remove = []
    for bit in bits[1:]:
        if bit[0] == '-':
            tags_to_remove.append(bit[1:])
        else:
            tags_to_add.append(bit)

    return CatalogueURLNode(tags_to_add, tags_to_remove)


class CatalogueURLNode(Node):
    def __init__(self, tags_to_add, tags_to_remove):
        self.tags_to_add = [Variable(tag) for tag in tags_to_add]
        self.tags_to_remove = [Variable(tag) for tag in tags_to_remove]

    def render(self, context):
        tags_to_add = []
        tags_to_remove = []

        for tag_variable in self.tags_to_add:
            tag = tag_variable.resolve(context)
            if isinstance(tag, (list, dict)):
                tags_to_add += [t for t in tag]
            else:
                tags_to_add.append(tag)

        for tag_variable in self.tags_to_remove:
            tag = tag_variable.resolve(context)
            if iterable(tag):
                tags_to_remove += [t for t in tag]
            else:
                tags_to_remove.append(tag)

        tag_slugs = [tag.url_chunk for tag in tags_to_add]
        for tag in tags_to_remove:
            try:
                tag_slugs.remove(tag.url_chunk)
            except KeyError:
                pass

        if len(tag_slugs) > 0:
            return reverse('tagged_object_list', kwargs={'tags': '/'.join(tag_slugs)})
        else:
            return reverse('main_page')


@register.inclusion_tag('catalogue/latest_blog_posts.html')
def latest_blog_posts(feed_url, posts_to_show=5):
    try:
        feed = feedparser.parse(str(feed_url))
        posts = []
        for i in range(posts_to_show):
            pub_date = feed['entries'][i].updated_parsed
            published = datetime.date(pub_date[0], pub_date[1], pub_date[2] )
            posts.append({
                'title': feed['entries'][i].title,
                'summary': feed['entries'][i].summary,
                'link': feed['entries'][i].link,
                'date': published,
                })
        return {'posts': posts}
    except:
        return {'posts': []}


@register.inclusion_tag('catalogue/tag_list.html')
def tag_list(tags, choices=None):
    if choices is None:
        choices = []
    if len(tags) == 1:
        one_tag = tags[0]
    return locals()

@register.inclusion_tag('catalogue/inline_tag_list.html')
def inline_tag_list(tags, choices=None):
    if choices is None:
        choices = []
    if len(tags) == 1:
        one_tag = tags[0]
    return locals()


@register.inclusion_tag('catalogue/book_info.html')
def book_info(book):
    return locals()


@register.inclusion_tag('catalogue/book_wide.html', takes_context=True)
def book_wide(context, book):
    theme_counter = book.theme_counter
    book_themes = Tag.objects.filter(pk__in=theme_counter.keys())
    for tag in book_themes:
        tag.count = theme_counter[tag.pk]
    extra_info = book.get_extra_info_value()
    hide_about = extra_info.get('about', '').startswith('http://wiki.wolnepodreczniki.pl')

    return {
        'book': book,
        'main_link': reverse('book_text', args=[book.slug]),
        'related': book.related_info(),
        'extra_info': book.get_extra_info_value(),
        'hide_about': hide_about,
        'themes': book_themes,
        'custom_pdf_form': forms.CustomPDFForm(),
        'request': context.get('request'),
    }


@register.inclusion_tag('catalogue/book_short.html', takes_context=True)
def book_short(context, book):
    return {
        'book': book,
        'main_link': book.get_absolute_url(),
        'related': book.related_info(),
        'request': context.get('request'),
    }


@register.inclusion_tag('catalogue/book_mini_box.html')
def book_mini(book):
    return {
        'book': book,
        'related': book.related_info(),
    }


@register.inclusion_tag('catalogue/work-list.html', takes_context=True)
def work_list(context, object_list):
    request = context.get('request')
    if object_list:
        object_type = type(object_list[0]).__name__
    return locals()


@register.inclusion_tag('catalogue/fragment_promo.html')
def fragment_promo(arg=None):
    if arg is None:
        fragments = Fragment.objects.all().order_by('?')
        fragment = fragments[0] if fragments.exists() else None
    elif isinstance(arg, Book):
        fragment = arg.choose_fragment()
    else:
        fragments = Fragment.tagged.with_all(arg).order_by('?')
        fragment = fragments[0] if fragments.exists() else None

    return {
        'fragment': fragment,
    }


@register.inclusion_tag('catalogue/related_books.html')
def related_books(book, limit=6):
    related = list(Book.objects.filter(
        common_slug=book.common_slug).exclude(pk=book.pk)[:limit])
    limit -= len(related)
    if limit:
        related += Book.tagged.related_to(book,
                Book.objects.exclude(common_slug=book.common_slug),
                ignore_by_tag=book.book_tag())[:limit]
    return {
        'books': related,
    }


@register.inclusion_tag('catalogue/menu.html')
def catalogue_menu():
    tags = Tag.objects.filter(
            category__in=('author', 'epoch', 'genre', 'kind', 'theme')
        ).exclude(book_count=0)
    return split_tags(tags)
    


@register.simple_tag
def tag_url(category, slug):
    return reverse('catalogue.views.tagged_object_list', args=[
        '/'.join((Tag.categories_dict[category], slug))
    ])
