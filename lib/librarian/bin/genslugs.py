#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import optparse

from lxml import etree
from librarian import html
from slughifi import slughifi


BOOK_URL = 'http://wolnelektury.pl/katalog/lektura/'


if __name__ == '__main__':
    # Parse commandline arguments
    usage = """Usage: %prog [options] SOURCE [SOURCE...]
    Generate slugs for SOURCE."""

    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False,
        help='print status messages to stdout')

    options, input_filenames = parser.parse_args()

    if len(input_filenames) < 1:
        parser.print_help()
        exit(1)

    # Do some real work
    for input_filename in input_filenames:
        if options.verbose:
            print input_filename
        
        doc = etree.parse(input_filename)
        try:
            title = doc.find('//{http://purl.org/dc/elements/1.1/}title').text
        except AttributeError:
            print '%s:error:book title not found, skipping' % input_filename
            continue
        
        parent = ''
        try:
            parent_url = doc.find('//{http://purl.org/dc/elements/1.1/}relation.isPartOf').text
            parent = parent_url.rsplit('/', 1)[1] + ' '
        except AttributeError:
            pass
        
        book_url = doc.find('//{http://purl.org/dc/elements/1.1/}identifier.url')
        if book_url is None:
            book_description = doc.find('//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')
            book_url = etree.SubElement(book_description, '{http://purl.org/dc/elements/1.1/}identifier.url')
        elif book_url.text.startswith('http://'):
            print '%s:notice:book already has identifier starting with http://, skipping' % input_filename
            continue
        book_url.text = BOOK_URL + slughifi(parent + title)

        doc.write(input_filename, xml_declaration=True, pretty_print=True, encoding='utf-8')

