from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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
        ('donation_scheduled', 'Donation Scheduled'),
        ('donation_reminder', 'Donation Reminder'),
        ('emergency_request', 'Emergency Blood Request'),
        ('donation_completed', 'Donation Completed'),
        ('eligibility_update', 'Eligibility Update'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default='info')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_active = models.BooleanField(default=True)
    target_audience = models.CharField(max_length=20, choices=[
        ('all', 'All Users'),
        ('donors', 'Donors Only'),
        ('admins', 'Admins Only'),
    ], default='all')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    action_url = models.URLField(blank=True, help_text="Optional URL for action button")

    # For targeted notifications
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    class Meta:
        ordering = ['-created_at']


class UserNotification(models.Model):
    """Individual user notifications for specific events"""
    NOTIFICATION_TYPES = [
        ('donation_scheduled', 'Donation Scheduled'),
        ('donation_reminder', 'Donation Reminder'),
        ('donation_completed', 'Donation Completed'),
        ('emergency_request', 'Emergency Blood Request'),
        ('eligibility_restored', 'Eligibility Restored'),
        ('profile_updated', 'Profile Updated'),
        ('location_updated', 'Location Updated'),
        ('health_metrics_added', 'Health Metrics Added'),
        ('request_approved', 'Request Approved'),
        ('request_rejected', 'Request Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    action_url = models.URLField(blank=True)

    # Related objects for context
    related_donation_request = models.ForeignKey('donor.DonationRequest', on_delete=models.CASCADE, null=True, blank=True)
    related_emergency = models.ForeignKey('donor.EmergencyRequest', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}: {self.title}"

    class Meta:
        ordering = ['-created_at']


class SystemNotificationRead(models.Model):
    """Track which system notifications each user has dismissed/read"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    system_notification = models.ForeignKey(SystemNotification, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'system_notification')
        ordering = ['-read_at']

    def __str__(self):
        return f"{self.user.username} read {self.system_notification.title}"
