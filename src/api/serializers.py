# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.auth.models import User
from rest_framework import serializers
from .fields import UserPremiumField, AbsoluteURLField, ThumbnailField
from .models import BookUserData
from migdal.models import Entry, Photo


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


class BlogGalleryUrlSerializer(PlainSerializer):
    class Meta:
        model = Photo
        fields = ['image']


class BlogSerializer(serializers.ModelSerializer):
    url = AbsoluteURLField()
    image_url = serializers.FileField(source='image')
    image_thumb = ThumbnailField('193x193', source='image')
    key = serializers.DateTimeField(source='first_published_at')
    gallery_urls = BlogGalleryUrlSerializer(many=True, source='photo_set')
    body = serializers.CharField()
    lead = serializers.CharField()

    class Meta:
        model = Entry
        fields = ['title', 'lead', 'body', 'place', 'time', 'image_url', 'image_thumb',
                  'gallery_urls', 'type', 'key', 'url']
