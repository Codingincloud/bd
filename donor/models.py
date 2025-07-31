from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date, timedelta

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
        validators=[MinValueValidator(45), MaxValueValidator(200)]
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
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    def can_donate(self):
        if not self.last_donation_date:
            return True
        # Standard waiting period of 56 days (8 weeks) between donations
        next_donation_date = self.last_donation_date + timedelta(days=56)
        return date.today() >= next_donation_date

    @property
    def next_eligible_date(self):
        if self.last_donation_date:
            return self.last_donation_date + timedelta(days=56)
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

        # Earth's radius in kilometers
        r = 6371

        return round(c * r, 2)

    @property
    def compatible_blood_groups(self):
        """Returns blood groups this donor can donate to"""
        compatibility = {
            'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],  # Universal donor
            'O+': ['O+', 'A+', 'B+', 'AB+'],
            'A-': ['A-', 'A+', 'AB-', 'AB+'],
            'A+': ['A+', 'AB+'],
            'B-': ['B-', 'B+', 'AB-', 'AB+'],
            'B+': ['B+', 'AB+'],
            'AB-': ['AB-', 'AB+'],
            'AB+': ['AB+'],
        }
        return compatibility.get(self.blood_group, [])

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

    def __str__(self):
        return self.name

class DonationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    requested_date = models.DateField()
    preferred_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.donor.name} - {self.requested_date} ({self.status})"

    class Meta:
        ordering = ['-created_at']


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
    donation_center = models.CharField(max_length=200)  # Store as string for simplicity
    units_donated = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    blood_pressure = models.CharField(max_length=20, blank=True)  # e.g., "120/80"
    hemoglobin_level = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.name} - {self.donation_date}"

    class Meta:
        ordering = ['-donation_date']
        verbose_name_plural = "Donation histories"

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
