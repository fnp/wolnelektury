from rest_framework.permissions import BasePermission
from .rest import user_is_subscribed


class IsSubscribed(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and user_is_subscribed(request.user)
