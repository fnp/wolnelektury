# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from rest_framework import serializers
from sorl.thumbnail import default
from django.core.urlresolvers import reverse
from club.models import Membership


class AbsoluteURLField(serializers.ReadOnlyField):
    def __init__(self, view_name=None, view_args=None, source='get_absolute_url', *args, **kwargs):
        if view_name is not None:
            source = '*'
        super(AbsoluteURLField, self).__init__(*args, source=source, **kwargs)
        self.view_name = view_name
        self.view_args = {}
        if view_args:
            for v in view_args:
                fields = v.split(':', 1)
                self.view_args[fields[0]] = fields[1] if len(fields)>1 else fields[0]

    def to_representation(self, value):
        if self.view_name is not None:
            kwargs = {
                arg: getattr(value, field)
                for (arg, field) in self.view_args.items()
            }
            value = reverse(self.view_name, kwargs=kwargs)
        return self.context['request'].build_absolute_uri(value)


class LegacyMixin(object):
    def to_representation(self, value):
        value = super(LegacyMixin, self).to_representation(value)
        non_null_fields = getattr(getattr(self, 'Meta', None), 'legacy_non_null_fields', [])
        for field in non_null_fields:
            if field in value and value[field] is None:
                value[field] = ''
        return value


class UserPremiumField(serializers.ReadOnlyField):
    def __init__(self, *args, **kwargs):
        super(UserPremiumField, self).__init__(*args, source='*', **kwargs)

    def to_representation(self, value):
        return Membership.is_active_for(value)


class ThumbnailField(serializers.FileField):
    def __init__(self, geometry, *args, **kwargs):
        self.geometry = geometry
        super(ThumbnailField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        if value:
            return super(ThumbnailField, self).to_representation(
                default.backend.get_thumbnail(value, self.geometry)
            )
