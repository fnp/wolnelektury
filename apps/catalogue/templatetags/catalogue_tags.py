# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import datetime
import feedparser
from random import randint

from django.conf import settings
from django import template
from django.template import Node, Variable, Template, Context
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import ugettext as _

from catalogue.utils import split_tags, related_tag_name as _related_tag_name
from catalogue.models import Book, BookMedia, Fragment, Tag
from catalogue.constants import LICENSES, LANGUAGES_3TO2

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


@register.simple_tag
def html_title_from_tags(tags):
    if len(tags) < 2:
        return title_from_tags(tags)
    template = Template("{{ category }}: <a href='{{ tag.get_absolute_url }}'>{{ tag.name }}</a>")
    return capfirst(",<br/>".join(
        template.render(Context({'tag': tag, 'category': _(tag.category)})) for tag in tags))
    

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
def audiobook_tree(book_list, books_by_parent):
    text = "".join("<li><a class='open-player' href='%s'>%s</a>%s</li>" % (
        reverse("book_player", args=[book.slug]), book.title, audiobook_tree(books_by_parent.get(book, ()), books_by_parent)
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
def book_tree_csv(author, book_list, books_by_parent, depth=1, max_depth=3, delimeter="\t"):
    def quote_if_necessary(s):
        try:
            s.index(delimeter)
            s.replace('"', '\\"')
            return '"%s"' % s
        except ValueError:
            return s
        
    return "".join("""%(author)s%(d)s%(preindent)s%(title)s%(d)s%(postindent)s%(audiences)s%(d)s%(audiobook)s
%(children)s""" % {
                "d": delimeter,
                "preindent": delimeter * (depth - 1),
                "postindent": delimeter * (max_depth - depth), 
                "depth": depth,
                "author": quote_if_necessary(author.name),
                "title": quote_if_necessary(book.title),
                "audiences": ", ".join(book.audiences_pl()),
                "audiobook": "audiobook" if book.has_media('mp3') else "",
                "children": book_tree_csv(author, books_by_parent.get(book.id, ()), books_by_parent, depth + 1)
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
    if len(tags) == 1 and tags[0].category not in [t.category for t in choices]:
        one_tag = tags[0]
    return locals()


@register.inclusion_tag('catalogue/inline_tag_list.html')
def inline_tag_list(tags, choices=None):
    return tag_list(tags, choices)


@register.inclusion_tag('catalogue/collection_list.html')
def collection_list(collections):
    return locals()


@register.inclusion_tag('catalogue/book_info.html')
def book_info(book):
    return locals()


@register.inclusion_tag('catalogue/book_wide.html', takes_context=True)
def book_wide(context, book):
    book_themes = book.related_themes()
    extra_info = book.extra_info
    hide_about = extra_info.get('about', '').startswith('http://wiki.wolnepodreczniki.pl')

    return {
        'book': book,
        'main_link': reverse('book_text', args=[book.slug]) if book.html_file else None,
        'related': book.related_info(),
        'extra_info': extra_info,
        'hide_about': hide_about,
        'themes': book_themes,
        'request': context.get('request'),
        'show_lang': book.language_code() != settings.LANGUAGE_CODE,
    }


@register.inclusion_tag('catalogue/book_short.html', takes_context=True)
def book_short(context, book):
    return {
        'book': book,
        'main_link': book.get_absolute_url(),
        'related': book.related_info(),
        'request': context.get('request'),
        'show_lang': book.language_code() != settings.LANGUAGE_CODE,
    }


@register.inclusion_tag('catalogue/book_mini_box.html')
def book_mini(book, with_link=True):
    author_str = ", ".join(related_tag_name(tag)
        for tag in book.related_info()['tags'].get('author', ()))
    return {
        'book': book,
        'author_str': author_str,
        'with_link': with_link,
        'show_lang': book.language_code() != settings.LANGUAGE_CODE,
    }


@register.inclusion_tag('catalogue/work-list.html', takes_context=True)
def work_list(context, object_list):
    request = context.get('request')
    for obj in object_list:
        obj.object_type = type(obj).__name__
        
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
def related_books(book, limit=6, random=1, taken=0):
    limit = limit - taken
    cache_key = "catalogue.related_books.%d.%d" % (book.id, limit - random)
    related = cache.get(cache_key)
    if related is None:
        related = Book.tagged.related_to(book,
                Book.objects.exclude(common_slug=book.common_slug),
                ignore_by_tag=book.book_tag())[:limit-random]
        cache.set(cache_key, related, 1800)
    if random:
        random_books = Book.objects.exclude(
                        pk__in=[b.pk for b in related] + [book.pk])
        if random == 1:
            count = random_books.count()
            if count:
                related.append(random_books[randint(0, count - 1)])
        else:
            related += list(random_books.order_by('?')[:random])
    return {
        'books': related,
    }


@register.inclusion_tag('catalogue/menu.html')
def catalogue_menu():
    return {'categories': [
                ('author', _('Authors'), 'autorzy'),
                ('genre', _('Genres'), 'gatunki'),
                ('kind', _('Kinds'), 'rodzaje'),
                ('epoch', _('Epochs'), 'epoki'),
                ('theme', _('Themes'), 'motywy'),
        ]}


@register.simple_tag
def tag_url(category, slug):
    return Tag.create_url(category, slug)


@register.simple_tag
def download_audio(book, daisy=True):
    related = book.related_info()
    links = []
    if related['media'].get('mp3'):
        links.append("<a href='%s'>%s</a>" %
            (reverse('download_zip_mp3', args=[book.slug]),
                BookMedia.formats['mp3'].name))
    if related['media'].get('ogg'):
        links.append("<a href='%s'>%s</a>" %
            (reverse('download_zip_ogg', args=[book.slug]),
                BookMedia.formats['ogg'].name))
    if daisy and related['media'].get('daisy'):
        for dsy in book.get_media('daisy'):
            links.append("<a href='%s'>%s</a>" %
                (dsy.file.url, BookMedia.formats['daisy'].name))
    return ", ".join(links)


@register.inclusion_tag("catalogue/snippets/custom_pdf_link_li.html")
def custom_pdf_link_li(book):
    return {
        'book': book,
        'NO_CUSTOM_PDF': settings.NO_CUSTOM_PDF,
    }


@register.inclusion_tag("catalogue/snippets/license_icon.html")
def license_icon(license_url):
    """Creates a license icon, if the license_url is known."""
    known = LICENSES.get(license_url)
    if known is None:
        return {}
    return {
        "license_url": license_url,
        "icon": "img/licenses/%s.png" % known['icon'],
        "license_description": known['description'],
    }


@register.simple_tag
def related_tag_name(tag, lang=None):
    return _related_tag_name(tag, lang)


@register.simple_tag
def class_name(obj):
    return obj.__class__.__name__

