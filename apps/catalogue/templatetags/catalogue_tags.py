# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import feedparser
import datetime

from django import template
from django.template import Node, Variable
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q
from django.conf import settings
from django.utils.translation import ugettext as _

from catalogue.forms import SearchForm


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


@register.inclusion_tag('catalogue/search_form.html')
def search_form():
    return {"form": SearchForm()}

@register.inclusion_tag('catalogue/breadcrumbs.html')
def breadcrumbs(tags, search_form=True):
    context = {'tag_list': tags}
    try:
        max_tag_list = settings.MAX_TAG_LIST
    except AttributeError:
        max_tag_list = -1
    if search_form and (max_tag_list == -1 or len(tags) < max_tag_list):
        context['search_form'] = SearchForm(tags=tags)
    return context


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


@register.inclusion_tag('catalogue/folded_tag_list.html')
def folded_tag_list(tags, title='', choices=None):
    tags = [tag for tag in tags if tag.count]
    if choices is None:
        choices = []
    some_tags_hidden = False
    tag_count = len(tags)

    if tag_count == 1:
        one_tag = tags[0]
    else:
        shown_tags = [tag for tag in tags if tag.main_page]
        if tag_count > len(shown_tags):
            some_tags_hidden = True
    return locals()


@register.inclusion_tag('catalogue/book_info.html')
def book_info(book):
    return locals()
