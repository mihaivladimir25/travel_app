import json
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .models import *
from django.contrib import messages
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.shortcuts import redirect
from .forms import *
from elasticsearch import Elasticsearch
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

ORS_API_KEY = '5b3ce3597851110001cf624883fa224470104f559740f3027dce1307'

es = Elasticsearch("http://localhost:9200")

def home(request):
    cities = ['London', 'Paris', 'Rome', 'Berlin', 'Amsterdam', 'Madrid']
    return render(request, 'home.html', {'cities': cities})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contul a fost creat cu succes! Te poți autentifica acum.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def city_page(request, city_name):
    city = get_object_or_404(City, name__iexact=city_name.strip())
    locations = Location.objects.filter(city=city, is_approved=True)
    return render(request, 'city_page.html', {'city': city, 'locations': locations})

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'locations': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER)
            )
        },
        required=['locations']
    ),
    responses={200: openapi.Response("Generated itinerary")}
)
@api_view(['POST'])
def generate_itinerary(request):
    selected_ids = request.data.get('locations', [])
    locations = Location.objects.filter(id__in=selected_ids)

    if locations.count() < 2:
        return Response({"error": "Select at least 2 locations"}, status=400)

    coordinates = [[loc.longitude, loc.latitude] for loc in locations]

    ors_url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    res = requests.post(ors_url, headers=headers, json={"coordinates": coordinates}).json()

    feature = res["features"][0]
    distance = feature["properties"]["summary"]["distance"] / 1000
    duration = feature["properties"]["summary"]["duration"] / 60

    return Response({
        "geometry": feature["geometry"],
        "distance": round(distance, 2),
        "duration": round(duration, 2),
        "itinerary": " ➔ ".join([loc.name for loc in locations])
    })

@staff_member_required
def approve_location(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    location.is_approved = True
    location.save()
    return redirect('admin:index')


def location_detail(request, location_id):
    location = get_object_or_404(Location, id=location_id, is_approved=True)
    images = location.images.all()
    reviews = location.reviews.all()
    return render(request, 'location_detail.html', {
        'location': location,
        'images': images,
        'reviews': reviews
    })

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

@login_required
def add_review(request, location_id):
    location = get_object_or_404(Location, id=location_id)

    if request.method == 'POST':
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')
        sentiment_score = sia.polarity_scores(comment)['compound']
        calculated_rating = 5 if sentiment_score > 0.5 else 4 if sentiment_score > 0.2 else 3 if sentiment_score > 0 else 2 if sentiment_score > -0.2 else 1
        Review.objects.create(
            location=location,
            user=request.user,
            rating=calculated_rating,
            comment=comment
        )

        reviews = location.reviews.all()
        average_rating = sum([rev.rating for rev in reviews]) / reviews.count()
        location.rating = round(average_rating, 2)
        location.reviews_count = reviews.count()
        location.save()

        return redirect('location_detail', location_id=location.id)

    return redirect('location_detail', location_id=location.id)


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import UserProfile


def profile_view(request, username):
    user = get_object_or_404(User, username=username)

    if user.is_superuser or user.is_staff:
        return redirect('/admin/')

    user_profile = get_object_or_404(UserProfile, user=user)
    itineraries = user_profile.user.saved_itineraries.all()

    return render(request, 'profile.html', {
        'profile': user_profile,
        'itineraries': itineraries
    })

@login_required
def save_itinerary(request):
    if request.method == "POST":
        selected_ids = request.POST.getlist('locations')
        locations = Location.objects.filter(id__in=selected_ids)
        itinerary_name = request.POST.get('itinerary_name')

        itinerary = SavedItinerary.objects.create(user=request.user, name=itinerary_name)
        itinerary.locations.set(locations)
        itinerary.save()

        return redirect('profile', username=request.user.username)
    return redirect('home')

@login_required
def add_friend(request, user_id):
    user_to_add = get_object_or_404(UserProfile, id=user_id)
    profile = request.user.userprofile
    profile.friends.add(user_to_add)
    return redirect('profile', username=user_to_add.user.username)


def custom_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            UserProfile.objects.get_or_create(user=user)
            return redirect('profile', username=user.username)
        else:
            messages.error(request, "Date de autentificare incorecte.")
    return render(request, 'login.html')


def itinerary_detail(request, itinerary_id):
    itinerary = get_object_or_404(SavedItinerary, id=itinerary_id)
    return render(request, 'itinerary_detail.html', {'itinerary': itinerary})


@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        user_form = EditProfileForm(request.POST, instance=user)
        profile_form = EditUserProfileForm(request.POST, request.FILES, instance=user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profilul a fost actualizat cu succes!')
            return redirect('profile', username=user.username)
    else:
        user_form = EditProfileForm(instance=user)
        profile_form = EditUserProfileForm(instance=user.userprofile)

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Parola a fost schimbată cu succes!')
            return redirect('profile', username=request.user.username)
        else:
            messages.error(request, 'Te rugam să corectezi erorile.')
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'change_password.html', {'form': form})


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('q', openapi.IN_QUERY, description="Search term", type=openapi.TYPE_STRING)
    ],
    responses={200: openapi.Response("List of locations")}
)
@api_view(['GET'])
def search_locations(request):
    q = request.GET.get("q", "")

    results = Location.objects.filter(name__icontains=q)

    data = [{
        "id": loc.id,
        "name": loc.name,
        "city": loc.city.name,
        "type": loc.location_type
    } for loc in results]

    return Response(data)