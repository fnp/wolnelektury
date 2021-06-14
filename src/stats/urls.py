from django.urls import path
from . import views


urlpatterns = [
    path('top/', views.TopView.as_view(), name='stats_top'),
    path('top/daily/', views.DailyTopView.as_view(), name='stats_top'),
]
