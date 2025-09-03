from django.urls import path
from . import views


urlpatterns = [
    path('deviceTokens/', views.DeviceTokensView.as_view()),
]
