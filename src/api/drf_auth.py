# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from oauthlib.oauth1 import ResourceEndpoint
from rest_framework.authentication import BaseAuthentication, TokenAuthentication
from .request_validator import PistonRequestValidator
from .utils import oauthlib_request
from .models import Token


class PistonOAuthAuthentication(BaseAuthentication):
    def __init__(self):
        validator = PistonRequestValidator()
        self.provider = ResourceEndpoint(validator)

    def authenticate_header(self, request):
        return 'OAuth realm="API"'

    def authenticate(self, request):
        v, r = self.provider.validate_protected_resource_request(
            **oauthlib_request(request)
        )
        if v:
            return r.token.user, r.token


class WLTokenAuthentication(TokenAuthentication):
    model = Token
