from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class City(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

class Location(models.Model):
    TYPE_CHOICES = [
        ('museum', 'Museum'),
        ('restaurant', 'Restaurant'),
        ('market', 'Market'),
        ('park', 'Park'),
    ]

    city = models.ForeignKey('City', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    schedule = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    location_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    rating = models.FloatField(default=0)
    reviews_count = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class LocationImage(models.Model):
    location = models.ForeignKey(Location, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='location_images/')

class Review(models.Model):
    location = models.ForeignKey(Location, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class SavedItinerary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_itineraries')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    locations = models.ManyToManyField('Location')

    def __str__(self):
        return f"Itinerary - {self.name} ({self.user.username})"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    friends = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not instance.is_superuser and not instance.is_staff:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


