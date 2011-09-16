# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import feedparser
import datetime

from django import template

from catalogue.models import Book, BookMedia


register = template.Library()

#~ 
#~ @register.tag(name='captureas')
#~ def do_captureas(parser, token):
    #~ try:
        #~ tag_name, args = token.contents.split(None, 1)
    #~ except ValueError:
        #~ raise template.TemplateSyntaxError("'captureas' node requires a variable name.")
    #~ nodelist = parser.parse(('endcaptureas',))
    #~ parser.delete_first_token()
    #~ return CaptureasNode(nodelist, args)

class StatsNode(template.Node):
    def __init__(self, value, varname=None):
        self.value = value
        self.varname = varname

    def render(self, context):
        print self.varname
        if self.varname:
            context[self.varname] = self.value
            return ''
        else:
            return self.value



#~ @register.tag
#~ def count_books_all(*args, **kwargs):
    #~ print args, kwargs
    #~ return StatsNode(Book.objects.all().count())

@register.tag
def count_books_nonempty(parser, token):
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        args = None
    return StatsNode(Book.objects.exclude(html_file='').count(), args)

#~ @register.simple_tag
#~ def count_books_empty():
    #~ return Book.objects.exclude(html_file='').count()
#~ 
#~ @register.simple_tag
#~ def count_books_root():
    #~ return Book.objects.filter(parent=None).count()
