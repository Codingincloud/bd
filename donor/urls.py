from django.urls import path
from . import views

app_name = 'donor'

urlpatterns = [
    path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('location/update/', views.update_location, name='update_location'),
    path('location/detect/', views.detect_location, name='detect_location'),
    path('compatibility/', views.compatibility_check, name='compatibility_check'),
    path('blood-inventory/', views.blood_inventory, name='blood_inventory'),
    path('donation-centers/', views.donation_centers, name='donation_centers'),
    path('medical-reports/', views.medical_reports, name='medical_reports'),
    path('medical-info/update/', views.update_medical_info, name='update_medical_info'),
    path('health-metrics/add/', views.add_health_metrics, name='add_health_metrics'),
    path('donation/schedule/', views.schedule_donation, name='schedule_donation'),
    path('donation/history/', views.donation_history, name='donation_history'),
    path('emergency-requests/', views.emergency_requests, name='emergency_requests'),
    path('request/cancel/<int:request_id>/', views.cancel_request, name='cancel_request'),
]
