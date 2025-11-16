from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count
from donor.models import DonationRequest, DonationHistory, EmergencyRequest, Donor

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    cache_key = 'admin_dashboard_data'
    data = cache.get(cache_key)
    
    if not data:
        pending_requests = DonationRequest.objects.filter(status='pending').select_related('donor')
        recent_donations = DonationHistory.objects.all().order_by('-donation_date')[:10]
        emergency_requests = EmergencyRequest.objects.filter(status='active').order_by('required_by')
        total_donors = Donor.objects.count()
        recent_donors = Donor.objects.order_by('-user__date_joined')[:5]
        
        # Calculate blood group distribution
        blood_groups = Donor.objects.values('blood_group').annotate(count=Count('id')).order_by('blood_group')
        blood_group_dict = {bg['blood_group']: bg['count'] for bg in blood_groups}
        
        # Create lists for template (easier to work with in JavaScript)
        blood_group_labels = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        blood_group_counts = [blood_group_dict.get(bg, 0) for bg in blood_group_labels]
        
        # Calculate active donors (donated in last 6 months)
        six_months_ago = timezone.now() - timezone.timedelta(days=180)
        active_donors = Donor.objects.filter(
            donation_history__donation_date__gte=six_months_ago
        ).distinct().count()
        
        data = {
            'pending_requests': pending_requests,
            'recent_donations': recent_donations,
            'emergency_requests': emergency_requests,
            'total_donors': total_donors,
            'active_donors': active_donors,
            'total_donations': DonationHistory.objects.count(),
            'recent_donors': recent_donors,
            'blood_group_labels': blood_group_labels,
            'blood_group_counts': blood_group_counts,
            'has_updates': False
        }
        cache.set(cache_key, 60)  # Cache for 1 minute
    
    # Check for updates
    if cache.get('admin_dashboard_update'):
        data['has_updates'] = True
        cache.delete('admin_dashboard_update')
    
    return render(request, 'admin_panel/dashboard.html', data)

