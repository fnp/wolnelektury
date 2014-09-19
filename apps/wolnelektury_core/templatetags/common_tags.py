# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from ssify import ssi_variable
from ssify.utils import ssi_vary_on_cookie

register = template.Library()


@ssi_variable(register, patch_response=[ssi_vary_on_cookie])
def user_username(request):
    return request.user.username


@ssi_variable(register, patch_response=[ssi_vary_on_cookie])
def user_is_staff(request):
    return request.user.is_staff
