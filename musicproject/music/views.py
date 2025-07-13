import requests
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth import logout
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from .models import Profile
from django.contrib.auth import authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

# Create your views here.

def safe_fetch(query):
    try:
        print(f"🔍 Fetching: {query}")
        return fetch_jiosaavn_songs(query)
    except Exception as e:
        print(f"⚠️ Error fetching '{query}': {e}")
        return []

@login_required
def user_playlists_api(request):
    playlists = Playlist.objects.filter(user=request.user)
    data = [{"id": p.id, "name": p.name} for p in playlists]
    return JsonResponse({"playlists": data})

@login_required
def my_playlists(request):
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'music/playlists.html', {
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
    return render(request, 'music/create_playlist.html')


    
@login_required
def view_playlist(request, playlist_id):
    playlist = Playlist.objects.get(id=playlist_id, user=request.user)
    return render(request, 'music/view_playlist.html', {
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
            print("Error:", e)
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
        recent_tracks = recent_tracks[:5]

        request.session['recent_tracks'] = recent_tracks
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'invalid'}, status=400)


def fetch_jiosaavn_songs(query):
    url = f'https://saavn.dev/api/search/songs?query={query}'
    print("🔍 Fetching from:", url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
            return json_data.get('data', {}).get('results', [])[:10]
    except Exception as e:
        pass
    return []

@login_required
def home(request):
    songs = Song.objects.all()
    search_query = request.GET.get('query', '')

    # JioSaavn song sections
    hindi_tracks = fetch_jiosaavn_songs("hindi")
    punjabi_tracks = fetch_jiosaavn_songs("punjabi")
    gujarati_tracks = fetch_jiosaavn_songs("gujarati")
    rajasthani_tracks = fetch_jiosaavn_songs("rajasthani folk")

    search_results = []
    if search_query:
        search_results = fetch_jiosaavn_songs(search_query)
    recent_tracks = request.session.get('recent_tracks', [])

    return render(request, 'music/home.html', {
        'songs': songs,
        'hindi_tracks': hindi_tracks,
        'punjabi_tracks': punjabi_tracks,
        'gujarati_tracks': gujarati_tracks,
        'rajasthani_tracks': rajasthani_tracks,
        'search_results': search_results,
        'search_query': search_query,
        'recent_tracks': recent_tracks,
        'show_logout': True
    })


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save User
            user = form.save(commit=False)
            raw_password = form.cleaned_data['password']
            user.set_password(raw_password)
            user.is_staff = False
            user.save()

            # Save Profile
            phone = form.cleaned_data.get('phone')
            gender = form.cleaned_data.get('gender')
            age = form.cleaned_data.get('age')

            # Important: Create profile with user relation
            Profile.objects.create(
                user=user,
                phone=phone,
                gender=gender,
                age=age
            )

            # Login and Redirect
            login(request, user)
            return redirect('home')  # <== Make sure 'home' is defined in your urls.py
        else:
            messages.error(request, "Form is invalid. Please check your inputs.")
    else:
        form = SignUpForm()

    return render(request, 'music/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # your home page view name
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'music/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')