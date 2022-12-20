from django.urls import path
from django.views.generic import DetailView
from . import models


urlpatterns = [
    path('<slug:slug>/', DetailView.as_view(model=models.Course)),
]
