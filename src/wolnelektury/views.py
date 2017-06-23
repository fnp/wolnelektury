# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import date, datetime
import feedparser

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.http import urlquote_plus
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache

from ajaxable.utils import AjaxableFormView
from ajaxable.utils import placeholdized
from catalogue.models import Book, Collection, Tag, Fragment
from ssify import ssi_included

from social.utils import get_or_choose_cite
from wolnelektury.forms import RegistrationForm


def main_page(request):
    ctx = {
        'last_published': Book.objects.exclude(cover_thumb='').filter(parent=None).order_by('-created_at')[:6],
        'theme_books': [],
        'cite': get_or_choose_cite(request),
    }

    # for category in ('author', 'epoch', 'genre', 'kind'):
    #     try:
    #         ctx[category] = Tag.objects.filter(category=category).order_by('?')[:1][0]
    #     except IndexError:
    #         pass

    # FIXME: find this theme and books properly.
    if Fragment.objects.exists():
        while True:
            ctx['theme'] = Tag.objects.filter(category='theme').order_by('?')[:1][0]
            tf = Fragment.tagged.with_any([ctx['theme']]).select_related('book').order_by('?')[:100]
            if not tf:
                continue
            ctx['theme_fragment'] = tf[0]
            for f in tf:
                if f.book not in ctx['theme_books']:
                    ctx['theme_books'].append(f.book)
                if len(ctx['theme_books']) == 3:
                    break
            break

    # Choose a collection for main.
    try:
        ctx['collection'] = Collection.objects.order_by('?')[:1][0]
    except IndexError:
        pass

    ctx['best'] = Book.objects.order_by('?')[:5]

    return render(request, "main_page.html", ctx)


class LoginFormView(AjaxableFormView):
    form_class = AuthenticationForm
    template = "auth/login.html"
    placeholdize = True
    title = _('Sign in')
    submit = _('Sign in')
    ajax_redirect = True

    def __call__(self, request):
        if request.user.is_authenticated():
            return self.redirect_or_refresh(
                request, '/',
                message=_('Already logged in as user %(user)s', ) % {'user': request.user.username})
        return super(LoginFormView, self).__call__(request)

    def success(self, form, request):
        auth.login(request, form.get_user())


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
        if request.user.is_authenticated():
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
            "register_form": placeholdized(UserCreationForm(prefix='register')),
            "register_submit": _('Register'),
        }


@never_cache
def logout_then_redirect(request):
    auth.logout(request)
    return HttpResponseRedirect(urlquote_plus(request.GET.get('next', '/'), safe='/?='))


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


@ssi_included(use_lang=False, timeout=1800)
def latest_blog_posts(request, feed_url=None, posts_to_show=5):
    if feed_url is None:
        feed_url = settings.LATEST_BLOG_POSTS
    try:
        feed = feedparser.parse(str(feed_url))
        posts = []
        for i in range(posts_to_show):
            pub_date = feed['entries'][i].published_parsed
            published = date(pub_date[0], pub_date[1], pub_date[2])
            posts.append({
                'title': feed['entries'][i].title,
                'summary': feed['entries'][i].summary,
                'link': feed['entries'][i].link,
                'date': published,
                })
    except:
        posts = []
    return render(request, 'latest_blog_posts.html', {'posts': posts})


@ssi_included(use_lang=False)
def widget(request):
    return render(request, 'widget.html')


def exception_test(request):
    raise Exception('Exception test')