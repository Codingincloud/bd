from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

@login_required
def check_updates(request):
    """Check if there are any updates for the current user's dashboard"""
    if request.user.is_staff:
        # For admin users
        update_available = cache.get('admin_dashboard_update', False)
        if update_available:
            cache.delete('admin_dashboard_update')
    else:
        # For donor users
        update_available = cache.get(f'donor_update_{request.user.id}', False)
        if update_available:
            cache.delete(f'donor_update_{request.user.id}')
    
    return JsonResponse({'update_available': update_available})
