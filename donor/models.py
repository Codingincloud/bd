from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date, timedelta
from utils.constants import (
    MINIMUM_DONATION_INTERVAL_DAYS,
    MINIMUM_DONOR_WEIGHT_KG,
    MAXIMUM_DONOR_WEIGHT_KG,
    BMI_UNDERWEIGHT,
    BMI_NORMAL,
    BMI_OVERWEIGHT,
    BLOOD_COMPATIBILITY,
    EARTH_RADIUS_KM,
    INVENTORY_CRITICAL_THRESHOLD,
    INVENTORY_LOW_THRESHOLD,
    INVENTORY_MEDIUM_THRESHOLD
)

class Donor(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

    # Enhanced location fields
    city = models.CharField(max_length=100, blank=True, help_text="City or town")
    state = models.CharField(max_length=100, blank=True, help_text="State or province")
    postal_code = models.CharField(max_length=20, blank=True, help_text="ZIP/Postal code")
    country = models.CharField(max_length=100, default='Nepal', help_text="Country")
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True, help_text="Latitude for mapping (optional)")
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, help_text="Longitude for mapping (optional)")

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(MINIMUM_DONOR_WEIGHT_KG), MaxValueValidator(MAXIMUM_DONOR_WEIGHT_KG)]
    )
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in cm")
    medical_conditions = models.TextField(blank=True)
    last_donation_date = models.DateField(null=True, blank=True)
    is_eligible = models.BooleanField(default=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    
    # Preferences
    allow_emergency_contact = models.BooleanField(default=True, help_text="Allow contact for emergency blood requests")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['blood_group']),
            models.Index(fields=['is_eligible']),
            models.Index(fields=['city', 'state']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['allow_emergency_contact', 'blood_group']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.blood_group})"

    @property
    def name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    @property
    def bmi(self):
        if self.weight and self.height:
            height_m = float(self.height) / 100  # Convert cm to meters
            return round(float(self.weight) / (height_m ** 2), 1)
        return None

    @property
    def bmi_category(self):
        bmi = self.bmi
        if not bmi:
            return "Unknown"
        if bmi < BMI_UNDERWEIGHT:
            return "Underweight"
        elif bmi < BMI_NORMAL:
            return "Normal"
        elif bmi < BMI_OVERWEIGHT:
            return "Overweight"
        else:
            return "Obese"

    @property
    def next_eligible_date(self):
        if self.last_donation_date:
            return self.last_donation_date + timedelta(days=MINIMUM_DONATION_INTERVAL_DAYS)
        return None

    @property
    def total_donations(self):
        return self.donationhistory_set.count()

    @property
    def full_location(self):
        """Returns a formatted full location string"""
        location_parts = []
        if self.city:
            location_parts.append(self.city)
        if self.state:
            location_parts.append(self.state)
        if self.postal_code:
            location_parts.append(self.postal_code)
        if self.country and self.country != 'Nepal':  # Only show country if not default
            location_parts.append(self.country)

        if location_parts:
            return ', '.join(location_parts)
        return self.address if self.address else 'Location not specified'

    def distance_to(self, other_lat, other_lng):
        """Calculate distance to another location in kilometers using Haversine formula"""
        if not (self.latitude and self.longitude and other_lat and other_lng):
            return None

        import math

        # Convert to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [float(self.latitude), float(self.longitude), float(other_lat), float(other_lng)])

        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))

        # Earth's radius from constants
        return round(c * EARTH_RADIUS_KM, 2)

    @property
    def compatible_blood_groups(self):
        """Returns blood groups this donor can donate to"""
        return BLOOD_COMPATIBILITY.get(self.blood_group, [])

    def can_donate(self):
        """Check if donor is eligible to donate based on last donation date"""
        if not self.last_donation_date:
            return True, "Eligible to donate"

        # Standard donation interval from constants
        next_eligible_date = self.last_donation_date + timedelta(days=MINIMUM_DONATION_INTERVAL_DAYS)
        today = date.today()

        if today >= next_eligible_date:
            return True, "Eligible to donate"
        else:
            days_remaining = (next_eligible_date - today).days
            return False, f"Must wait {days_remaining} more days. Next eligible date: {next_eligible_date.strftime('%B %d, %Y')}"

    @property
    def donation_eligibility_status(self):
        """Get donation eligibility status"""
        eligible, message = self.can_donate()
        return {
            'eligible': eligible,
            'message': message,
            'next_eligible_date': self.last_donation_date + timedelta(days=MINIMUM_DONATION_INTERVAL_DAYS) if self.last_donation_date else None
        }

class DonationCenter(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['city']),
        ]

    def __str__(self):
        return self.name

class DonationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    donation_center = models.ForeignKey(DonationCenter, on_delete=models.SET_NULL, null=True, blank=True, related_name='donation_requests')
    requested_date = models.DateField()
    preferred_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    # Rejection fields
    rejection_reason = models.TextField(blank=True)
    rejected_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='rejected_requests')
    rejected_at = models.DateTimeField(null=True, blank=True)

    # Completion fields
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.donor.name} - {self.requested_date} ({self.status})"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['requested_date']),
            models.Index(fields=['-created_at']),
        ]


class HealthMetrics(models.Model):
    """Model to store donor health metrics updates"""
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='health_metrics')
    weight = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    blood_pressure_systolic = models.IntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True)
    resting_heart_rate = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.name} - {self.recorded_at.strftime('%Y-%m-%d')}"

    @property
    def blood_pressure(self):
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return None

    class Meta:
        ordering = ['-recorded_at']
        verbose_name = 'Health Metrics'
        verbose_name_plural = 'Health Metrics'

class DonationHistory(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    donation_date = models.DateField()
    donation_center_name = models.CharField(max_length=200, blank=True)  # Store as string for simplicity
    units_donated = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    blood_pressure = models.CharField(max_length=20, blank=True)  # e.g., "120/80"
    hemoglobin_level = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    notes = models.TextField(blank=True)
    blood_center = models.ForeignKey(DonationCenter, on_delete=models.SET_NULL, null=True, blank=True)
    pre_donation_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    pulse_rate = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.name} - {self.donation_date}"

    class Meta:
        ordering = ['-donation_date']
        verbose_name_plural = "Donation histories"
        indexes = [
            models.Index(fields=['-donation_date']),
            models.Index(fields=['donor', '-donation_date']),
        ]


class BloodInventory(models.Model):
    """Track blood inventory by blood group"""
    blood_group = models.CharField(max_length=5, choices=Donor.BLOOD_GROUPS, unique=True)
    units_available = models.FloatField(default=0.0)
    units_reserved = models.FloatField(default=0.0, help_text="Units reserved for specific requests")
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Notes about inventory changes")

    class Meta:
        verbose_name_plural = "Blood Inventories"
        ordering = ['blood_group']

    def __str__(self):
        return f"{self.get_blood_group_display()}: {self.units_available} units"

    @property
    def status(self):
        """Get inventory status based on units available"""
        if self.units_available <= INVENTORY_CRITICAL_THRESHOLD:
            return 'critical'
        elif self.units_available <= INVENTORY_LOW_THRESHOLD:
            return 'low'
        elif self.units_available <= INVENTORY_MEDIUM_THRESHOLD:
            return 'medium'
        else:
            return 'good'

class EmergencyRequest(models.Model):
    URGENCY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('fulfilled', 'Fulfilled'),
        ('expired', 'Expired'),
    ]

    blood_group_needed = models.CharField(max_length=3, choices=Donor.BLOOD_GROUPS)
    units_needed = models.PositiveIntegerField()
    hospital_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)
    location = models.CharField(max_length=200)
    urgency_level = models.CharField(max_length=10, choices=URGENCY_LEVELS)
    required_by = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Emergency: {self.blood_group_needed} - {self.hospital_name}"

    @property
    def is_urgent(self):
        return self.urgency_level in ['high', 'critical']

    @property
    def time_remaining(self):
        if self.required_by > timezone.now():
            return self.required_by - timezone.now()
        return None

    class Meta:
        ordering = ['-urgency_level', '-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['blood_group_needed', 'status']),
            models.Index(fields=['-urgency_level', '-created_at']),
            models.Index(fields=['required_by']),
        ]


class EmergencyResponse(models.Model):
    """Track donor responses to emergency blood requests"""
    RESPONSE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    emergency_request = models.ForeignKey(EmergencyRequest, on_delete=models.CASCADE, related_name='responses')
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='emergency_responses')
    response_message = models.TextField(blank=True, help_text="Donor's response message")
    selected_hospital = models.ForeignKey('Hospital', on_delete=models.SET_NULL, null=True, blank=True, 
                                         help_text="Hospital selected by donor if multiple options")
    
    # Response tracking
    status = models.CharField(max_length=20, choices=RESPONSE_STATUS_CHOICES, default='pending')
    responded_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Donation details (filled when completed)
    units_donated = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    donation_notes = models.TextField(blank=True)
    
    # Admin tracking
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='confirmed_emergency_responses')
    admin_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-responded_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['emergency_request', 'status']),
            models.Index(fields=['-responded_at']),
        ]
        unique_together = ['emergency_request', 'donor']  # One response per donor per emergency
    
    def __str__(self):
        return f"{self.donor.name} → {self.emergency_request.hospital_name} ({self.status})"
    
    def confirm_response(self, confirmed_by_user):
        """Confirm donor's response"""
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.confirmed_by = confirmed_by_user
        self.save()
    
    def mark_completed(self, units_donated, notes=''):
        """Mark donation as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.units_donated = units_donated
        self.donation_notes = notes
        self.save()


class Hospital(models.Model):
    """Model for hospitals and blood donation centers"""
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='Nepal')
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    
    # Location coordinates
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Hospital details
    hospital_type = models.CharField(max_length=50, choices=[
        ('government', 'Government Hospital'),
        ('private', 'Private Hospital'),
        ('blood_bank', 'Blood Bank'),
        ('clinic', 'Clinic'),
        ('medical_college', 'Medical College'),
    ], default='government')
    
    # Blood donation services
    has_blood_bank = models.BooleanField(default=True)
    accepts_donations = models.BooleanField(default=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    
    # Operating hours
    operating_hours = models.CharField(max_length=100, default='24/7')
    
    # Services offered
    services = models.TextField(help_text="Comma-separated list of services", default="Blood Collection, Blood Testing, Emergency Supply")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active', 'accepts_donations']),
            models.Index(fields=['city']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['hospital_type']),
        ]

    def __str__(self):
        return f"{self.name} - {self.city}"

    @property
    def services_list(self):
        """Return services as a list"""
        return [service.strip() for service in self.services.split(',') if service.strip()]

    def distance_to_donor(self, donor):
        """Calculate distance to a donor in kilometers"""
        if not (self.latitude and self.longitude and donor.latitude and donor.longitude):
            return None
        
        import math
        
        # Convert to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [
            float(donor.latitude), float(donor.longitude), 
            float(self.latitude), float(self.longitude)
        ])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius from constants
        return round(c * EARTH_RADIUS_KM, 2)

    @classmethod
    def get_nearest_hospitals(cls, donor, max_distance=50, limit=10):
        """Get nearest hospitals to a donor"""
        if not (donor.latitude and donor.longitude):
            return cls.objects.filter(is_active=True, accepts_donations=True)[:limit]
        
        hospitals = cls.objects.filter(is_active=True, accepts_donations=True)
        hospitals_with_distance = []
        
        for hospital in hospitals:
            distance = hospital.distance_to_donor(donor)
            if distance is not None and distance <= max_distance:
                hospitals_with_distance.append((hospital, distance))
        
        # Sort by distance
        hospitals_with_distance.sort(key=lambda x: x[1])
        
        return [hospital for hospital, distance in hospitals_with_distance[:limit]]
