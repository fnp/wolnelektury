from django.contrib.auth.models import User
from rest_framework import serializers
from .fields import UserPremiumField
from .models import BookUserData


class UserSerializer(serializers.ModelSerializer):
    premium = UserPremiumField()

    class Meta:
        model = User
        fields = ['username', 'premium']


class BookUserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookUserData
        fields = ['state']
