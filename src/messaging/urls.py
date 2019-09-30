from django.urls import path
from . import views


urlpatterns = [
    path('states/<slug>/info.json', views.state_info),
]
