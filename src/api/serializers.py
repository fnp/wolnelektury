# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.auth.models import User
from rest_framework import serializers
from .fields import UserPremiumField, AbsoluteURLField, ThumbnailField
from .models import BookUserData


class PlainSerializer(serializers.ModelSerializer):
    def to_representation(self, value):
        value = super(PlainSerializer, self).to_representation(value)
        return value.values()[0]


class UserSerializer(serializers.ModelSerializer):
    premium = UserPremiumField()

    class Meta:
        model = User
        fields = ['username', 'premium']


class BookUserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookUserData
        fields = ['state']
