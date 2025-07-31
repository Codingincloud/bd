from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Donor, DonationCenter, DonationRequest, DonationHistory, EmergencyRequest, HealthMetrics

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['name', 'blood_group', 'age', 'phone_number', 'city', 'is_eligible', 'last_donation_date', 'total_donations']
    list_filter = ['blood_group', 'gender', 'is_eligible', 'city', 'country', 'created_at']
    search_fields = [
        'user__first_name', 'user__last_name', 'user__username', 'user__email',
        'phone_number', 'address', 'city', 'country', 'emergency_contact_name',
        'emergency_contact_phone', 'medical_conditions'
    ]
    readonly_fields = ['created_at', 'updated_at', 'age', 'bmi', 'total_donations']
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'blood_group', 'date_of_birth', 'gender', 'phone_number')
        }),
        ('Physical Information', {
            'fields': ('weight', 'height', 'bmi')
        }),
        ('Location Information', {
            'fields': ('address', 'city', 'country', 'latitude', 'longitude')
        }),
        ('Medical Information', {
            'fields': ('medical_conditions', 'medications', 'is_eligible')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'allow_emergency_contact')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'age', 'total_donations'),
            'classes': ('collapse',)
        })
    )

    def get_search_results(self, request, queryset, search_term):
        """Enhanced search functionality"""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if search_term:
            # Additional search for blood group compatibility
            blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
            if search_term.upper() in blood_groups:
                queryset |= self.model.objects.filter(blood_group__icontains=search_term)

            # Search by age range
            if search_term.isdigit():
                age = int(search_term)
                queryset |= self.model.objects.extra(
                    where=["EXTRACT(year FROM age(date_of_birth)) = %s"],
                    params=[age]
                )

        return queryset, use_distinct

@admin.register(DonationCenter)
class DonationCenterAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'phone_number', 'email', 'is_active', 'created_at']
    list_filter = ['city', 'state', 'is_active', 'created_at']
    search_fields = [
        'name', 'city', 'state', 'address', 'phone_number', 'email',
        'contact_person', 'description'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ['name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'phone_number', 'email')
        }),
        ('Location Information', {
            'fields': ('address', 'city', 'state', 'postal_code', 'latitude', 'longitude')
        }),
        ('Operating Information', {
            'fields': ('operating_hours', 'services_offered')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
    list_display = ['donor_name', 'donor_blood_group', 'requested_date', 'status', 'created_at']
    list_filter = ['status', 'requested_date', 'donor__blood_group', 'created_at']
    search_fields = [
        'donor__user__first_name', 'donor__user__last_name', 'donor__user__username',
        'donor__phone_number', 'donor__blood_group', 'notes', 'admin_notes'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'requested_date'
    ordering = ['-created_at']

    def donor_name(self, obj):
        return obj.donor.name
    donor_name.short_description = 'Donor Name'
    donor_name.admin_order_field = 'donor__user__first_name'

    def donor_blood_group(self, obj):
        return obj.donor.blood_group
    donor_blood_group.short_description = 'Blood Group'
    donor_blood_group.admin_order_field = 'donor__blood_group'

@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
    list_display = ['donor_name', 'donor_blood_group', 'donation_date', 'donation_center', 'units_donated']
    list_filter = ['donation_date', 'donation_center', 'donor__blood_group', 'created_at']
    search_fields = [
        'donor__user__first_name', 'donor__user__last_name', 'donor__user__username',
        'donor__phone_number', 'donor__blood_group', 'donation_center',
        'notes'
    ]
    readonly_fields = ['created_at']
    list_per_page = 25
    date_hierarchy = 'donation_date'
    ordering = ['-donation_date']

    def donor_name(self, obj):
        return obj.donor.name
    donor_name.short_description = 'Donor Name'
    donor_name.admin_order_field = 'donor__user__first_name'

    def donor_blood_group(self, obj):
        return obj.donor.blood_group
    donor_blood_group.short_description = 'Blood Group'
    donor_blood_group.admin_order_field = 'donor__blood_group'

@admin.register(EmergencyRequest)
class EmergencyRequestAdmin(admin.ModelAdmin):
    list_display = ['blood_group_needed', 'hospital_name', 'urgency_level', 'status', 'required_by', 'units_needed', 'created_at']
    list_filter = ['blood_group_needed', 'urgency_level', 'status', 'required_by', 'created_at']
    search_fields = [
        'hospital_name', 'contact_person', 'contact_phone', 'contact_email',
        'patient_name', 'blood_group_needed', 'location', 'description'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    date_hierarchy = 'required_by'
    ordering = ['-urgency_level', 'required_by']

    fieldsets = (
        ('Emergency Information', {
            'fields': ('blood_group_needed', 'units_needed', 'urgency_level', 'required_by')
        }),
        ('Hospital Information', {
            'fields': ('hospital_name', 'location', 'description')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'contact_phone', 'contact_email')
        }),
        ('Patient Information', {
            'fields': ('patient_name', 'patient_age', 'medical_condition')
        }),
        ('Status', {
            'fields': ('status', 'fulfilled_at', 'notes')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(HealthMetrics)
class HealthMetricsAdmin(admin.ModelAdmin):
    list_display = ['donor_name', 'donor_blood_group', 'weight', 'blood_pressure', 'resting_heart_rate', 'recorded_at']
    list_filter = ['recorded_at', 'donor__blood_group', 'donor__city']
    search_fields = [
        'donor__user__first_name', 'donor__user__last_name', 'donor__user__username',
        'donor__phone_number', 'donor__blood_group', 'notes'
    ]
    readonly_fields = ['recorded_at']
    list_per_page = 25
    date_hierarchy = 'recorded_at'
    ordering = ['-recorded_at']

    def donor_name(self, obj):
        return obj.donor.name
    donor_name.short_description = 'Donor Name'
    donor_name.admin_order_field = 'donor__user__first_name'

    def donor_blood_group(self, obj):
        return obj.donor.blood_group
    donor_blood_group.short_description = 'Blood Group'
    donor_blood_group.admin_order_field = 'donor__blood_group'
