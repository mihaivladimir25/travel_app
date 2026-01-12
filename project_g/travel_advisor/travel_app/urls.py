from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('city/<str:city_name>/', views.city_page, name='city_page'),
    path('generate-itinerary/', views.generate_itinerary, name='generate_itinerary'),
    path('approve-location/<int:location_id>/', views.approve_location, name='approve_location'),
    path('location/<int:location_id>/', views.location_detail, name='location_detail'),
    path('location/<int:location_id>/add_review/', views.add_review, name='add_review'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('save-itinerary/', views.save_itinerary, name='save_itinerary'),
    path('add-friend/<int:user_id>/', views.add_friend, name='add_friend'),
    path('itinerary/<int:itinerary_id>/', views.itinerary_detail, name='itinerary_detail'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path("api/search-locations/", views.search_locations, name='search_locations'),
    path("api/", views.api_playground, name="api_playground"),
]
