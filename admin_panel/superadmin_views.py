"""
Superadmin-only views for system administration
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from admin_panel.models import AdminProfile
from donor.models import Hospital, Donor


@login_required
def superadmin_dashboard(request):
    """Minimal superadmin dashboard with only core functions"""
    # Check if user is superadmin
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superadmin privileges required.')
        return redirect('admin_panel:dashboard')
    
    # Get system-wide statistics
    total_hospitals = Hospital.objects.count()
    active_staff = User.objects.filter(is_staff=True, is_active=True, is_superuser=False).count()
    pending_users = User.objects.filter(is_staff=True, is_active=False).count()
    total_donors = Donor.objects.count()
    
    context = {
        'total_hospitals': total_hospitals,
        'active_staff': active_staff,
        'pending_users': pending_users,
        'total_donors': total_donors,
    }
    
    return render(request, 'admin_panel/superadmin_dashboard.html', context)


@login_required
def verify_users(request):
    """Approve/reject pending hospital admin registrations - Superadmin only"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superadmin only.')
        return redirect('admin_panel:dashboard')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        try:
            user = User.objects.get(id=user_id)
            
            if action == 'approve':
                user.is_active = True
                user.save()
                messages.success(request, f'✅ Approved {user.username} - {user.get_full_name()}')
            elif action == 'reject':
                username = user.username
                full_name = user.get_full_name()
                user.delete()
                messages.success(request, f'❌ Rejected and deleted {username} - {full_name}')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        
        return redirect('admin_panel:verify_users')
    
    # Show pending users (inactive hospital admins)
    pending_users = User.objects.filter(
        is_staff=True, 
        is_active=False
    ).select_related('adminprofile', 'hospital').order_by('-date_joined')
    
    return render(request, 'admin_panel/verify_users.html', {
        'pending_users': pending_users
    })


@login_required
def view_all_staff(request):
    """View all hospital staff (read-only) - Superadmin only"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superadmin only.')
        return redirect('admin_panel:dashboard')
    
    # Get all hospital staff (exclude superadmins)
    all_staff = User.objects.filter(
        is_staff=True, 
        is_superuser=False
    ).select_related('adminprofile', 'hospital').order_by('-date_joined')
    
    return render(request, 'admin_panel/view_all_staff.html', {
        'all_staff': all_staff
    })
