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

from ajaxable.utils import AjaxableFormView
from ajaxable.utils import placeholdized
from catalogue.models import Book, Collection, Tag, Fragment
import club.models
from social.utils import get_or_choose_cite
from wolnelektury.forms import RegistrationForm, SocialSignupForm, WLAuthenticationForm


def main_page_2022(request):
    ctx = {}
    ctx['last_published'] = Book.objects.exclude(cover_clean='').filter(findable=True, parent=None).order_by('-created_at')[:10]
    ctx['recommended_collection'] = Collection.objects.filter(listed=True, role='recommend').order_by('?').first()
    ctx['ambassadors'] = club.models.Ambassador.objects.all().order_by('?')
    ctx['widget'] = settings.WIDGETS.get(request.GET.get('w'))
    if not ctx['widget'] and request.EXPERIMENTS['sowka'].value:
        ctx['widget'] = settings.WIDGETS['pan-sowka']
    return render(request, '2022/main_page.html', ctx)

@never_cache
def main_page(request):
    if request.GET.get('w') in settings.WIDGETS:
        request.EXPERIMENTS['layout'].override(True)
    if request.EXPERIMENTS['sowka'].value:
        request.EXPERIMENTS['layout'].override(True)

    if request.EXPERIMENTS['layout'].value:
        return main_page_2022(request)

    ctx = {
        'last_published': Book.objects.exclude(cover_thumb='').filter(findable=True, parent=None).order_by('-created_at')[:6],
        'theme_books': [],
    }

    # FIXME: find this theme and books properly.
    if Fragment.objects.exists():
        while True:
            ctx['theme'] = Tag.objects.filter(category='theme').order_by('?')[:1][0]
            tf = Fragment.tagged.with_any([ctx['theme']]).select_related('book').filter(book__findable=True).order_by('?')[:100]
            if not tf:
                continue
            ctx['theme_fragment'] = tf[0]
            for f in tf:
                if f.book not in ctx['theme_books']:
                    ctx['theme_books'].append(f.book)
                if len(ctx['theme_books']) == 3:
                    break
            break

    # Choose collections for main.
    ctx['collections'] = Collection.objects.filter(listed=True).order_by('?')[:4]

    best = []
    best_places = 5
    recommended_collection = None
    for recommended in Collection.objects.filter(listed=True, role='recommend').order_by('?'):
        if recommended_collection is None:
            recommended_collection = recommended
        books = list(recommended.get_books().exclude(id__in=[b.id for b in best]).order_by('?')[:best_places])
        best.extend(books)
        best_places -= len(books)
        if not best_places:
            break
    ctx['recommended_collection'] = recommended_collection
    if best_places:
        best.extend(
            list(
                Book.objects.filter(findable=True).exclude(id__in=[b.id for b in best]).order_by('?')[:best_places]
            )
        )
    ctx['best'] = best

    return render(request, "main_page.html", ctx)


class WLLoginView(LoginView):
    form_class = WLAuthenticationForm


wl_login_view = WLLoginView.as_view()


class LoginFormView(AjaxableFormView):
    form_class = AuthenticationForm
    template = "auth/login.html"
    placeholdize = True
    title = _('Sign in')
    submit = _('Sign in')
    ajax_redirect = True

    def __call__(self, request):
        if request.EXPERIMENTS['layout'].value:
            return wl_login_view(request)

        if request.user.is_authenticated:
            return self.redirect_or_refresh(
                request, '/',
                message=_('Already logged in as user %(user)s', ) % {'user': request.user.username})
        return super(LoginFormView, self).__call__(request)

    def success(self, form, request):
        auth.login(request, form.get_user())


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

wl_register_view = WLRegisterView.as_view()


class RegisterFormView(AjaxableFormView):
    form_class = RegistrationForm
    template = "auth/register.html"
    placeholdize = True
    title = _('Register')
    submit = _('Register')
    ajax_redirect = True
    form_prefix = 'register'
    honeypot = True

    def __call__(self, request):
        if request.EXPERIMENTS['layout'].value:
            return wl_register_view(request)

        if request.user.is_authenticated:
            return self.redirect_or_refresh(
                request, '/',
                message=_('Already logged in as user %(user)s', ) % {'user': request.user.username})
        return super(RegisterFormView, self).__call__(request)

    def success(self, form, request):
        form.save()
        user = auth.authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1']
        )
        auth.login(request, user)


class LoginRegisterFormView(LoginFormView):
    template = 'auth/login_register.html'
    title = _('You have to be logged in to continue')

    def extra_context(self, request, obj):
        return {
            "register_form": placeholdized(RegistrationForm(prefix='register')),
            "register_submit": _('Register'),
        }


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


def exception_test(request):
    msg = request.GET.get('msg')
    if msg:
        raise Exception('Exception test: %s' % msg)
    else:
        raise Exception('Exception test')


def post_test(request):
    return render(request, 'post_test.html', {'action': '/api/reading/jego-zasady/complete/'})
