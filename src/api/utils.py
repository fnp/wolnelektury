# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri


def oauthlib_request(request):
    """Creates parameters for OAuthlib's Request from a Django Request."""
    headers = {}
    # We don't have request.content_type yet in 2015,
    # while test client has no META['CONTENT_TYPE'].
    ct = request.META.get('CONTENT_TYPE', getattr(request, 'content_type', None))
    if ct:
        headers["Content-Type"] = ct
    if 'HTTP_AUTHORIZATION' in request.META:
        headers["Authorization"] = request.META['HTTP_AUTHORIZATION']
    return {
        "uri": request.build_absolute_uri(),
        "http_method": request.method,
        "body": request.body,
        "headers": headers,
    }

def oauthlib_response((headers, body, status)):
    """Creates a django.http.HttpResponse from (headers, body, status) tuple from OAuthlib."""
    response = HttpResponse(body, status=status)
    for k, v in headers.items():
        if k == 'Location':
            v = iri_to_uri(v)
        response[k] = v
    return response
