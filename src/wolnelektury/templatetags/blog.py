# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from datetime import date
from django.conf import settings
from django.template import Library
import feedparser


register = Library()


@register.inclusion_tag('latest_blog_posts.html')
def latest_blog_posts(feed_url=None, posts_to_show=5):
    if feed_url is None:
        feed_url = settings.LATEST_BLOG_POSTS
    posts = []
    try:
        feed = feedparser.parse(str(feed_url))
        for i in range(posts_to_show):
            pub_date = feed['entries'][i].published_parsed
            published = date(pub_date[0], pub_date[1], pub_date[2])
            posts.append({
                'title': feed['entries'][i].title,
                'summary': feed['entries'][i].summary,
                'link': feed['entries'][i].link,
                'date': published,
                })
    except:
        pass
    return {
        'posts': posts
    }
