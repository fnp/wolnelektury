# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import datetime
from celery.task import task
import catalogue.models
from traceback import print_exc

@task
def touch_tag(tag):
    update_dict = {
        'book_count': tag.get_count(),
        'changed_at': datetime.now(),
    }

    type(tag).objects.filter(pk=tag.pk).update(**update_dict)


@task
def index_book(book_id, book_info=None):
    try:
        return catalogue.models.Book.objects.get(id=book_id).search_index(book_info)
    except Exception, e:
        print "Exception during index: %s" % e
        print_exc()
        raise e
