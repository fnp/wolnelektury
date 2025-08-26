from django.urls import path
from . import views


urlpatterns = [
    path('deviceTokens/', views.DeviceTokensView.as_view()),
    path('deviceTokens/<int:pk>/', views.DeviceTokenView.as_view(), name='push_api_device_token'),
]
