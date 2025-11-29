"""
Custom decorators to simplify view access control
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def admin_required(view_func):
    """
    Decorator that checks if user is staff/admin before allowing access.
    Simplified alternative to @user_passes_test(lambda u: u.is_staff)
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('accounts:login')
        
        if not request.user.is_staff:
            messages.error(request, 'You must be an admin to access this page.')
            return redirect('donor:donor_dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def donor_required(view_func):
    """
    Decorator that checks if user has a donor profile.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            # Check if user has donor profile
            donor = request.user.donor
            return view_func(request, *args, **kwargs)
        except AttributeError:
            messages.error(request, 'Donor profile not found. Please contact support.')
            return redirect('accounts:login')
    
    return wrapper
