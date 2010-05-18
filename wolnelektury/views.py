# -*- coding: utf-8 -*-

from django import http
from django.template import RequestContext, loader

def server_error(request):
    t = loader.get_template('500.html')
    return http.HttpResponseServerError(t.render(RequestContext(request)))

