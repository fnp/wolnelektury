from django.urls import path
from . import views


urlpatterns = [
    path('states/<slug>/info.json', views.state_info),
    path('opt-out/<key>/', views.OptOutView.as_view(), name='messaging_optout'),
]
