from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('donors/', views.manage_donors, name='manage_donors'),
    path('donors/location-search/', views.location_search, name='location_search'),

    path('api/geocode/', views.geocode_address, name='geocode_address'),
    path('api/address-suggestions/', views.address_suggestions, name='address_suggestions'),
    path('api/location-search-by-name/', views.location_search_by_name, name='location_search_by_name'),
    path('requests/', views.manage_requests, name='manage_requests'),
    path('requests/approve/<int:request_id>/', views.approve_request, name='approve_request'),
    path('inventory/', views.manage_inventory, name='manage_inventory'),
    path('emergencies/', views.manage_emergencies, name='manage_emergencies'),
    path('emergencies/create/', views.create_emergency_request, name='create_emergency_request'),
    path('requests/approve/<int:request_id>/', views.approve_donation_request, name='approve_donation_request'),
    path('requests/reject/<int:request_id>/', views.reject_donation_request, name='reject_donation_request'),
    path('requests/complete/<int:request_id>/', views.mark_donation_completed, name='mark_donation_completed'),
    path('blood-centers/', views.manage_blood_centers, name='manage_blood_centers'),
    path('blood-centers/delete/<int:center_id>/', views.delete_blood_center, name='delete_blood_center'),
    path('donor-tracking/', views.donor_tracking, name='donor_tracking'),
    path('reports/', views.reports, name='reports'),
]
