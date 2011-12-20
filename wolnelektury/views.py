from datetime import datetime

from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.http import urlquote_plus
from django.utils.translation import ugettext_lazy as _
from django.views.decorators import cache

from ajaxable.utils import AjaxableFormView
from catalogue.models import Book


def main_page(request):
    last_published = Book.objects.exclude(html_file='').order_by('-created_at')[:4]

    return render_to_response("main_page.html", locals(),
        context_instance=RequestContext(request))


class LoginFormView(AjaxableFormView):
    form_class = AuthenticationForm
    #template = "auth/login.html"
    title = _('Sign in')
    submit = _('Sign in')

    def __call__(self, request):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/')
        return super(LoginFormView, self).__call__(request)

    def success(self, form, request):
        auth.login(request, form.get_user())


class RegisterFormView(AjaxableFormView):
    form_class = UserCreationForm
    #template = "auth/register.html"
    title = _('Register')
    submit = _('Register')

    def __call__(self, request):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/')
        return super(RegisterFormView, self).__call__(request)

    def success(self, form, request):
        user = form.save()
        user = auth.authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1']
        )
        auth.login(request, user)


@cache.never_cache
def logout_then_redirect(request):
    auth.logout(request)
    return HttpResponseRedirect(urlquote_plus(request.GET.get('next', '/'), safe='/?='))


def clock(request):
    """ Provides server time for jquery.countdown,
    in a format suitable for Date.parse()
    """
    return HttpResponse(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
