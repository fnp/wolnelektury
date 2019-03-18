from rest_framework.permissions import BasePermission
from .models import Membership


class IsClubMember(BasePermission):
    def has_permission(self, request, view):
        return Membership.is_active_for(request.user)
