from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User

class UserProfile(AbstractUser):
    is_driver = models.BooleanField(default=False)
# class UserProfile(models.Model):
#   user = models.OneToOneField(User, on_delete=models.CASCADE)
#   is_driver = models.BooleanField(default=False)

class Vehicle(models.Model):
    owner = models.OneToOneField(UserProfile, on_delete=models.CASCADE,related_name='vehicle')
    VEHICLE_TYPE_CHOICES = [
        ('CAR', 'Car'),
        ('CARXL', 'CarXL'),
        ('COMFORT', 'Comfort'),
    ]
    vehicle_type = models.CharField(max_length=100, choices=VEHICLE_TYPE_CHOICES)
    license_plate = models.CharField(max_length=20)
    max_passengers = models.PositiveIntegerField()
    special_info = models.TextField(blank=True)

class Ride(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='rides_owned')
    driver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='rides_driven',null=True)
    sharer = models.ManyToManyField(UserProfile, related_name='rides_shared', blank=True)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="requested")
    shared_ride = models.BooleanField(default=False)
    total_passengers = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField(default=0)
    VEHICLE_TYPE_CHOICES = [
        ('CAR', 'Car'),
        ('CARXL', 'CarXL'),
        ('COMFORT', 'Comfort'),
    ]
    vehicle_type = models.CharField(max_length=100, choices=VEHICLE_TYPE_CHOICES)
    start_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    special_info = models.TextField(blank=True)