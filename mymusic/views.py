import requests
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
# Create your views here.

def fetch_songs(query):
    url = f'https://saavn.dev/api/search/songs?query={query}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
            return json_data.get('data', {}).get('results', [])[:10]
    except Exception as e:
        print(query,e)
        pass
    return []


@login_required
def home(request):
    songs = Song.objects.all()
    search_query = request.GET.get('query', '')

    hindi_tracks = fetch_songs('hindi')
    punjabi_tracks = fetch_songs('punjabi')
    rajasthani_tracks = fetch_songs('rajasthani flok')
    gujarati_tracks = fetch_songs('gujarati')
    haryanvi_tracks = fetch_songs('haryanvi')
    search_results = []
    if search_query:
        search_results = fetch_songs(search_query)
    recent_tracks = request.session.get('recent_tracks', [])
    return render(request, 'home.html', {
        'songs':songs,
        'hindi_tracks': hindi_tracks,
        'punjabi_tracks': punjabi_tracks,
        'gujarati_tracks': gujarati_tracks,
        'rajasthani_tracks': rajasthani_tracks,
        'haryanvi_tracks':haryanvi_tracks,
        'search_results': search_results,
        'search_query': search_query,
        'recent_tracks': recent_tracks,
        'show_logout': True
    })

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(forms.cleaned_data['password1'])
            user.save()
            Profile.objects.create(
                user=user,
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                gender=form.cleaned_data['gender'],
                age=form.cleaned_data['age']
            )
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'registration/singup.html', {'form': form})

@login_required
def my_profile(request):
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        print('Note exist')
        profile = None
    context = {
        'phone': profile.phone if profile else'',
        'username': user.username if profile else'',
        'email': user.email if profile else'',
        'profile_image':profile.profile_image if profile and profile.profile_image else''
    }
    return render(request, 'profile.html', context)
    

@login_required
def user_playlists_api(request):
    print('it work')
    playlists = Playlist.objects.filter(user=request.user)
    data = [{"id": p.id, "name": p.name} for p in playlists]
    return JsonResponse({"playlists": data})

@login_required
def my_playlists(request):
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'playlists.html', {
        'playlists': playlists,
        'show_create_playlist': True
        })


@login_required
def create_playlist(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Playlist.objects.create(user=request.user, name=name)
            return redirect('my_playlists')
    return render(request, 'create_playlist.html')

@login_required
def delete_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    if request.method == 'POST':
        playlist.delete()
        return redirect('my_playlists')
    return redirect('view_playlist', playlist_id=playlist_id)

    
@login_required
def view_playlist(request, playlist_id):
    playlist = Playlist.objects.get(id=playlist_id, user=request.user)
    return render(request, 'view_playlist.html', {
        'playlist': playlist,
        'show_create_playlist': True
        })


@login_required
def add_to_playlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            playlist_id = data.get('playlist_id')
            title = data.get('title')
            artist = data.get('artist')
            image = data.get('image')
            audio_url = data.get('audio')

            playlist = Playlist.objects.get(id=playlist_id, user=request.user)

            PlaylistSong.objects.create(
                playlist=playlist,
                title=title,
                artist=artist,
                image=image,
                audio_url=audio_url
            )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def track_played(request):
    if request.method == "POST":
        data = json.loads(request.body)
        recent_tracks = request.session.get('recent_tracks', [])

        # Avoid duplicate
        if data not in recent_tracks:
            recent_tracks.insert(0, data)

        # Keep only last 5
        recent_tracks = recent_tracks[:10]

        request.session['recent_tracks'] = recent_tracks
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'invalid'}, status=400)
