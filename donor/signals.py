from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import DonationRequest, DonationHistory, EmergencyRequest

@receiver([post_save, post_delete], sender=DonationRequest)
@receiver([post_save, post_delete], sender=DonationHistory)
@receiver([post_save, post_delete], sender=EmergencyRequest)
def update_dashboard_cache(sender, instance, **kwargs):
    # Invalidate cache for admin dashboard
    cache.delete('admin_dashboard_data')
    
    # Invalidate cache for donor's dashboard if applicable
    if hasattr(instance, 'donor'):
        cache.delete(f'donor_dashboard_{instance.donor.id}')
        cache.set(f'donor_update_{instance.donor.id}', True, 60)  # Set update flag for 60 seconds
