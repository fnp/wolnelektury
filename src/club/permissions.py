# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from rest_framework.permissions import BasePermission
from .models import Membership


class IsClubMember(BasePermission):
    def has_permission(self, request, view):
        return Membership.is_active_for(request.user)
