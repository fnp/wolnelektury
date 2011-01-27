# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse

from catalogue import models

def absolute_url(url):
    return "http://%s%s" % (Site.objects.get_current().domain, url)


class AudiobookFeed(Feed):
    description = "Audiobooki ostatnio dodane do serwisu Wolne Lektury."

    mime_types = {
        'mp3': 'audio/mpeg',
        'ogg': 'audio/ogg',
        'daisy': 'application/zip',
    }

    titles = {
        'all': 'WolneLektury.pl - audiobooki we wszystkich formatach',
        'mp3': 'WolneLektury.pl - audiobooki w formacie MP3',
        'ogg': 'WolneLektury.pl - audiobooki w formacie Ogg Vorbis',
        'daisy': 'WolneLektury.pl - audiobooki w formacie DAISY',
    }

    def get_object(self, request, type):
        return type

    def title(self, type):
        return self.titles[type]

    def link(self, type):
        return reverse('audiobook_feed', args=(type,))

    def items(self, type):
        objects = models.BookMedia.objects.order_by('-uploaded_at')
        if type == 'all':
            objects = objects.filter(type__in=('mp3', 'ogg', 'daisy'))
        else:
            objects = objects.filter(type=type)
        return objects[:20]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        lines = []
        artist = item.get_extra_info_value().get('artist_name', None)
        if artist is not None:
            lines.append(u'Czyta: %s' % artist)
        director = item.get_extra_info_value().get('artist_name', None)
        if director is not None:
            lines.append(u'Reżyseruje: %s' % director)
        return u'<br/>\n'.join(lines)

    def item_link(self, item):
        if item.book_set.exists():
            return item.book_set.all()[0].get_absolute_url()
        else:
            return item.file.url

    def item_guid(self, item):
        return absolute_url(item.file.url)

    def item_enclosure_url(self, item):
        return absolute_url(item.file.url)

    def item_enclosure_length(self, item):
        return item.file.size

    def item_enclosure_mime_type(self, item):
        return self.mime_types[item.type]

    def item_pubdate(self, item):
        return item.uploaded_at
