from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('signup/',views.signup,name='signup'),
    path('track-played/', views.track_played, name='track_played'),
    path('playlists/', views.my_playlists, name='my_playlists'),
    path('playlist/create/', views.create_playlist, name='create_playlist'),
    path('playlist/<int:playlist_id>/', views.view_playlist, name='view_playlist'),
    path('playlist/<int:playlist_id>/delete/', views.delete_playlist, name='delete_playlist'),
    path('playlist/add/', views.add_to_playlist, name='add_to_playlist'),
    path('api/user-playlists/', views.user_playlists_api, name='user_playlists_api'),
    path("add-to-playlist/", views.add_to_playlist, name="add_to_playlist"),
    path("my-profile/", views.my_profile, name='my_profile')
]
