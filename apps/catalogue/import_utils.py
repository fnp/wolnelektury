# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from librarian import DocProvider

class ORMDocProvider(DocProvider):
    """Used for getting books' children."""

    def __init__(self, book):
        self.book = book

    def by_slug(self, slug):
        if slug == self.book.slug:
            return open(self.book.xml_file.path)
        else:
            return type(self.book).objects.get(slug=slug).xml_file