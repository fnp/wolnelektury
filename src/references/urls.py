from django.urls import path, re_path
from . import views


urlpatterns = [
    path('mapa/', views.pin_map),
    re_path(r'^mapa/(?P<tags>[a-zA-Z0-9-/]*)/$', views.pin_map_tagged),
    path('popup/<int:pk>', views.popup),
]
