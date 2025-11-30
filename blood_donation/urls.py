"""
URL configuration for blood_donation project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

# Customize admin site
admin.site.site_header = 'Blood Donation Management System'
admin.site.site_title = 'Blood Donation Admin'
admin.site.index_title = 'Blood Donation Administration'

def home(request):
    """Home page for Blood Donation Management System"""
    from donor.models import Donor, BloodInventory
    from django.db.models import Count, Sum
    
    # Get blood group distribution from donors
    blood_group_stats = Donor.objects.values('blood_group').annotate(count=Count('id')).order_by('-count')
    
    # Get total inventory across all hospitals
    total_inventory = BloodInventory.objects.values('blood_group').annotate(
        total_units=Sum('units_available')
    ).order_by('blood_group')
    
    # Format blood groups for display
    blood_groups_data = {}
    for stat in blood_group_stats:
        blood_groups_data[stat['blood_group']] = {
            'donors': stat['count'],
            'inventory': 0
        }
    
    # Add inventory data
    for inv in total_inventory:
        bg = inv['blood_group']
        if bg in blood_groups_data:
            blood_groups_data[bg]['inventory'] = inv['total_units'] or 0
        else:
            blood_groups_data[bg] = {
                'donors': 0,
                'inventory': inv['total_units'] or 0
            }
    
    context = {
        'system_name': 'Blood Donation Management System',
        'system_description': 'Comprehensive Blood Donation Management Platform',
        'total_donors': Donor.objects.filter(user__is_active=True).count(),
        'total_hospitals': BloodInventory.objects.values('hospital').distinct().count(),
        'blood_groups_data': blood_groups_data,
    }
    return render(request, 'home.html', context)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('donor/', include('donor.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    path('', home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
