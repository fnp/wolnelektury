from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.pin_map),
    path('popup/<int:pk>', views.popup),
    re_path(r'^(?P<tags>[a-zA-Z0-9-/]*)/$', views.pin_map_tagged),
]
