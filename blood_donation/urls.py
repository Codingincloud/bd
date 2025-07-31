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
    context = {
        'system_name': 'Blood Donation Management System',
        'system_description': 'Comprehensive Blood Donation Management Platform'
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
