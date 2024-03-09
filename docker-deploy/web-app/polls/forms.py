from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Vehicle, Ride
class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'email','first_name', 'last_name','password1', 'password2']

class AccountEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'email','first_name', 'last_name']

class PasswordForm(PasswordChangeForm):
    class Meta:
        model = UserProfile
        fields = ['password']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['is_driver']

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_type', 'license_plate', 'max_passengers', 'special_info']

class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['start_location', 'end_location', 'shared_ride',
                  'total_passengers', 'vehicle_type', 'start_time','arrival_time', 'special_info']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

class PassengerCountForm(forms.Form):
    passenger_count = forms.IntegerField(min_value=1, label='Number of Passengers')
