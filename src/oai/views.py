# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from oai.handlers import Catalogue, NS_DCTERMS, nsdcterms
from oaipmh.server import ServerBase, NS_OAIDC, NS_DC, NS_XSI, nsoaidc, nsdc
from oaipmh.metadata import MetadataRegistry
from django.http import HttpResponse
from django.utils.functional import SimpleLazyObject
from lxml.etree import SubElement



#ns_map = {'oai_dc': NS_OAIDC, 'dc': NS_DC, 'xsi': NS_XSI }


def fbc_oai_dc_writer(element, metadata):
    """FBC notified us that original writer does not output all necessary namespace declarations.
    """
    e_dc = SubElement(element, nsoaidc('dc'),
                      nsmap={'oai_dc': NS_OAIDC, 'dc': NS_DC, 'xsi': NS_XSI})
    e_dc.set('{%s}schemaLocation' % NS_XSI,
             '%s http://www.openarchives.org/OAI/2.0/oai_dc.xsd' % NS_OAIDC)
    map = metadata.getMap()
    for name in [
        'title', 'creator', 'subject', 'description', 'publisher',
        'contributor', 'date', 'type', 'format', 'identifier',
        'source', 'language', 'relation', 'coverage', 'rights',
        ]:
        for value in map.get(name, []):
            e = SubElement(e_dc, nsdc(name))
            e.text = value


def qdc_writer(element, metadata):
    """FBC notified us that original writer does not output all necessary namespace declarations.
    """
    nsmap = {'oai_dc': NS_OAIDC, 'dc': NS_DC, 'xsi': NS_XSI, 'dcterms': NS_DCTERMS}
    map = metadata.getMap()
    for name in [
        'title', 'creator', 'subject', 'description', 'publisher',
        'contributor', 'date', 'type', 'format', 'identifier',
        'source', 'language', 'relation', 'coverage', 'rights',
        ]:
        for value in map.get(name, []):
            e = SubElement(element, nsdc(name), nsmap=nsmap)
            e.text = value

    for name in ['hasPart', 'isPartOf']:
        for value in map.get(name, []):
            e = SubElement(element, nsdcterms(name), nsmap=nsmap)
            e.text = value



metadata_registry = MetadataRegistry()
metadata_registry.registerWriter('oai_dc', fbc_oai_dc_writer)
metadata_registry.registerWriter('qdc', qdc_writer)


server = SimpleLazyObject(lambda: 
    ServerBase(Catalogue(metadata_registry), metadata_registry,
        {'topxsi': NS_XSI})
    )


def oaipmh(request):
    resp = server.handleRequest(request.GET)
    return HttpResponse(resp, content_type='application/xml')
