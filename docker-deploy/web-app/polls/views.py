from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, VehicleForm, RideForm, PasswordForm, AccountEditForm, PassengerCountForm
from .models import UserProfile, Vehicle, Ride
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.forms import ChoiceField
from datetime import datetime
from project_1 import settings
from django.template.loader import render_to_string

import os.path
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

vehicle_capacity = {
    'CAR': 4,
    'CARXL': 6,
    'COMFORT': 4
}
def welcome_view(request):
  return render(request, 'welcome.html')

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        vehicle_form = VehicleForm(request.POST)
        if user_form.is_valid() and vehicle_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password1'])
            new_user.is_driver = True
            new_user.save()
            vehicle = vehicle_form.save(commit=False)
            vehicle.owner = new_user
            vehicle.save()
            return redirect('welcome')
    else:
        user_form = UserRegistrationForm()
        vehicle_form = VehicleForm()
    return render(request, 'register.html', {'user_form': user_form, 'vehicle_form': vehicle_form})

def register_rider(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password1'])
            new_user.save()
            return redirect('welcome')
    else:
        user_form = UserRegistrationForm()
    return render(request, 'register.html', {'user_form': user_form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
          login(request, user)
          return redirect('main_view')
        else:
          error_message = "Invalid username or password. Please try again."
          return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')

@login_required
def logout_view(request):
  logout(request)
  return redirect('welcome')

@login_required
def edit_account(request):
    user_profile = request.user
    is_driver = user_profile.is_driver
    if is_driver:
        vehicle_instance = user_profile.vehicle

    if request.method == 'POST':
        user_form = AccountEditForm(request.POST, instance=request.user)
        if is_driver:
            vehicle_form = VehicleForm(request.POST, instance=vehicle_instance)
        else:
            vehicle_form = None
        success = True
        if user_form.is_valid():
            user_form.save()
            #password_form.save()
            if vehicle_form != None:
                if vehicle_form.is_valid():
                    vehicle_form.save()
                else:
                    success = False
        else:
            success = False
        if success:
            messages.success(request, 'Your account has been updated successfully!')
            return redirect('edit_account')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = AccountEditForm(instance=request.user)
        if is_driver:
            vehicle_form = VehicleForm(instance=vehicle_instance)
        else:
            vehicle_form = None
    return render(request, 'edit_account.html', {'user_form': user_form, 'vehicle_form': vehicle_form})

@login_required
def driver_rider(request):
    user_profile = request.user
    vehicle = user_profile.vehicle
    vehicle.delete()
    user_profile.is_driver = False
    user_profile.save()
    messages.success(request, 'Your are no longer a driver!')
    return redirect('edit_account')

@login_required
def rider_driver(request):
    user_profile = request.user
    user_profile.is_driver = True
    user_profile.save()
    if request.method == 'POST':
        vehicle_form = VehicleForm(request.POST)
        if vehicle_form.is_valid():
            vehicle = vehicle_form.save(commit=False)
            vehicle.owner = user_profile
            vehicle.save()
            messages.success(request, 'You have been a driver successfully!')
            return redirect('edit_account')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        vehicle_form = VehicleForm()
    return render(request, 'rider_driver.html', {'vehicle_form': vehicle_form})

@login_required
def password_change(request):
    if request.method == 'POST':
        password_form = PasswordForm(request.user, request.POST)
        if password_form.is_valid():
            password_form.save()
            messages.success(request, 'Your password has been updated successfully!')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        password_form = PasswordForm(request.user)
    return render(request, 'password_change.html', {'password_form': password_form})

@login_required
def main_view(request):
    non_complete_rides = Ride.objects.filter(
        Q(owner=request.user) | Q(sharer__in=[request.user]),
        status__in=['requested', 'confirmed']).distinct()
    confirmed_rides = Ride.objects.filter(driver=request.user,status='confirmed').distinct()
    return render(request, 'main_view.html', {'non_complete_rides': non_complete_rides, 'confirmed_rides':confirmed_rides})

@login_required
def request_ride(request):

    if request.method == 'POST':
        ride_form = RideForm(request.POST)
        # if ride_form.is_valid():
        if is_valid_ride_form(request, ride_form):
            # start_time = ride_form.cleaned_data['start_time']
            # arrival_time = ride_form.cleaned_data['arrival_time']
            # if arrival_time < start_time:
            #     messages.error(request, "Arrival time cannot be earlier than start time.")
            #     return render(request, 'request_ride.html', {'ride_form': ride_form})

            new_ride = ride_form.save(commit=False)
            new_ride.owner = request.user
            new_ride.status = 'requested'
            new_ride.available_seats = vehicle_capacity[new_ride.vehicle_type]-new_ride.total_passengers
            new_ride.save()

            return redirect('main_view')
        else:
            return render(request, 'request_ride.html', {'ride_form': ride_form})
    else:
        ride_form = RideForm()
    return render(request, 'request_ride.html', {'ride_form': ride_form})

def is_valid_ride_form(request, ride_form):
    """
    Check if the ride form is valid, including the arrival time being later than or equal to the start time.
    """
    if not ride_form.is_valid():
        return False
    start_time = ride_form.cleaned_data['start_time']
    arrival_time = ride_form.cleaned_data['arrival_time']
    vehicle_type = ride_form.cleaned_data['vehicle_type']
    total_passengers = ride_form.cleaned_data['total_passengers']
    if arrival_time < start_time:
        messages.error(request, "Arrival time cannot be earlier than start time.")
        return False
    if vehicle_type=='CAR' and total_passengers>4:
        messages.error(request, "Vehicle type is Car and suitable for up to 4 passengers.")
        return False
    if vehicle_type=='CARXL' and total_passengers>6:
        messages.error(request, "Vehicle type is CarXL and suitable for up to 6 passengers.")
        return False
    if vehicle_type=='COMFORT' and total_passengers>4:
        messages.error(request, "Vehicle type is Comfort and suitable for up to 4 passengers.")
        return False
    return True

@login_required
def cancel_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)

    if request.method == 'POST':
        if ride.status == 'requested':
            # Check if the user is the owner of the ride
            if request.user == ride.owner:
                # Delete the ride if the user is the owner
                
                messages.success(request, 'Ride canceled successfully!')

                subject = "Ride Cancelled"
                from_email = "ridesharing52@gmail.com"
                to_emails = [ride.owner.email]
                for sharer in ride.sharer.all():
                    to_emails.append(sharer.email)

                context = {'ride': ride}
                html_message = render_to_string('ride_confirmation_email.html', context)

                service = gmail_authenticate()
                for to_email in to_emails:
                    send_message(service, from_email, to_email, subject, html_message)
                ride.delete()
                return redirect('main_view')
            elif request.user in ride.sharer.all():
                # Redirect to a page to input passenger count
                # ride.sharer.remove(request.user)
                # ride.save()
                return redirect('passenger_count', ride_id=ride_id)
            else:
                messages.error(request, 'You are not authorized to cancel this ride.')
                return redirect('main_view')

        messages.error(request, 'You cannot cancel a confirmed ride.')
        return redirect('main_view')
    else:
        ride_form = RideForm(instance=ride)

    return render(request, 'edit_ride.html', {'ride_form': ride_form})

@login_required
def passenger_count(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)

    if request.method == 'POST':
        form = PassengerCountForm(request.POST)
        if form.is_valid():
            passenger_count = form.cleaned_data['passenger_count']
            if passenger_count < ride.total_passengers:
                ride.sharer.remove(request.user)
                ride.total_passengers -= passenger_count
                ride.available_seats += passenger_count
                ride.save()
                messages.success(request, 'You have canceled your participation in this ride.')
                return redirect('main_view')
            else:
                messages.error(request, 'Passenger count exceeds the total passengers in the ride.')
    else:
        form = PassengerCountForm()

    return render(request, 'passenger_count.html', {'form': form})

@login_required
def view_ride_details(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    return render(request, 'ride_details.html', {'ride': ride})

@login_required
def edit_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)

    if request.method == 'POST':
        if ride.status == 'requested':
            # Check if the user is the owner of the ride
            if request.user == ride.owner:
                if not ride.sharer.all():
                    # Delete the ride if the user is the owner
                    ride_form = RideForm(request.POST, instance=ride)
                    if is_valid_ride_form(request, ride_form):
                        ride = ride_form.save(commit=False)
                        ride.available_seats = vehicle_capacity[ride.vehicle_type] - ride.total_passengers
                        ride.save()
                        messages.success(request, 'Ride updated successfully!')
                    else:
                        messages.error(request,'Failed to update ride. Please correct the errors.')
                else:
                    messages.error(request, "You can't edit this ride since there are other sharers.")
                return redirect('edit_ride',ride_id=ride_id)
            else:
                messages.error(request, 'You are not authorized to edit this ride.')
                return redirect('edit_ride',ride_id=ride_id)

        # If the ride is not in the "requested" status, proceed with editing
        # ride_form = RideForm(request.POST, instance=ride)
        # if ride_form.is_valid():
        #     ride_form.save()
        #     return redirect('main_view')
    else:
        ride_form = RideForm(instance=ride)

    return render(request, 'edit_ride.html', {'ride_form': ride_form})

@login_required
def request_share_ride(request):
    if request.method == 'POST':
        ride_form = RideForm(request.POST)
        if ride_form.is_valid():
            shared_rides = Ride.objects.filter(
                shared_ride=True,
                status='requested',
                start_location=request.POST.get('start_location'),
                end_location=request.POST.get('end_location'),
                vehicle_type=request.POST.get('vehicle_type'),
                arrival_time__gte=datetime.strptime(request.POST.get('start_time'), '%Y-%m-%dT%H:%M'),
                arrival_time__lte=datetime.strptime(request.POST.get('arrival_time'), '%Y-%m-%dT%H:%M'),
                available_seats__gte=int(request.POST.get('total_passengers'))
            ).exclude(owner=request.user)
            total_passengers=request.POST.get('total_passengers')
            return render(request, 'request_share_ride.html', {'ride_form': ride_form, 'shared_rides': shared_rides,'total_passengers': total_passengers})
    else:
        ride_form = RideForm(initial={'shared_ride': True})

    return render(request, 'request_share_ride.html', {'ride_form': ride_form})

@login_required
def join_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    if request.method == 'POST':
        if ride.status == 'requested':
            total_passengers = int(request.POST.get('total_passengers', 0))
            ride.sharer.add(request.user)
            ride.total_passengers += total_passengers
            ride.available_seats = vehicle_capacity[ride.vehicle_type] - ride.total_passengers
            ride.save()
            messages.success(request, 'You have successfully joined the ride.')
            return redirect('main_view')
    messages.error(request, 'Unable to join the ride.')
    return redirect('request_share_ride')

@login_required
def accept_ride(request):
    driver_vehicle_type = request.user.vehicle.vehicle_type
    driver_maxpassengers = request.user.vehicle.max_passengers
    rides = Ride.objects.filter(
        status='requested',
        vehicle_type=driver_vehicle_type,
        total_passengers__lte=driver_maxpassengers
    ).exclude(owner=request.user)
    return render(request, 'accept_ride.html', {'rides': rides})

@login_required
def confirm_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    ride.status = 'confirmed'
    ride.driver = request.user
    ride.vehicle_type = request.user.vehicle.vehicle_type

    ride.save()

    subject = "Ride Confirmation"
    from_email = "ridesharing52@gmail.com"
    to_emails = [ride.owner.email]
    for sharer in ride.sharer.all():
        to_emails.append(sharer.email)

    context = {'ride': ride}
    html_message = render_to_string('ride_confirmation_email.html', context)

    service = gmail_authenticate()
    for to_email in to_emails:
        send_message(service, from_email, to_email, subject, html_message)

    return redirect('main_view')

@login_required
def finish_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    ride.status = 'completed'
    ride.save()
    return redirect('main_view')

# Authentication and service creation
def gmail_authenticate():
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    # token.json stored user access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Authentication if no valid credentials are available
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This credentials.json is the credential you download from Google API portal when you
            # created the OAuth 2.0 Client IDs
            credential_dir = os.path.join(settings.BASE_DIR,'credentials.json')
            flow = InstalledAppFlow.from_client_secrets_file(
                credential_dir, SCOPES)
            # this is the redirect URI which should match your API setting, you can
            # find this setting in Credentials/Authorized redirect URIs at the API setting portal
            creds = flow.run_local_server(host="localhost", port=8080)
        # Save vouchers for later use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

# Create and send emails
def send_message(service, sender, to, subject, msg_html):
    message = MIMEMultipart('alternative')
    message['from'] = sender
    message['to'] = to
    message['subject'] = subject

    msg = MIMEText(msg_html, 'html')
    message.attach(msg)

    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}

    message = (service.users().messages().send(userId="me", body=body).execute())
    print(f"Message Id: {message['id']}")