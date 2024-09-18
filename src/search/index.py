# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import re
from librarian.elements.base import WLElement
from librarian.document import WLDocument
from lxml import etree


class Index:
    """
    Class indexing books.
    """
    master_tags = [
        'opowiadanie',
        'powiesc',
        'dramat_wierszowany_l',
        'dramat_wierszowany_lp',
        'dramat_wspolczesny', 'liryka_l', 'liryka_lp',
        'wywiad',
    ]

    ignore_content_tags = [
        'uwaga', 'extra', 'nota_red', 'abstrakt',
        'zastepnik_tekstu', 'sekcja_asterysk', 'separator_linia', 'zastepnik_wersu',
        'didaskalia',
        'naglowek_aktu', 'naglowek_sceny', 'naglowek_czesc', 'motyw'
    ]

    footnote_tags = ['pa', 'pt', 'pr', 'pe']

    skip_header_tags = ['autor_utworu', 'nazwa_utworu', 'dzielo_nadrzedne',
                        '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF']

    @staticmethod
    def add_snippet(book, text, position, anchor):
        book.snippet_set.create(
            sec=position + 1,
            text=text,
            anchor=anchor
        )

    # TODO: The section links stuff won't work.
    @classmethod
    def index_book(cls, book):
        """
        Walks the book XML and extract content from it.
        Adds parts for each header tag and for each fragment.
        """
        if not book.xml_file: return

        book.snippet_set.all().delete()

        wld = WLDocument(filename=book.xml_file.path)
        wld.assign_ids()

        master = wld.tree.getroot().master
        if master is None:
            return []

        def get_indexable(element):
            for child in element:
                if not isinstance(child, WLElement):
                    continue
                if not child.attrib.get('_id'):
                    for e in get_indexable(child):
                        yield e
                else:
                    yield child

        def walker(node):
            if node.tag not in cls.ignore_content_tags:
                yield node, None, None
                if node.text is not None:
                    yield None, node.text, None
                for child in list(node):
                    for b, t, e in walker(child):
                        yield b, t, e
                yield None, None, node

            if node.tail is not None:
                yield None, node.tail, None
            return

        def fix_format(text):
            if isinstance(text, list):
                text = filter(lambda s: s is not None, content)
                text = ' '.join(text)

            return re.sub("(?m)/$", "", text)

        for position, header in enumerate(get_indexable(master)):
            if header.tag in cls.skip_header_tags:
                continue
            if header.tag is etree.Comment:
                continue

            el_id = header.attrib['_id']

            # section content
            content = []
            footnote = []

            def all_content(text):
                content.append(text)
            handle_text = [all_content]

            for start, text, end in walker(header):
                # handle footnotes
                if start is not None and start.tag in cls.footnote_tags:
                    footnote = []

                    def collect_footnote(t):
                        footnote.append(t)

                    handle_text.append(collect_footnote)
                elif end is not None and footnote is not [] and end.tag in cls.footnote_tags:
                    handle_text.pop()
                    cls.add_snippet(book, ''.join(footnote), position, el_id)
                    footnote = []

                if text is not None and handle_text is not []:
                    hdl = handle_text[-1]
                    hdl(text)

            # in the end, add a section text.
            cls.add_snippet(book, fix_format(content), position, el_id)
