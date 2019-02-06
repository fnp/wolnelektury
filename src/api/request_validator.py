# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from oauthlib.oauth1 import RequestValidator
from piston.models import Consumer, Nonce, Token


class PistonRequestValidator(RequestValidator):
    dummy_access_token = '!'
    realms = ['API']

    # Just for the tests.
    # It'd be a little more kosher to use test client with secure=True.
    enforce_ssl = False

    # iOS app generates 8-char nonces.
    nonce_length = 8, 250

    # Because piston.models.Token.key is char(18).
    access_token_length = 18, 32

    def check_client_key(self, client_key):
        """We control the keys anyway."""
        return True

    def get_access_token_secret(self, client_key, token, request):
        return request.token.secret

    def get_default_realms(self, client_key, request):
        return ['API']

    def validate_access_token(self, client_key, token, request):
        try:
            token = Token.objects.get(
                token_type=Token.ACCESS,
                consumer__key=client_key,
                key=token
            )
        except Token.DoesNotExist:
            return False
        else:
            request.token = token
            return True

    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce,
                                     request, request_token=None, access_token=None):
        # TODO: validate the timestamp
        token = request_token or access_token
        # Yes, this is what Piston did.
        if token is None:
            return True

        nonce, created = Nonce.objects.get_or_create(consumer_key=client_key,
                                                     token_key=token,
                                                     key=nonce)
        return created

    def validate_client_key(self, client_key, request):
        try:
            request.oauth_consumer = Consumer.objects.get(key=client_key)
        except Consumer.DoesNotExist:
            return False
        return True

    def validate_realms(self, client_key, token, request, uri=None, realms=None):
        return True

    def validate_requested_realms(self, *args, **kwargs):
        return True

    def validate_redirect_uri(self, *args, **kwargs):
        return True

    def get_client_secret(self, client_key, request):
        return request.oauth_consumer.secret

    def save_request_token(self, token, request):
        Token.objects.create(
            token_type=Token.REQUEST,
            timestamp=request.timestamp,
            key=token['oauth_token'],
            secret=token['oauth_token_secret'],
            consumer=request.oauth_consumer,
        )
