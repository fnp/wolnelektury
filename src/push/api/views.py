from rest_framework import serializers
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from api.utils import never_cache
from api.fields import AbsoluteURLField
from push import models


class DeviceTokenSerializer(serializers.ModelSerializer):
    href = AbsoluteURLField(
        view_name='push_api_device_token',
        view_args=('pk',)
    )

    class Meta:
        model = models.DeviceToken
        fields = ['token', 'created_at', 'updated_at', 'href']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        return models.DeviceToken.objects.create(
            user=self.context['request'].user,
            **validated_data
        )


@never_cache
class DeviceTokensView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeviceTokenSerializer

    def get_queryset(self):
        return models.DeviceToken.objects.filter(user=self.request.user)


@never_cache
class DeviceTokenView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeviceTokenSerializer

    def get_queryset(self):
        return models.DeviceToken.objects.filter(user=self.request.user)
