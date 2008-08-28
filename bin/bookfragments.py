#!/usr/bin/env python
# -*- coding: utf-8 -*-
import optparse
import os
import copy

from lxml import etree


class Fragment(object):
    def __init__(self, id, themes):
        super(Fragment, self).__init__()
        self.id = id
        self.themes = themes
        self.events = []
        
    def append(self, event, element):
        self.events.append((event, element))
    
    def closed_events(self):
        stack = []
        for event, element in self.events:
            if event == 'start':
                stack.append(('end', element))
            elif event == 'end':
                try:
                    stack.pop()
                except IndexError:
                    print 'CLOSED NON-OPEN TAG:', element
        
        stack.reverse()
        return self.events + stack
    
    def to_string(self):
        result = []
        for event, element in self.closed_events():
            if event == 'start':
                result.append(u'<%s %s>' % (element.tag, ' '.join('%s="%s"' % (k, v) for k, v in element.attrib.items())))
                if element.text:
                    result.append(element.text)
            elif event == 'end':
                result.append(u'</%s>' % element.tag)
                if element.tail:
                    result.append(element.tail)
            else:
                result.append(element)
        
        return ''.join(result)
    
    def __unicode__(self):
        return self.to_string()


def extract_fragments(input_filename):
    """Extracts theme fragments from input_filename."""
    open_fragments = {}
    closed_fragments = {}
    
    for event, element in etree.iterparse(input_filename, events=('start', 'end')):
        # Process begin and end elements
        if element.tag == 'span' and element.get('class', '') in ('theme-begin', 'theme-end'):
            if not event == 'end': continue # Process elements only once, on end event
            
            # Open new fragment
            if element.get('class', '') == 'theme-begin':
                fragment = Fragment(id=element.get('fid'), themes=element.text)
                
                # Append parents
                if element.getparent().tag != 'body':
                    parents = [element.getparent()]
                    while parents[-1].getparent().tag != 'body':
                        parents.append(parents[-1].getparent())
                    
                    parents.reverse()
                    for parent in parents:
                        fragment.append('start', parent)
                
                open_fragments[fragment.id] = fragment
                    
            # Close existing fragment
            else:
                try:
                    fragment = open_fragments[element.get('fid')]
                except KeyError:
                    print '%s:closed not open fragment #%s' % (input_filename, element.get('fid'))
                else:
                    closed_fragments[fragment.id] = fragment
                    del open_fragments[fragment.id]
            
            # Append element tail to lost_text (we don't want to lose any text)
            if element.tail:
                for fragment_id in open_fragments:
                    open_fragments[fragment_id].append('text', element.tail)
        
        
        # Process all elements except begin and end
        else:
            # Omit annotation tags
            if len(element.get('name', '')) or element.get('class', '') == 'annotation':
                if event == 'end' and element.tail:
                    for fragment_id in open_fragments:
                        open_fragments[fragment_id].append('text', element.tail)
            else:
                for fragment_id in open_fragments:
                    open_fragments[fragment_id].append(event, copy.copy(element))
        
    return closed_fragments, open_fragments


if __name__ == '__main__':
    # Parse commandline arguments
    usage = """Usage: %prog [options] SOURCE [SOURCE...]
    Extract theme fragments from SOURCE."""
    
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
    
        output_filename = os.path.splitext(input_filename)[0] + '.fragments.html'
    
        closed_fragments, open_fragments = extract_fragments(input_filename)

        for fragment_id in open_fragments:
            print '%s:warning:unclosed fragment #%s' % (input_filename, fragment_id)

        output_file = open(output_filename, 'w')
        output_file.write("""
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
            <html><head>
                <title>bookfragments output</title>
                <meta http-equiv="content-type" content="text/html;charset=utf-8"/>
                <link rel="stylesheet" href="master.css" type="text/css" media="screen" charset="utf-8" />
            </head>
            <body>""")
        for fragment in closed_fragments.values():
            html = u'<div class="fragment"><h3>[#%s] %s</h3>%s</div>' % (fragment.id, fragment.themes, fragment)
            output_file.write(html.encode('utf-8'))
        output_file.write('</body></html>')
        output_file.close()

