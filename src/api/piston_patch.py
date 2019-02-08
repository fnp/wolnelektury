# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from oauthlib.oauth1 import AuthorizationEndpoint
from django.contrib.auth.decorators import login_required
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .request_validator import PistonRequestValidator
from .utils import oauthlib_request, oauthlib_response


class HttpResponseAppRedirect(HttpResponseRedirect):
    allowed_schemes = HttpResponseRedirect.allowed_schemes + ['wolnelekturyapp']


class OAuthAuthenticationForm(forms.Form):
    oauth_token = forms.CharField(widget=forms.HiddenInput)
    oauth_callback = forms.CharField(widget=forms.HiddenInput)  # changed from URLField - too strict
    # removed authorize_access - redundant


@login_required
def oauth_user_auth(request):
    endpoint = AuthorizationEndpoint(PistonRequestValidator())

    if request.method == "GET":
        # Why not just get oauth_token here?
        # This is fairly straightforward, in't?
        realms, credentials = endpoint.get_realms_and_credentials(
            **oauthlib_request(request))
        callback = request.GET.get('oauth_callback')

        form = OAuthAuthenticationForm(initial={
            'oauth_token': credentials['resource_owner_key'],
            'oauth_callback': callback,
        })

        return render(request, 'piston/authorize_token.html', {'form': form})

    elif request.method == "POST":
        response = oauthlib_response(
            endpoint.create_authorization_response(
                credentials={"user": request.user},
                **oauthlib_request(request)
            )
        )

        return response
