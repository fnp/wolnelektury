#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import optparse
import codecs


REGEXES = [
    (r'<rdf:RDF[^>]*>(.|\n)*?</rdf:RDF>', ''),
    (r'<motyw[^>]*>(.|\n)*?</motyw>', ''),
    ('<(begin|end)\\sid=[\'|"][b|e]\\d+[\'|"]\\s/>', ''),
    (r'<extra>((<!--<(elementy_poczatkowe|tekst_glowny)>-->)|(<!--</(elementy_poczatkowe|tekst_glowny)>-->))</extra>', ''),
    (r'<uwaga>(.|\n)*?</uwaga>', ''),
    (r'<p[a|e|r|t]>(.|\n)*?</p[a|e|r|t]>', ''),
    (r'<[^>]+>', ''),
    (r'/\n', ''),
    (r'---', u'—'),
    (r'--', u'-'),
    (r',,', u'„'),
    (r'"', u'”'),
]


if __name__ == '__main__':
    # Parse commandline arguments
    usage = """Usage: %prog [options] SOURCE [SOURCE...]
    Convert SOURCE files to TXT format."""

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
        
        output_filename = os.path.splitext(input_filename)[0] + '.txt'
        
        xml = codecs.open(input_filename, 'r', encoding='utf-8').read()
        for pattern, repl in REGEXES:
            # print pattern, repl
            xml, n = re.subn(pattern, repl, xml)
            # print n
            
        output = codecs.open(output_filename, 'w', encoding='utf-8')
        output.write(xml)

