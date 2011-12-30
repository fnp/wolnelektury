from datetime import datetime
import feedparser

from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.http import urlquote_plus
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache

from django.conf import settings
from ajaxable.utils import AjaxableFormView
from catalogue.models import Book


def main_page(request):
    last_published = Book.objects.exclude(html_file='').order_by('-created_at')[:4]

    return render_to_response("main_page.html", locals(),
        context_instance=RequestContext(request))


class LoginFormView(AjaxableFormView):
    form_class = AuthenticationForm
    title = _('Sign in')
    submit = _('Sign in')
    ajax_redirect = True

    def __call__(self, request):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/')
        return super(LoginFormView, self).__call__(request)

    def success(self, form, request):
        auth.login(request, form.get_user())


class RegisterFormView(AjaxableFormView):
    form_class = UserCreationForm
    title = _('Register')
    submit = _('Register')
    ajax_redirect = True

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


@never_cache
def logout_then_redirect(request):
    auth.logout(request)
    return HttpResponseRedirect(urlquote_plus(request.GET.get('next', '/'), safe='/?='))


def clock(request):
    """ Provides server time for jquery.countdown,
    in a format suitable for Date.parse()
    """
    return HttpResponse(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))


def publish_plan(request):
    cache_key = "publish_plan"
    plan = cache.get(cache_key)

    if plan is None:
        plan = []
        try:
            feed = feedparser.parse(settings.PUBLISH_PLAN_FEED)
        except:
            pass
        else:
            for i in range(len(feed['entries'])):
                print i
                plan.append({
                    'title': feed['entries'][i].title,
                    'link': feed['entries'][i].link,
                    })
        cache.set(cache_key, plan, 1800)

    return render_to_response("publish_plan.html", {'plan': plan},
        context_instance=RequestContext(request))
