# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from time import time
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django import forms
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render
from django.views.generic.base import View
from oauthlib.common import urlencode, generate_token
from oauthlib.oauth1 import RequestTokenEndpoint, AccessTokenEndpoint
from oauthlib.oauth1 import AuthorizationEndpoint, OAuth1Error
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, RetrieveAPIView, get_object_or_404
from catalogue.models import Book
from .models import BookUserData, KEY_SIZE, SECRET_SIZE, Token
from . import serializers
from .request_validator import PistonRequestValidator
from .utils import oauthlib_request, oauthlib_response, vary_on_auth


class OAuth1RequestTokenEndpoint(RequestTokenEndpoint):
    def _create_request(self, *args, **kwargs):
        r = super(OAuth1RequestTokenEndpoint, self)._create_request(*args, **kwargs)
        r.redirect_uri = 'oob'
        return r

    def create_request_token(self, request, credentials):
        token = {
            'oauth_token': self.token_generator()[:KEY_SIZE],
            'oauth_token_secret': self.token_generator()[:SECRET_SIZE],
        }
        token.update(credentials)
        self.request_validator.save_request_token(token, request)
        return urlencode(token.items())


# Never Cache
class OAuth1RequestTokenView(View):
    def __init__(self):
        self.endpoint = OAuth1RequestTokenEndpoint(PistonRequestValidator())

    def dispatch(self, request):
        return oauthlib_response(
            self.endpoint.create_request_token_response(
                **oauthlib_request(request)
            )
        )


class OAuthAuthenticationForm(forms.Form):
    oauth_token = forms.CharField(widget=forms.HiddenInput)
    oauth_callback = forms.CharField(widget=forms.HiddenInput)  # changed from URLField - too strict
    # removed authorize_access - redundant


class OAuth1AuthorizationEndpoint(AuthorizationEndpoint):
    def create_verifier(self, request, credentials):
        verifier = super(OAuth1AuthorizationEndpoint, self).create_verifier(request, credentials)
        return {
            'oauth_token': verifier['oauth_token'],
        }


@login_required
def oauth_user_auth(request):
    endpoint = OAuth1AuthorizationEndpoint(PistonRequestValidator())

    if request.method == "GET":
        # Why not just get oauth_token here?
        # This is fairly straightforward, in't?
        try:
            realms, credentials = endpoint.get_realms_and_credentials(
                **oauthlib_request(request))
        except OAuth1Error as e:
            return HttpResponse(str(e), status=400)
        callback = request.GET.get('oauth_callback')

        form = OAuthAuthenticationForm(initial={
            'oauth_token': credentials['resource_owner_key'],
            'oauth_callback': callback,
        })

        return render(request, 'oauth/authorize_token.html', {'form': form})

    if request.method == "POST":
        try:
            response = oauthlib_response(
                endpoint.create_authorization_response(
                    credentials={"user": request.user},
                    **oauthlib_request(request)
                )
            )
        except OAuth1Error as e:
            return HttpResponse(e.message, status=400)
        else:
            return response


class OAuth1AccessTokenEndpoint(AccessTokenEndpoint):
    def _create_request(self, *args, **kwargs):
        r = super(OAuth1AccessTokenEndpoint, self)._create_request(*args, **kwargs)
        r.verifier = 'x' * 20
        return r

    def create_access_token(self, request, credentials):
        request.realms = self.request_validator.get_realms(
            request.resource_owner_key, request)
        token = {
            'oauth_token': self.token_generator()[:KEY_SIZE],
            'oauth_token_secret': self.token_generator()[:SECRET_SIZE],
            'oauth_authorized_realms': ' '.join(request.realms)
        }
        token.update(credentials)
        self.request_validator.save_access_token(token, request)
        return urlencode(token.items())


# Never cache
class OAuth1AccessTokenView(View):
    def __init__(self):
        self.endpoint = OAuth1AccessTokenEndpoint(PistonRequestValidator())

    def dispatch(self, request):
        return oauthlib_response(
            self.endpoint.create_access_token_response(
                **oauthlib_request(request)
            )
        )


class LoginView(GenericAPIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        user = authenticate(username=d['username'], password=d['password'])
        if user is None:
            return Response({"detail": "Invalid credentials."})

        key = generate_token()[:KEY_SIZE]
        Token.objects.create(
            key=key,
            token_type=Token.ACCESS,
            timestamp=time(),
            user=user,
        )
        return Response({"access_token": key})


@vary_on_auth
class UserView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user


@vary_on_auth
class BookUserDataView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.BookUserDataSerializer
    lookup_field = 'book__slug'
    lookup_url_kwarg = 'slug'

    def get_queryset(self):
        return BookUserData.objects.filter(user=self.request.user)

    def get(self, *args, **kwargs):
        try:
            return super(BookUserDataView, self).get(*args, **kwargs)
        except Http404:
            return Response({"state": "not_started"})

    def post(self, request, slug, state):
        if state not in ('reading', 'complete'):
            raise Http404

        book = get_object_or_404(Book, slug=slug)
        instance = BookUserData.update(book, request.user, state)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class BlogView(APIView):
    def get(self, request):
        return Response([])
