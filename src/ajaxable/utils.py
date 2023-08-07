# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from functools import wraps
import json
from urllib.parse import quote_plus

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.utils.encoding import force_str
from django.utils.functional import Promise
from django.views.decorators.vary import vary_on_headers
from honeypot.decorators import verify_honeypot_value
from wolnelektury.utils import is_ajax


class LazyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Promise):
            return force_str(o)
        return o


def method_decorator(function_decorator):
    """Converts a function decorator to a method decorator.

    It just makes it ignore first argument.
    """
    def decorator(method):
        @wraps(method)
        def wrapped_method(self, *args, **kwargs):
            def function(*fargs, **fkwargs):
                return method(self, *fargs, **fkwargs)
            return function_decorator(function)(*args, **kwargs)
        return wrapped_method
    return decorator


def require_login(request):
    """Return 403 if request is AJAX. Redirect to login page if not."""
    if is_ajax(request):
        return HttpResponseForbidden('Not logged in')
    return HttpResponseRedirect('/uzytkownicy/zaloguj')  # next?=request.build_full_path())


class AjaxableFormView:
    """Subclass this to create an ajaxable view for any form.

    In the subclass, provide at least form_class.

    """
    form_class = None
    # override to customize form look
    template = "ajaxable/form.html"
    submit = 'Send'
    action = ''

    title = ''
    success_message = ''
    POST_login = False
    formname = "form"
    form_prefix = None
    full_template = "ajaxable/form_on_page.html"
    honeypot = False

    @method_decorator(vary_on_headers('X-Requested-With'))
    def __call__(self, request, *args, **kwargs):
        """A view displaying a form, or JSON if request is AJAX."""
        obj = self.get_object(request, *args, **kwargs)

        response = self.validate_object(obj, request)
        if response:
            return response

        form_args, form_kwargs = self.form_args(request, obj)
        if self.form_prefix:
            form_kwargs['prefix'] = self.form_prefix

        if request.method == "POST":
            if self.honeypot:
                response = verify_honeypot_value(request, None)
                if response:
                    return response

            # do I need to be logged in?
            if self.POST_login and not request.user.is_authenticated:
                return require_login(request)

            form_kwargs['data'] = request.POST
            form = self.form_class(*form_args, **form_kwargs)
            if form.is_valid():
                add_args = self.success(form, request)
                response_data = {
                    'success': True,
                    'message': self.success_message,
                    'redirect': request.GET.get('next')
                    }
                if add_args:
                    response_data.update(add_args)
                if not is_ajax(request) and response_data['redirect']:
                    return HttpResponseRedirect(quote_plus(
                        response_data['redirect'], safe='/?=&'))
            elif is_ajax(request):
                # Form was sent with errors. Send them back.
                if self.form_prefix:
                    errors = {}
                    for key, value in form.errors.items():
                        errors["%s-%s" % (self.form_prefix, key)] = value
                else:
                    errors = form.errors
                response_data = {'success': False, 'errors': errors}
            else:
                response_data = None
            if is_ajax(request):
                return HttpResponse(LazyEncoder(ensure_ascii=False).encode(response_data))
        else:
            if self.POST_login and not request.user.is_authenticated and not is_ajax(request):
                return require_login(request)

            form = self.form_class(*form_args, **form_kwargs)
            response_data = None

        title = self.title
        if is_ajax(request):
            template = self.template
        else:
            template = self.full_template
            cd = self.context_description(request, obj)
            if cd:
                title += ": " + cd
        context = {
            self.formname: form,
            "title": title,
            "honeypot": self.honeypot,
            "submit": self.submit,
            "action": self.action,
            "response_data": response_data,
            "ajax_template": self.template,
            "view_args": args,
            "view_kwargs": kwargs,
        }
        context.update(self.extra_context(request, obj))
        return render(request, template, context)

    def validate_object(self, obj, request):
        return None

    def redirect_or_refresh(self, request, path, message=None):
        """If the form is AJAX, refresh the page. If not, go to `path`."""
        if is_ajax(request):
            output = "<script>window.location.reload()</script>"
            if message:
                output = "<div class='normal-text'>" + message + "</div>" + output
            return HttpResponse(output)
        return HttpResponseRedirect(path)

    def get_object(self, request, *args, **kwargs):
        """Override to parse view args and get some associated data."""
        return None

    def form_args(self, request, obj):
        """Override to parse view args and give additional args to the form."""
        return (), {}

    def extra_context(self, request, obj):
        """Override to pass something to template."""
        return {}

    def context_description(self, request, obj):
        """Description to appear in standalone form, but not in AJAX form."""
        return ""

    def success(self, form, request):
        """What to do when the form is valid.

        By default, just save the form.

        """
        return form.save(request)
