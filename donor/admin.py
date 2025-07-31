from django.contrib import admin
from .models import Donor, DonationCenter, DonationRequest, DonationHistory, EmergencyRequest

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['name', 'blood_group', 'age', 'phone_number', 'is_eligible', 'last_donation_date']
    list_filter = ['blood_group', 'gender', 'is_eligible']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(DonationCenter)
class DonationCenterAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'phone_number', 'is_active']
    list_filter = ['city', 'state', 'is_active']
    search_fields = ['name', 'city']

@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
    list_display = ['donor', 'requested_date', 'status', 'created_at']
    list_filter = ['status', 'requested_date']
    search_fields = ['donor__user__first_name', 'donor__user__last_name']

@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
    list_display = ['donor', 'donation_date', 'donation_center', 'units_donated']
    list_filter = ['donation_date', 'donation_center']
    search_fields = ['donor__user__first_name', 'donor__user__last_name']

@admin.register(EmergencyRequest)
class EmergencyRequestAdmin(admin.ModelAdmin):
    list_display = ['blood_group_needed', 'hospital_name', 'urgency_level', 'status', 'required_by']
    list_filter = ['blood_group_needed', 'urgency_level', 'status']
    search_fields = ['hospital_name', 'contact_person']
