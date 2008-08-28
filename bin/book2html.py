#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cStringIO
import re
import optparse
import os
import sys

from lxml import etree


def transform(input_filename, output_filename):
    """Transforms file input_filename in XML to output_filename in XHTML."""
    # Parse XSLT
    style_filename = os.path.join(os.path.dirname(__file__), 'book2html.xslt')
    style = etree.parse(style_filename)

    doc_file = cStringIO.StringIO()
    expr = re.compile(r'/\s', re.MULTILINE | re.UNICODE);

    f = open(input_filename, 'r')
    for line in f:
        line = line.decode('utf-8')
        line = expr.sub(u'<br/>\n', line).replace(u'---', u'—').replace(u',,', u'„')
        doc_file.write(line.encode('utf-8'))
    f.close()

    doc_file.seek(0);

    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(doc_file, parser)

    result = doc.xslt(style)
    result.write(output_filename, xml_declaration=True, pretty_print=True, encoding='utf-8')


if __name__ == '__main__':
    # Parse commandline arguments
    usage = """Usage: %prog [options] SOURCE [SOURCE...]
    Convert SOURCE files to HTML format."""

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
        
        output_filename = os.path.splitext(input_filename)[0] + '.html'
        transform(input_filename, output_filename)

