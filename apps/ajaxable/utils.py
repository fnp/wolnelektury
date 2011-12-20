from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.encoding import force_unicode
from django.utils.functional import Promise
from django.utils.http import urlquote_plus
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _


class LazyEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj

# shortcut for JSON reponses
class JSONResponse(HttpResponse):
    def __init__(self, data={}, callback=None, **kwargs):
        # get rid of mimetype
        kwargs.pop('mimetype', None)
        data = simplejson.dumps(data)
        if callback:
            data = callback + "(" + data + ");" 
        super(JSONResponse, self).__init__(data, mimetype="application/json", **kwargs)



class AjaxableFormView(object):
    """Subclass this to create an ajaxable view for any form.

    In the subclass, provide at least form_class.

    """
    form_class = None
    # override to customize form look
    template = "ajaxable/form.html"
    # set to redirect after succesful ajax-less post
    submit = _('Send')
    redirect = None
    title = ''
    success_message = ''
    formname = "form"
    full_template = "ajaxable/form_on_page.html"

    def __call__(self, request):
        """A view displaying a form, or JSON if `ajax' GET param is set."""
        ajax = request.GET.get('ajax', False)
        if request.method == "POST":
            form = self.form_class(data=request.POST)
            if form.is_valid():
                self.success(form, request)
                redirect = request.GET.get('next')
                if not ajax and redirect is not None:
                    return HttpResponseRedirect(urlquote_plus(
                                redirect, safe='/?='))
                response_data = {'success': True, 'message': self.success_message}
            else:
                response_data = {'success': False, 'errors': form.errors}
            if ajax:
                return HttpResponse(LazyEncoder(ensure_ascii=False).encode(response_data))
        else:
            form = self.form_class()
            response_data = None

        template = self.template if ajax else self.full_template
        return render_to_response(template, {
                self.formname: form, 
                "title": self.title,
                "submit": self.submit,
                "response_data": response_data,
                "ajax_template": self.template,
            },
            context_instance=RequestContext(request))

    def success(self, form, request):
        """What to do when the form is valid.
        
        By default, just save the form.

        """
        return form.save(request)
