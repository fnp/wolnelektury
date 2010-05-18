# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext

def server_error(request):
    return render_to_response('500.html', RequestContext(request))

