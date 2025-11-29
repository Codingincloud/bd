from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.html import format_html
from .models import Donor, DonationRequest, DonationHistory, EmergencyRequest, HealthMetrics, Hospital, BloodInventory

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'hospital_type', 'city', 'state', 'phone_number', 'has_blood_bank', 'accepts_donations', 'is_active']
    list_filter = ['hospital_type', 'city', 'state', 'has_blood_bank', 'accepts_donations', 'is_active']
    search_fields = ['name', 'address', 'city', 'state', 'phone_number', 'email']
    list_editable = ['is_active']
    list_per_page = 25
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'hospital_type', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'emergency_contact')
        }),
        ('Location Information', {
            'fields': ('address', 'city', 'state', 'latitude', 'longitude')
        }),
        ('Services', {
            'fields': ('has_blood_bank', 'accepts_donations', 'operating_hours', 'services')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['created_at', 'updated_at']

@admin.register(BloodInventory)
class BloodInventoryAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'blood_group', 'units_available', 'units_reserved', 'last_updated', 'status']
    list_filter = ['hospital', 'blood_group', 'last_updated']
    search_fields = ['hospital__name', 'blood_group', 'notes']
    list_editable = ['units_available', 'units_reserved']
    list_per_page = 10
    ordering = ['hospital', 'blood_group']
    
    fieldsets = (
        ('Inventory Details', {
            'fields': ('hospital', 'blood_group', 'units_available', 'units_reserved', 'notes')
        }),
        ('System Information', {
            'fields': ('last_updated', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['last_updated']

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['name', 'blood_group', 'age', 'phone_number', 'city', 'is_eligible', 'last_donation_date']
    list_filter = ['blood_group', 'gender', 'is_eligible', 'city', 'country', 'created_at']
    search_fields = [
        'user__first_name', 'user__last_name', 'user__username', 'user__email',
        'phone_number', 'address', 'city', 'country', 'emergency_contact_name',
        'emergency_contact_phone', 'medical_conditions'
    ]
    readonly_fields = ['created_at', 'updated_at', 'age', 'bmi']
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
            'fields': ('address', 'city', 'state', 'postal_code', 'country', 'latitude', 'longitude')
        }),
        ('Medical Information', {
            'fields': ('medical_conditions', 'is_eligible', 'last_donation_date')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'allow_emergency_contact')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'age'),
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
    list_display = ['donor_name', 'donor_blood_group', 'donation_date', 'donation_center_name', 'units_donated']
    list_filter = ['donation_date', 'donation_center_name', 'donor__blood_group', 'created_at']
    search_fields = [
        'donor__user__first_name', 'donor__user__last_name', 'donor__user__username',
        'donor__phone_number', 'donor__blood_group', 'donation_center_name',
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
        'hospital_name', 'contact_person', 'contact_phone',
        'blood_group_needed', 'location', 'notes'
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
            'fields': ('hospital_name', 'location')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'contact_phone')
        }),
        ('Status', {
            'fields': ('status', 'notes')
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
