from rest_framework import serializers
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from api.utils import never_cache
from api.fields import AbsoluteURLField
from push import models


class DeviceTokenSerializer(serializers.ModelSerializer):
    deleted = serializers.BooleanField(default=False, write_only=True)
    # Explicit definition to disable unique validator.
    token = serializers.CharField()

    class Meta:
        model = models.DeviceToken
        fields = ['token', 'created_at', 'updated_at', 'deleted']
        read_only_fields = ['created_at', 'updated_at']

    def save(self):
        if self.validated_data['deleted']:
            self.destroy(self.validated_data)
        else:
            return self.create(self.validated_data)

    def create(self, validated_data):
        obj, created = models.DeviceToken.objects.get_or_create(
            user=self.context['request'].user,
            token=validated_data['token'],
        )
        return obj

    def destroy(self, validated_data):
        models.DeviceToken.objects.filter(
            user=self.context['request'].user,
            token=validated_data['token']
        ).delete()

@never_cache
class DeviceTokensView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeviceTokenSerializer

    def get_queryset(self):
        return models.DeviceToken.objects.filter(user=self.request.user)
