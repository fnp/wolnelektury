"""
Transitional code: bridge between Piston's OAuth implementation
and DRF views.
"""
from piston.authentication import OAuthAuthentication
from rest_framework.authentication import BaseAuthentication


class PistonOAuthAuthentication(BaseAuthentication):
    def __init__(self):
        self.piston_auth = OAuthAuthentication()

    def authenticate_header(self, request):
        return 'OAuth realm="API"'

    def authenticate(self, request):
        if self.piston_auth.is_valid_request(request):
            consumer, token, parameters = self.piston_auth.validate_token(request)
            if consumer and token:
                return token.user, token
