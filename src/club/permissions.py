# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from rest_framework.permissions import BasePermission
from .models import Membership


class IsClubMember(BasePermission):
    def has_permission(self, request, view):
        return Membership.is_active_for(request.user)
