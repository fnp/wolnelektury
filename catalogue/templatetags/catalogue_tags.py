# -*- coding: utf-8 -*-
from django import template
from django.template import Node, Variable
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q


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
def title_from_tags(tags):
    def split_tags(tags):
        result = {}
        for tag in tags:
            result[tag.category] = tag
        return result
    
    class Flection(object):
        def get_case(self, name, flection):
            return name
    flection = Flection()
    
    self = split_tags(tags)
    
    title = u''
    
    # Specjalny przypadek oglądania wszystkich lektur w danym zestawie
    if len(self) == 1 and 'set' in self:
        return u'Zestaw %s' % self['set']
    
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
def user_creation_form():
    return RegistrationForm(prefix='registration').as_ul()


@register.simple_tag
def authentication_form():
    return LoginForm(prefix='login').as_ul()


@register.inclusion_tag('catalogue/breadcrumbs.html')
def breadcrumbs(tags, search_form=True):
    from wolnelektury.catalogue.forms import SearchForm
    context = {'tag_list': tags}
    if search_form:
        context['search_form'] = SearchForm(tags=tags)
    return context


@register.inclusion_tag('catalogue/_book.html')
def book(book):
    tags = book.tags.filter(~Q(category__in=('set', 'theme')))
    tags = [u'<a href="%s">%s</a>' % (tag.get_absolute_url(), tag.name) for tag in tags]
    
    formats = []
    if book.html_file:
        formats.append(u'<a href="%s">Czytaj online</a>' % book.html_file.url)
    if book.pdf_file:
        formats.append(u'<a href="%s">Plik PDF</a>' % book.pdf_file.url)
    if book.odt_file:
        formats.append(u'<a href="%s">Plik ODT</a>' % book.odt_file.url)
        
    return {'book': book, 'tags': tags, 'formats': formats}


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
            
        tag_slugs = [tag.slug for tag in tags_to_add]
        for tag in tags_to_remove:
            try:
                tag_slugs.remove(tag.slug)
            except KeyError:
                pass
        
        if len(tag_slugs) > 0:
            return reverse('tagged_book_list', kwargs={'tags': '/'.join(tag_slugs)})
        else:
            return reverse('main_page')


@register.inclusion_tag('catalogue/latest_blog_posts.html')
def latest_blog_posts(feed_url, posts_to_show=5):
    import feedparser
    import datetime
    
    feed = feedparser.parse(feed_url)
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

