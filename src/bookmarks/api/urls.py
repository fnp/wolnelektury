from django.urls import path
from . import views


urlpatterns = [
    path('bookmarks/', views.BookmarksView.as_view()),
    path('bookmarks/book/<slug:book>/', views.BookBookmarksView.as_view()),
    path('bookmarks/<uuid:uuid>/', views.BookmarkView.as_view(), name='api_bookmark'),
]
