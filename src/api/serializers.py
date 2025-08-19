# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.contrib.auth.models import User
from rest_framework import serializers
from .fields import UserPremiumField
from .models import BookUserData


class PlainSerializer(serializers.ModelSerializer):
    def to_representation(self, value):
        value = super(PlainSerializer, self).to_representation(value)
        return value.values()[0]


class UserSerializer(serializers.ModelSerializer):
    premium = UserPremiumField()
    confirmed = serializers.BooleanField(source='is_active')

    class Meta:
        model = User
        fields = ['username', 'premium', 'confirmed']


class BookUserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookUserData
        fields = ['state']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})



class RegisterSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    options = serializers.ListField(child=serializers.IntegerField(), required=False)


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(style={'input_type': 'password'})


class RequestConfirmSerializer(serializers.Serializer):
    email = serializers.CharField()


class DeleteAccountSerializer(serializers.Serializer):
    password =serializers.CharField(
        style={'input_type': 'password'}
    )

    def validate_password(self, value):
        u = self.context['user']
        if not u.check_password(value):
            raise serializers.ValidationError("Password incorrect.")
        return value


class PasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        u = self.context['user']
        if not u.check_password(value):
            raise serializers.ValidationError("Password incorrect.")
        return value
