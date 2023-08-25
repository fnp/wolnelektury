# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import date, datetime
from urllib.parse import quote_plus
import feedparser
from allauth.socialaccount.views import SignupView

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.views.generic import FormView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache

from catalogue.models import Book, Collection, Tag, Fragment
import club.models
from social.utils import get_or_choose_cite
from wolnelektury.forms import RegistrationForm, SocialSignupForm, WLAuthenticationForm


@never_cache
def main_page(request):
    if request.GET.get('w') in settings.WIDGETS:
        request.EXPERIMENTS['layout'].override(True)
    if request.EXPERIMENTS['sowka'].value:
        request.EXPERIMENTS['layout'].override(True)

    ctx = {}
    ctx['last_published'] = Book.objects.exclude(cover_clean='').filter(findable=True, parent=None).order_by('-created_at')[:10]
    ctx['recommended_collection'] = Collection.objects.filter(listed=True, role='recommend').order_by('?').first()
    ctx['ambassadors'] = club.models.Ambassador.objects.all().order_by('?')
    ctx['widget'] = settings.WIDGETS.get(request.GET.get('w'))
    if not ctx['widget'] and request.EXPERIMENTS['sowka'].value:
        ctx['widget'] = settings.WIDGETS['pan-sowka']
    return render(request, 'main_page.html', ctx)


class WLLoginView(LoginView):
    form_class = WLAuthenticationForm


class WLRegisterView(FormView):
    form_class = RegistrationForm
    template_name = 'registration/register.html'

    def form_valid(self, form):
        form.save()
        user = auth.authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1']
        )
        auth.login(self.request, user)
        return HttpResponseRedirect(quote_plus(self.request.GET.get('next', '/'), safe='/?='))


@never_cache
def logout_then_redirect(request):
    auth.logout(request)
    return HttpResponseRedirect(quote_plus(request.GET.get('next', '/'), safe='/?='))


@never_cache
def clock(request):
    """ Provides server UTC time for jquery.countdown,
    in a format suitable for Date.parse()
    """
    return HttpResponse(datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S UTC'))


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
                plan.append({
                    'title': feed['entries'][i].title,
                    'link': feed['entries'][i].link,
                    })
        cache.set(cache_key, plan, 1800)

    return render(request, "publish_plan.html", {'plan': plan})


@login_required
def user_settings(request):
    return render(request, "user.html")


def widget(request):
    return render(request, 'widget.html')


class SocialSignupView(SignupView):
    form_class = SocialSignupForm
