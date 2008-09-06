# -*- coding: utf-8 -*-
from xml.parsers.expat import ExpatError

# Import ElementTree from anywhere
try:
    import xml.etree.ElementTree as ET # Python >= 2.5
except ImportError:
    try:
        import elementtree.ElementTree as ET # effbot's pure Python module
    except ImportError:
        import lxml.etree as ET # ElementTree API using libxml2

import converters


__all__ = ('parse', 'ParseError')


class ParseError(Exception):
    def __init__(self, message):
        super(self, Exception).__init__(message)


class XMLNamespace(object):
    '''Represents XML namespace.'''
    
    def __init__(self, uri):
        self.uri = uri

    def __call__(self, tag):
        return '{%s}%s' % (self.uri, tag)

    def __contains__(self, tag):
        return tag.startswith(str(self))

    def __repr__(self):
        return 'XMLNamespace(%r)' % self.uri
    
    def __str__(self):
        return '%s' % self.uri


class BookInfo(object):
    RDF = XMLNamespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    DC = XMLNamespace('http://purl.org/dc/elements/1.1/')
    
    mapping = {
        DC('creator')        : ('author', converters.str_to_person),
        DC('title')          : ('title', converters.str_to_unicode),
        DC('subject.period') : ('epoch', converters.str_to_unicode),
        DC('subject.type')   : ('kind', converters.str_to_unicode),
        DC('subject.genre')  : ('genre', converters.str_to_unicode),
        DC('date')           : ('created_at', converters.str_to_date),
        DC('date.pd')        : ('released_to_public_domain_at', converters.str_to_date),
        DC('contributor.translator') : ('translator', converters.str_to_person),
        DC('contributor.technical_editor') : ('technical_editor', converters.str_to_person),
        DC('publisher')      : ('publisher', converters.str_to_unicode),
        DC('source')         : ('source_name', converters.str_to_unicode),
        DC('source.URL')     : ('source_url', converters.str_to_unicode),
        DC('identifier.url') : ('url', converters.str_to_unicode),
        DC('relation.hasPart') : ('parts', converters.str_to_unicode_list),
    }

    @classmethod
    def from_string(cls, xml):
        from StringIO import StringIO
        return cls.from_file(StringIO(xml))
    
    @classmethod
    def from_file(cls, xml_file):
        book_info = cls()
        
        try:
            tree = ET.parse(xml_file)
        except ExpatError, e:
            raise ParseError(e)

        description = tree.find('//' + book_info.RDF('Description'))
        if description is None:
            raise ParseError('no Description tag found in document')
        
        for element in description.findall('*'):
            book_info.parse_element(element) 
        
        return book_info

    def parse_element(self, element):
        try:
            attribute, converter = self.mapping[element.tag]
            setattr(self, attribute, converter(element.text, getattr(self, attribute, None)))
        except KeyError:
            pass

    def to_xml(self):
        """XML representation of this object."""
        ET._namespace_map[str(self.RDF)] = 'rdf'
        ET._namespace_map[str(self.DC)] = 'dc'
        
        root = ET.Element(self.RDF('RDF'))
        description = ET.SubElement(root, self.RDF('Description'))
        
        for tag, (attribute, converter) in self.mapping.iteritems():
            if hasattr(self, attribute):
                e = ET.Element(tag)
                e.text = unicode(getattr(self, attribute))
                description.append(e)
        
        return unicode(ET.tostring(root, 'utf-8'), 'utf-8')


def parse(file_name):
    return BookInfo.from_file(file_name)


if __name__ == '__main__':
    import sys
    
    info = parse(sys.argv[1])
    for attribute, _ in BookInfo.mapping.values():
        print '%s: %r' % (attribute, getattr(info, attribute, None))

