from django.urls import path

from . import views

urlpatterns = [
    path('', views.welcome_view, name="welcome"),
    path('create_account/', views.register, name='create_account'),
    path('create_account_rider/', views.register_rider, name='create_account_rider'),
    path('login_in/', views.login_view, name='login'),
    path('main_view/', views.main_view, name='main_view'),
    path('logout/', views.logout_view, name='logout'),
    path('edit_account/', views.edit_account, name='edit_account'),
    path('accounts/login/', views.login_view, name='login'),
    path('password_change/', views.password_change, name='password_change'),
    path('rider_driver/', views.rider_driver, name='rider_driver'),
    path('driver_rider/', views.driver_rider, name='driver_rider'),
    path('request_ride/', views.request_ride, name='request_ride'),
    path('request_share_ride/', views.request_share_ride, name='request_share_ride'),
    path('edit_ride/<int:ride_id>/', views.edit_ride, name='edit_ride'),
    path('cancel_ride/<int:ride_id>/', views.cancel_ride, name='cancel_ride'),
    path('join_ride/<int:ride_id>/', views.join_ride, name='join_ride'),
    path('accept_ride/', views.accept_ride, name='accept_ride'),
    path('confirm_ride/<int:ride_id>/', views.confirm_ride, name='confirm_ride'),
    path('finish_ride/<int:ride_id>/', views.finish_ride, name='finish_ride'),
    path('ride_details/<int:ride_id>/', views.view_ride_details, name='ride_details'),
    path('passenger_count/<int:ride_id>/', views.passenger_count, name='passenger_count'),
]
