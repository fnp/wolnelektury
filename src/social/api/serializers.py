# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from rest_framework import serializers
import catalogue.models
from social import models


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = ['notifications']


class UserListBooksField(serializers.Field):
    def to_representation(self, value):
        return list(value.userlistitem_set.exclude(deleted=True).exclude(book=None).values_list('book__slug', flat=True))

    def to_internal_value(self, value):
        return {'books': catalogue.models.Book.objects.filter(slug__in=value)}


class UserListSerializerV2(serializers.ModelSerializer):
    client_id = serializers.CharField(write_only=True, required=False)
    books = UserListBooksField(source='*', required=False)
    timestamp = serializers.IntegerField(required=False)

    class Meta:
        model = models.UserList
        fields = [
            'timestamp',
            'client_id',
            'name',
            'slug',
            'favorites',
            'deleted',
            'books',
        ]
        read_only_fields = [
            'favorites',
            'slug',
        ]
        extra_kwargs = {
            'slug': {
                'required': False
            }
        }

    def create(self, validated_data):
        instance = models.UserList.get_by_name(
            validated_data['user'],
            validated_data['name'],
            create=True
        )
        if 'books' in validated_data:
            instance.userlistitem_set.all().delete()
            for book in validated_data['books']:
                instance.append(book)
        return instance

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        if 'books' in validated_data:
            instance.userlistitem_set.all().delete()
            for book in validated_data['books']:
                instance.append(instance)
        return instance


class UserListBooksSerializer(UserListSerializerV2):
    class Meta:
        model = models.UserList
        fields = ['books']


class UserListItemSerializer(serializers.ModelSerializer):
    client_id = serializers.CharField(write_only=True, required=False)
    favorites = serializers.BooleanField(read_only=True)
    list_slug = serializers.SlugRelatedField(
        queryset=models.UserList.objects.all(),
        source='list',
        slug_field='slug',
        required=False,
    )
    timestamp = serializers.IntegerField(required=False)
    book_slug = serializers.SlugRelatedField(
        queryset=catalogue.models.Book.objects.all(),
        source='book',
        slug_field='slug',
        required=False
    )

    class Meta:
        model = models.UserListItem
        fields = [
            'client_id',
            'uuid',
            'order',
            'list_slug',
            'timestamp',
            'favorites',
            'deleted',

            'book_slug',
            'fragment',
            'quote',
            'bookmark',
            'note',
        ]
        extra_kwargs = {
            'order': {
                'required': False
            }
        }


class UserListSerializerV3(serializers.ModelSerializer):
    client_id = serializers.CharField(write_only=True, required=False)
    timestamp = serializers.IntegerField(required=False)

    class Meta:
        model = models.UserList
        fields = [
            'timestamp',
            'client_id',
            'name',
            'slug',
            'favorites',
            'deleted',
        ]
        read_only_fields = [
            'favorites',
            'slug',
        ]
        extra_kwargs = {
            'slug': {
                'required': False
            }
        }

    def create(self, validated_data):
        instance = models.UserList.get_by_name(
            validated_data['user'],
            validated_data['name'],
            create=True
        )
        return instance


class ProgressSerializer(serializers.ModelSerializer):
    book = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='catalogue_api_book',
        lookup_field='slug'
    )
    book_slug = serializers.SlugRelatedField(
        queryset=catalogue.models.Book.objects.all(),
        source='book',
        slug_field='slug')
    timestamp = serializers.IntegerField(required=False)

    class Meta:
        model = models.Progress
        fields = [
            'timestamp',
            'book', 'book_slug', 'last_mode', 'text_percent',
            'text_anchor',
            'audio_percent',
            'audio_timestamp',
            'implicit_text_percent',
            'implicit_text_anchor',
            'implicit_audio_percent',
            'implicit_audio_timestamp',
        ]
        extra_kwargs = {
            'last_mode': {
                'required': False,
                'default': 'text',
            }
        }


class TextProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Progress
        fields = [
                'text_percent',
                'text_anchor',
                ]
        read_only_fields = ['text_percent']

class AudioProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Progress
        fields = ['audio_percent', 'audio_timestamp']
        read_only_fields = ['audio_percent']
