import logging
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

class DashboardCacheMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip for non-authenticated users
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
            
        # Check if session is valid
        session = request.session
        user_id = session.get('_auth_user_id')
        
        # Only proceed if we have a valid user ID in session
        if not user_id or str(user_id) != str(request.user.id):
            logger.warning(f'Session user ID mismatch. Session: {user_id}, User: {request.user.id}')
            # Don't log out, just log the issue
            return None
            
        # Update session expiry on each request
        session.set_expiry(settings.SESSION_COOKIE_AGE)
        
        return None

    def process_response(self, request, response):
        # Skip for non-authenticated users
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
            
        try:
            # Invalidate caches on POST, PUT, DELETE requests
            if request.method in ['POST', 'PUT', 'DELETE']:
                # Invalidate admin cache on any admin action
                if hasattr(request.user, 'is_staff') and request.user.is_staff:
                    cache.delete('admin_dashboard_data')
                
                # Invalidate donor cache for the current user
                if hasattr(request.user, 'donor'):
                    cache_key = f'donor_dashboard_{request.user.id}'
                    cache.delete(cache_key)
                    logger.debug(f'Invalidated cache for donor {request.user.id}')
                    
            # Ensure session is saved if user is authenticated
            if request.user.is_authenticated and not request.session.modified:
                request.session.modified = True
                
        except Exception as e:
            logger.error(
                f'Error in DashboardCacheMiddleware: {str(e)}', 
                exc_info=True, 
                extra={'user_id': getattr(request.user, 'id', None)}
            )
        
        return response
