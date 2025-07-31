from django.db import models
from django.contrib.auth.models import User
from donor.models import Donor, DonationCenter

class AdminProfile(models.Model):
    """Admin profile with additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=20)
    address = models.CharField(max_length=255)

    # Enhanced location fields
    city = models.CharField(max_length=100, blank=True, help_text="City or town")
    state = models.CharField(max_length=100, blank=True, help_text="State or province")
    postal_code = models.CharField(max_length=20, blank=True, help_text="ZIP/Postal code")
    country = models.CharField(max_length=100, default='Nepal', help_text="Country")
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True, help_text="Latitude for mapping (optional)")
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, help_text="Longitude for mapping (optional)")

    email = models.EmailField()
    photo = models.ImageField(upload_to='admin_photos/', blank=True, null=True)
    department = models.CharField(max_length=100, default='Blood Bank Management')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

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

class SystemNotification(models.Model):
    """System-wide notifications managed by admin"""
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('urgent', 'Urgent'),
        ('maintenance', 'Maintenance'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    is_active = models.BooleanField(default=True)
    target_audience = models.CharField(max_length=20, choices=[
        ('all', 'All Users'),
        ('donors', 'Donors Only'),
        ('admins', 'Admins Only'),
    ], default='all')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
