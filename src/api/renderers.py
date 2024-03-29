# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from rest_framework_xml.renderers import XMLRenderer


class LegacyXMLRenderer(XMLRenderer):
    """
    Renderer which serializes to XML.
    """

    item_tag_name = 'resource'
    root_tag_name = 'response'
