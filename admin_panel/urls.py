from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('donors/', views.manage_donors, name='manage_donors'),
    path('donors/location-search/', views.location_search, name='location_search'),
    path('donors/nepal-search/', views.nepal_location_search, name='nepal_location_search'),
    path('api/nepal-suggestions/', views.nepal_suggestions, name='nepal_suggestions'),
    path('api/geocode/', views.geocode_address, name='geocode_address'),
    path('api/address-suggestions/', views.address_suggestions, name='address_suggestions'),
    path('api/location-search-by-name/', views.location_search_by_name, name='location_search_by_name'),
    path('requests/', views.manage_requests, name='manage_requests'),
    path('requests/approve/<int:request_id>/', views.approve_request, name='approve_request'),
    path('inventory/', views.manage_inventory, name='manage_inventory'),
    path('emergencies/', views.manage_emergencies, name='manage_emergencies'),
    path('reports/', views.reports, name='reports'),
]
