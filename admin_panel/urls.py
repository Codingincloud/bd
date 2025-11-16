from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('donors/location-search/', views.location_search, name='location_search'),

    path('api/geocode/', views.geocode_address, name='geocode_address'),
    path('api/address-suggestions/', views.address_suggestions, name='address_suggestions'),
    path('api/location-search-by-name/', views.location_search_by_name, name='location_search_by_name'),
    path('requests/', views.manage_requests, name='manage_requests'),
    path('requests/<int:request_id>/approve/', views.approve_donation_request, name='approve_donation_request'),
    path('requests/<int:request_id>/reject/', views.reject_donation_request, name='reject_donation_request'),
    path('requests/<int:request_id>/complete/', views.complete_donation_request, name='complete_donation_request'),
    path('requests/<int:request_id>/cancel/', views.cancel_donation_request, name='cancel_donation_request'),
    path('inventory/', views.manage_inventory, name='manage_inventory'),
    path('emergencies/', views.manage_emergencies, name='manage_emergencies'),
    path('emergencies/create/', views.create_emergency_request, name='create_emergency_request'),
    path('emergencies/<int:emergency_id>/respond/', views.respond_to_emergency_admin, name='respond_to_emergency'),
    path('emergencies/<int:emergency_id>/resolve/', views.resolve_emergency, name='resolve_emergency'),
    path('inventory/update/', views.update_inventory, name='update_inventory'),
    path('blood-centers/', views.manage_blood_centers, name='manage_blood_centers'),
    path('blood-centers/delete/<int:center_id>/', views.delete_blood_center, name='delete_blood_center'),
    path('donor-tracking/', views.donor_tracking, name='donor_tracking'),
    path('donor-detail/<int:donor_id>/', views.donor_detail, name='donor_detail'),
    path('donor-edit/<int:donor_id>/', views.edit_donor, name='edit_donor'),
    path('donor/<int:donor_id>/deactivate/', views.deactivate_donor, name='deactivate_donor'),
    path('donor/<int:donor_id>/activate/', views.activate_donor, name='activate_donor'),
    path('profile/', views.admin_profile, name='admin_profile'),
    path('profile/edit/', views.edit_admin_profile, name='edit_admin_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('reports/', views.reports, name='reports'),
    path('export/donors/', views.export_donors, name='export_donors'),
    path('export/donations/', views.export_donations, name='export_donations'),
    path('export/reports/', views.export_reports, name='export_reports'),
    path('notifications/', views.all_notifications, name='all_notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]
