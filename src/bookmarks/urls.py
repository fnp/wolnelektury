from django.urls import path
from . import views


urlpatterns = [
    path('zakladki/', views.bookmarks, name='bookmarks'),
    path('zakladki/<uuid:uuid>/', views.bookmark, name='bookmark'),
    path('zakladki/<uuid:uuid>/delete/', views.bookmark_delete, name='bookmark_delete'),

    path('cytaty/', views.quotes, name='quotes'),
    path('cytaty/<uuid:uuid>/', views.quote, name='quote'),
]
