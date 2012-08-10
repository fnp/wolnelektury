
from oai.handlers import Catalogue
from oaipmh.server import ServerBase, oai_dc_writer, NS_OAIDC, NS_DC, NS_XSI
from oaipmh.metadata import MetadataRegistry
from django.http import HttpResponse
from lxml.etree import tostring

metadata_registry = MetadataRegistry()
metadata_registry.registerWriter('oai_dc', oai_dc_writer)
ns_map = {'oai_dc': NS_OAIDC, 'dc': NS_DC, 'xsi': NS_XSI}

server = ServerBase(Catalogue(metadata_registry), metadata_registry, ns_map)


def oaipmh(request):
    resp = server.handleRequest(request.GET)
    return HttpResponse(resp)
