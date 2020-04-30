from django.urls import path
from . import views
from stats.utils import piwik_track_view

urlpatterns = [
    path('<slug:slug>/', piwik_track_view(views.WLRedirectView.as_view()), name='redirect'),
]
