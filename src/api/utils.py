# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.encoding import iri_to_uri
from django.views.decorators.vary import vary_on_headers


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

def oauthlib_response(response_tuple):
    """Creates a django.http.HttpResponse from (headers, body, status) tuple from OAuthlib."""
    headers, body, status = response_tuple
    response = HttpResponse(body, status=status)
    for k, v in headers.items():
        if k == 'Location':
            v = iri_to_uri(v)
        response[k] = v
    return response


vary_on_auth = method_decorator(vary_on_headers('Authorization'), 'dispatch')


class HttpResponseAppRedirect(HttpResponseRedirect):
    allowed_schemes = HttpResponseRedirect.allowed_schemes + ['wolnelekturyapp']
