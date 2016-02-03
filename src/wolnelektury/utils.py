# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
import os
from functools import wraps

import pytz
from inspect import getargspec

from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

tz = pytz.timezone(settings.TIME_ZONE)


def localtime_to_utc(localtime):
    return timezone.utc.normalize(
        tz.localize(localtime)
    )


def utc_for_js(dt):
    return dt.strftime('%Y/%m/%d %H:%M:%S UTC')


def makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def stringify_keys(dictionary):
    return dict((keyword.encode('ascii'), value)
                for keyword, value in dictionary.iteritems())


def json_encode(obj, sort_keys=True, ensure_ascii=False):
    return json.dumps(obj, sort_keys=sort_keys, ensure_ascii=ensure_ascii)


def json_decode(obj):
    return json.loads(obj)


def json_decode_fallback(value):
    try:
        return json_decode(value)
    except ValueError:
        return value


class AjaxError(Exception):
    pass


def ajax(login_required=True, method=None, template=None, permission_required=None):
    def decorator(fun):
        @wraps(fun)
        def ajax_view(request):
            kwargs = {}
            request_params = None
            if method == 'post':
                request_params = request.POST
            elif method == 'get':
                request_params = request.GET
            fun_params, xx, fun_kwargs, defaults = getargspec(fun)
            if defaults:
                required_params = fun_params[1:-len(defaults)]
            else:
                required_params = fun_params[1:]
            missing_params = set(required_params) - set(request_params)
            if missing_params:
                res = {
                    'result': 'missing params',
                    'missing': ', '.join(missing_params),
                }
            else:
                if request_params:
                    request_params = dict(
                        (key, json_decode_fallback(value))
                        for key, value in request_params.iteritems()
                        if fun_kwargs or key in fun_params)
                    kwargs.update(stringify_keys(request_params))
                res = None
                if login_required and not request.user.is_authenticated():
                    res = {'result': 'logout'}
                if (permission_required and
                        not request.user.has_perm(permission_required)):
                    res = {'result': 'access denied'}
            if not res:
                try:
                    res = fun(request, **kwargs)
                    if res and template:
                        res = {'html': render_to_string(template, res, RequestContext(request))}
                except AjaxError as e:
                    res = {'result': e.args[0]}
            if 'result' not in res:
                res['result'] = 'ok'
            return HttpResponse(json_encode(res), content_type='application/json; charset=utf-8',
                                status=200 if res['result'] == 'ok' else 400)

        return ajax_view

    return decorator
