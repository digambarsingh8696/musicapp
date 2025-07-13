from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('', auth_views.LoginView.as_view(template_name='music/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('track-played/', views.track_played, name='track_played'),
    path('playlists/', views.my_playlists, name='my_playlists'),
    path('playlist/create/', views.create_playlist, name='create_playlist'),
    path('playlist/<int:playlist_id>/', views.view_playlist, name='view_playlist'),
    path('playlist/add/', views.add_to_playlist, name='add_to_playlist'),
    path("api/user-playlists/", views.user_playlists_api, name="user_playlists_api"),
    path("add-to-playlist/", views.add_to_playlist, name="add_to_playlist"),
]