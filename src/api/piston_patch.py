# -*- coding: utf-8 -*-

# modified from django-piston
import base64
import hmac

from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import get_callable
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from piston import oauth
from piston.authentication import initialize_server_request, INVALID_PARAMS_RESPONSE, send_oauth_error


class OAuthAuthenticationForm(forms.Form):
    oauth_token = forms.CharField(widget=forms.HiddenInput)
    oauth_callback = forms.CharField(widget=forms.HiddenInput)  # changed from URLField - too strict
    # removed authorize_access - redundant
    csrf_signature = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)

        self.fields['csrf_signature'].initial = self.initial_csrf_signature

    def clean_csrf_signature(self):
        sig = self.cleaned_data['csrf_signature']
        token = self.cleaned_data['oauth_token']

        sig1 = OAuthAuthenticationForm.get_csrf_signature(settings.SECRET_KEY, token)

        if sig != sig1:
            raise forms.ValidationError("CSRF signature is not valid")

        return sig

    def initial_csrf_signature(self):
        token = self.initial['oauth_token']
        return OAuthAuthenticationForm.get_csrf_signature(settings.SECRET_KEY, token)

    @staticmethod
    def get_csrf_signature(key, token):
        # Check signature...
        import hashlib  # 2.5
        hashed = hmac.new(key, token, hashlib.sha1)

        # calculate the digest base 64
        return base64.b64encode(hashed.digest())


# The only thing changed in the views below is the form used


def oauth_auth_view(request, token, callback, params):
    form = OAuthAuthenticationForm(initial={
        'oauth_token': token.key,
        'oauth_callback': callback,
    })

    return render_to_response('piston/authorize_token.html',
                              {'form': form}, RequestContext(request))


@login_required
def oauth_user_auth(request):
    oauth_server, oauth_request = initialize_server_request(request)

    if oauth_request is None:
        return INVALID_PARAMS_RESPONSE

    try:
        token = oauth_server.fetch_request_token(oauth_request)
    except oauth.OAuthError, err:
        return send_oauth_error(err)

    try:
        callback = oauth_server.get_callback(oauth_request)
    except:
        callback = None

    if request.method == "GET":
        params = oauth_request.get_normalized_parameters()

        oauth_view = getattr(settings, 'OAUTH_AUTH_VIEW', None)
        if oauth_view is None:
            return oauth_auth_view(request, token, callback, params)
        else:
            return get_callable(oauth_view)(request, token, callback, params)
    elif request.method == "POST":
        try:
            form = OAuthAuthenticationForm(request.POST)
            if form.is_valid():
                token = oauth_server.authorize_token(token, request.user)
                args = '?' + token.to_string(only_key=True)
            else:
                args = '?error=%s' % 'Access not granted by user.'

            if not callback:
                callback = getattr(settings, 'OAUTH_CALLBACK_VIEW')
                return get_callable(callback)(request, token)

            response = HttpResponseRedirect(callback + args)

        except oauth.OAuthError, err:
            response = send_oauth_error(err)
    else:
        response = HttpResponse('Action not allowed.')

    return response
