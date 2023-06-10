from django.urls import path
from . import views


urlpatterns = [
    path('mapa/', views.map),
    path('popup/<int:pk>', views.popup),
]
