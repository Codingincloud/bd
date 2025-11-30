from django.urls import path
from . import views

app_name = 'donor'

urlpatterns = [
    path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/deactivate/', views.deactivate_account, name='deactivate_account'),
    path('location/update/', views.update_location, name='update_location'),
    path('location/update-map/', views.update_location_map_view, name='update_location_map'),
    path('location/detect/', views.detect_location, name='detect_location'),
    path('location/save/', views.save_detected_location, name='save_detected_location'),

    # Notification URLs
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/all/', views.all_notifications, name='all_notifications'),
    path('notifications/dismiss-system/<int:notification_id>/', views.dismiss_system_notification, name='dismiss_system_notification'),
    path('compatibility/', views.compatibility_check, name='compatibility_check'),
    path('blood-inventory/', views.blood_inventory, name='blood_inventory'),
    path('donation-centers/', views.donation_centers, name='donation_centers'),
    path('hospitals/', views.hospitals_list, name='hospitals_list'),
    path('hospitals/nearest/', views.get_nearest_hospitals, name='get_nearest_hospitals'),
    path('medical-reports/', views.medical_reports, name='medical_reports'),
    path('medical-info/update/', views.update_medical_info, name='update_medical_info'),
    path('health-metrics/add/', views.add_health_metrics, name='add_health_metrics'),
    path('health-metrics/update/', views.update_health_metrics, name='update_health_metrics'),
    path('donation/schedule/', views.schedule_donation, name='schedule_donation'),
    path('donation/history/', views.donation_history, name='donation_history'),
    path('emergency-requests/', views.emergency_requests, name='emergency_requests'),
    path('emergencies/<int:emergency_id>/respond/', views.respond_to_emergency, name='respond_to_emergency'),
    path('request/cancel/<int:request_id>/', views.cancel_request, name='cancel_request'),
]
