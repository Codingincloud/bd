from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta, date
import json
from donor.models import (
    Donor, DonationRequest, DonationHistory, EmergencyRequest, DonationCenter
)
from .models import AdminProfile, SystemNotification
from utils.geocoding import geocoding_service
from utils.nepal_locations import get_nepal_location, get_nepal_suggestions

def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard with key statistics"""
    
    # Basic Statistics
    total_donors = Donor.objects.count()
    total_donations = DonationHistory.objects.count()
    pending_requests = DonationRequest.objects.filter(status='pending').count()
    active_emergencies = EmergencyRequest.objects.filter(status='active').count()
    
    # Today's statistics
    today = date.today()
    today_donations = DonationHistory.objects.filter(donation_date=today).count()
    today_requests = DonationRequest.objects.filter(created_at__date=today).count()
    
    # This month's statistics
    month_start = today.replace(day=1)
    month_donations = DonationHistory.objects.filter(donation_date__gte=month_start).count()
    month_new_donors = Donor.objects.filter(created_at__date__gte=month_start).count()
    
    # Blood inventory summary (simplified)
    blood_inventory = {}
    for blood_group, _ in Donor.BLOOD_GROUPS:
        # Count recent donations as available inventory (simplified)
        recent_donations = DonationHistory.objects.filter(
            donor__blood_group=blood_group,
            donation_date__gte=today - timedelta(days=35)  # Blood expires in 35 days
        ).aggregate(total=Sum('units_donated'))['total'] or 0
        blood_inventory[blood_group] = int(recent_donations)
    
    # Recent activities
    recent_donations = DonationHistory.objects.select_related(
        'donor__user'
    ).order_by('-created_at')[:5]
    
    recent_requests = DonationRequest.objects.select_related(
        'donor__user'
    ).order_by('-created_at')[:5]
    
    # Pending approvals
    pending_approvals = DonationRequest.objects.filter(
        status='pending'
    ).select_related('donor__user').order_by('requested_date')[:10]
    
    # Emergency requests requiring attention
    urgent_emergencies = EmergencyRequest.objects.filter(
        status='active',
        urgency_level__in=['high', 'critical']
    ).order_by('-urgency_level', 'required_by')[:5]
    
    # Blood group distribution
    blood_group_stats = []
    for blood_group, _ in Donor.BLOOD_GROUPS:
        donor_count = Donor.objects.filter(blood_group=blood_group).count()
        donation_count = DonationHistory.objects.filter(donor__blood_group=blood_group).count()
        blood_group_stats.append({
            'blood_group': blood_group,
            'donors': donor_count,
            'donations': donation_count,
            'inventory': blood_inventory.get(blood_group, 0)
        })

    # Location statistics
    location_stats = {
        'total_with_coordinates': Donor.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).count(),
        'top_cities': Donor.objects.exclude(city='').values('city').annotate(
            count=Count('id')
        ).order_by('-count')[:5],
        'top_states': Donor.objects.exclude(state='').values('state').annotate(
            count=Count('id')
        ).order_by('-count')[:5],
    }

    context = {
        'total_donors': total_donors,
        'total_donations': total_donations,
        'pending_requests': pending_requests,
        'active_emergencies': active_emergencies,
        'today_donations': today_donations,
        'today_requests': today_requests,
        'month_donations': month_donations,
        'month_new_donors': month_new_donors,
        'blood_inventory': blood_inventory,
        'recent_donations': recent_donations,
        'recent_requests': recent_requests,
        'pending_approvals': pending_approvals,
        'urgent_emergencies': urgent_emergencies,
        'blood_group_stats': blood_group_stats,
        'location_stats': location_stats,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def manage_donors(request):
    """Manage donors with enhanced location-based search"""
    donors = Donor.objects.select_related('user').order_by('-created_at')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        donors = donors.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(blood_group__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(state__icontains=search_query)
        )

    # Filter by blood group
    blood_group_filter = request.GET.get('blood_group', '')
    if blood_group_filter:
        donors = donors.filter(blood_group=blood_group_filter)

    # Filter by location
    city_filter = request.GET.get('city', '')
    if city_filter:
        donors = donors.filter(city__icontains=city_filter)

    state_filter = request.GET.get('state', '')
    if state_filter:
        donors = donors.filter(state__icontains=state_filter)

    country_filter = request.GET.get('country', '')
    if country_filter:
        donors = donors.filter(country__icontains=country_filter)

    # Get unique cities and states for filter dropdowns
    cities = Donor.objects.exclude(city='').values_list('city', flat=True).distinct().order_by('city')
    states = Donor.objects.exclude(state='').values_list('state', flat=True).distinct().order_by('state')
    countries = Donor.objects.exclude(country='').values_list('country', flat=True).distinct().order_by('country')

    context = {
        'donors': donors,
        'search_query': search_query,
        'blood_group_filter': blood_group_filter,
        'city_filter': city_filter,
        'state_filter': state_filter,
        'country_filter': country_filter,
        'blood_groups': Donor.BLOOD_GROUPS,
        'cities': cities,
        'states': states,
        'countries': countries,
    }
    return render(request, 'admin_panel/manage_donors.html', context)

@login_required
@user_passes_test(is_admin)
def location_search(request):
    """Location-based donor search with distance calculations"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))
            max_distance = float(data.get('max_distance', 50))  # Default 50km
            blood_group = data.get('blood_group', '')

            # Get donors with coordinates
            donors_with_coords = Donor.objects.filter(
                latitude__isnull=False,
                longitude__isnull=False
            ).select_related('user')

            # Filter by blood group if specified
            if blood_group:
                donors_with_coords = donors_with_coords.filter(blood_group=blood_group)

            # Calculate distances and filter
            nearby_donors = []
            for donor in donors_with_coords:
                distance = donor.distance_to(latitude, longitude)
                if distance is not None and distance <= max_distance:
                    nearby_donors.append({
                        'id': donor.id,
                        'name': donor.name,
                        'blood_group': donor.blood_group,
                        'phone_number': donor.phone_number,
                        'full_location': donor.full_location,
                        'distance': distance,
                        'is_eligible': donor.is_eligible,
                        'can_donate': donor.can_donate(),
                    })

            # Sort by distance
            nearby_donors.sort(key=lambda x: x['distance'])

            return JsonResponse({
                'success': True,
                'donors': nearby_donors,
                'total_found': len(nearby_donors)
            })

        except (ValueError, KeyError, json.JSONDecodeError) as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid request data: {str(e)}'
            })

    # GET request - show the search form
    context = {
        'blood_groups': Donor.BLOOD_GROUPS,
    }
    return render(request, 'admin_panel/location_search.html', context)

@login_required
@user_passes_test(is_admin)
def geocode_address(request):
    """API endpoint to convert address to coordinates"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            address = data.get('address', '').strip()
            country = data.get('country', 'Nepal').strip()

            if not address:
                return JsonResponse({
                    'success': False,
                    'error': 'Address is required'
                })

            result = geocoding_service.geocode(address, country)

            if result:
                return JsonResponse({
                    'success': True,
                    'latitude': result['lat'],
                    'longitude': result['lng'],
                    'display_name': result['display_name'],
                    'address_details': result['address_details']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Could not find location for "{address}"'
                })

        except (ValueError, KeyError, json.JSONDecodeError) as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid request: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'error': 'Only POST method allowed'
    })

@login_required
@user_passes_test(is_admin)
def address_suggestions(request):
    """API endpoint to get address suggestions for autocomplete"""
    query = request.GET.get('q', '').strip()
    country = request.GET.get('country', 'Nepal').strip()

    if len(query) < 3:
        return JsonResponse({
            'success': True,
            'suggestions': []
        })

    try:
        suggestions = geocoding_service.search_suggestions(query, country, limit=8)

        # Format suggestions for frontend
        formatted_suggestions = []
        for suggestion in suggestions:
            formatted_suggestions.append({
                'display_name': suggestion['display_name'],
                'lat': suggestion['lat'],
                'lng': suggestion['lng'],
                'type': suggestion.get('type', ''),
                'importance': suggestion.get('importance', 0)
            })

        return JsonResponse({
            'success': True,
            'suggestions': formatted_suggestions
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error getting suggestions: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
def nepal_location_search(request):
    """Simplified Nepal-only location search"""
    if request.method == 'POST':
        location_name = request.POST.get('location_name', '').strip()
        max_distance = request.POST.get('max_distance', '50')
        blood_group = request.POST.get('blood_group', '')

        try:
            max_distance = float(max_distance)
        except (ValueError, TypeError):
            max_distance = 50.0

        if not location_name:
            messages.error(request, 'Please enter a location name.')
            return redirect('admin_panel:nepal_location_search')

        # Get location coordinates
        location_data = get_nepal_location(location_name)

        if not location_data:
            messages.error(request, f'Could not find location "{location_name}" in Nepal.')
            return redirect('admin_panel:nepal_location_search')

        latitude = location_data['lat']
        longitude = location_data['lng']

        # Get donors with coordinates
        donors_with_coords = Donor.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).select_related('user')

        # Filter by blood group if specified
        if blood_group:
            donors_with_coords = donors_with_coords.filter(blood_group=blood_group)

        # Calculate distances and filter
        nearby_donors = []
        for donor in donors_with_coords:
            distance = donor.distance_to(latitude, longitude)
            if distance is not None and distance <= max_distance:
                nearby_donors.append({
                    'donor': donor,
                    'distance': distance,
                })

        # Sort by distance
        nearby_donors.sort(key=lambda x: x['distance'])

        context = {
            'search_performed': True,
            'location_name': location_name,
            'search_location': location_data,
            'nearby_donors': nearby_donors,
            'total_found': len(nearby_donors),
            'max_distance': max_distance,
            'blood_group': blood_group,
            'blood_groups': Donor.BLOOD_GROUPS,
        }

        return render(request, 'admin_panel/nepal_location_search.html', context)

    # GET request - show the search form
    context = {
        'blood_groups': Donor.BLOOD_GROUPS,
        'search_performed': False,
    }
    return render(request, 'admin_panel/nepal_location_search.html', context)

@login_required
@user_passes_test(is_admin)
def nepal_suggestions(request):
    """Get Nepal location suggestions"""
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'suggestions': []})

    suggestions = get_nepal_suggestions(query)
    return JsonResponse({'suggestions': suggestions})

@login_required
@user_passes_test(is_admin)
def location_search_by_name(request):
    """Enhanced location search that accepts place names"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            location_name = data.get('location_name', '').strip()
            max_distance = float(data.get('max_distance', 50))
            blood_group = data.get('blood_group', '')
            country = data.get('country', 'Nepal')

            if not location_name:
                return JsonResponse({
                    'success': False,
                    'error': 'Location name is required'
                })

            # Geocode the location name
            geocode_result = geocoding_service.geocode(location_name, country)

            if not geocode_result:
                return JsonResponse({
                    'success': False,
                    'error': f'Could not find location "{location_name}"'
                })

            latitude = geocode_result['lat']
            longitude = geocode_result['lng']

            # Get donors with coordinates
            donors_with_coords = Donor.objects.filter(
                latitude__isnull=False,
                longitude__isnull=False
            ).select_related('user')

            # Filter by blood group if specified
            if blood_group:
                donors_with_coords = donors_with_coords.filter(blood_group=blood_group)

            # Calculate distances and filter
            nearby_donors = []
            for donor in donors_with_coords:
                distance = donor.distance_to(latitude, longitude)
                if distance is not None and distance <= max_distance:
                    nearby_donors.append({
                        'id': donor.id,
                        'name': donor.name,
                        'blood_group': donor.blood_group,
                        'phone_number': donor.phone_number,
                        'full_location': donor.full_location,
                        'distance': distance,
                        'is_eligible': donor.is_eligible,
                        'can_donate': donor.can_donate(),
                    })

            # Sort by distance
            nearby_donors.sort(key=lambda x: x['distance'])

            return JsonResponse({
                'success': True,
                'search_location': {
                    'name': location_name,
                    'display_name': geocode_result['display_name'],
                    'latitude': latitude,
                    'longitude': longitude
                },
                'donors': nearby_donors,
                'total_found': len(nearby_donors)
            })

        except (ValueError, KeyError, json.JSONDecodeError) as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid request data: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'error': 'Only POST method allowed'
    })

@login_required
@user_passes_test(is_admin)
def manage_requests(request):
    """Manage donation requests"""
    requests = DonationRequest.objects.select_related('donor__user').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    context = {
        'requests': requests,
        'status_filter': status_filter,
        'status_choices': DonationRequest.STATUS_CHOICES,
    }
    return render(request, 'admin_panel/manage_requests.html', context)

@login_required
@user_passes_test(is_admin)
def approve_request(request, request_id):
    """Approve a donation request"""
    donation_request = get_object_or_404(DonationRequest, id=request_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')
        
        if action == 'approve':
            donation_request.status = 'approved'
            donation_request.admin_notes = admin_notes
            donation_request.save()
            
            # Send approval email
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                
                subject = 'Donation Request Approved - Blood Donation System'
                message = f"""
Dear {donation_request.donor.name},

Your blood donation request has been approved!

Appointment Details:
- Date: {donation_request.requested_date}
- Time: {donation_request.preferred_time}
- Blood Type: {donation_request.donor.blood_group}

{f"Admin Notes: {admin_notes}" if admin_notes else ""}

Please arrive 15 minutes early and bring a valid ID.

Thank you for your commitment to saving lives!

Best regards,
Blood Donation System Team
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [donation_request.donor.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Failed to send approval email: {e}")
            
            messages.success(request, 'Donation request approved successfully!')
            
        elif action == 'reject':
            donation_request.status = 'cancelled'
            donation_request.admin_notes = admin_notes
            donation_request.save()
            messages.success(request, 'Donation request rejected.')
    
    return redirect('admin_panel:manage_requests')

@login_required
@user_passes_test(is_admin)
def manage_emergencies(request):
    """Manage emergency requests"""
    emergencies = EmergencyRequest.objects.order_by('-urgency_level', '-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        emergencies = emergencies.filter(status=status_filter)
    
    context = {
        'emergencies': emergencies,
        'status_filter': status_filter,
        'status_choices': EmergencyRequest.STATUS_CHOICES,
    }
    return render(request, 'admin_panel/manage_emergencies.html', context)

@login_required
@user_passes_test(is_admin)
def reports(request):
    """Generate reports"""
    # Monthly donation statistics
    monthly_stats = []
    for i in range(12):
        month_start = date.today().replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        donations = DonationHistory.objects.filter(
            donation_date__range=[month_start, month_end]
        ).count()
        
        monthly_stats.append({
            'month': month_start.strftime('%B %Y'),
            'donations': donations
        })
    
    monthly_stats.reverse()
    
    # Blood group statistics
    blood_group_stats = []
    for blood_group, _ in Donor.BLOOD_GROUPS:
        donor_count = Donor.objects.filter(blood_group=blood_group).count()
        donation_count = DonationHistory.objects.filter(donor__blood_group=blood_group).count()
        blood_group_stats.append({
            'blood_group': blood_group,
            'donors': donor_count,
            'donations': donation_count,
        })
    
    context = {
        'monthly_stats': monthly_stats,
        'blood_group_stats': blood_group_stats,
    }
    return render(request, 'admin_panel/reports.html', context)

@login_required
@user_passes_test(is_admin)
def manage_inventory(request):
    """Manage blood inventory (simplified)"""
    # For now, show recent donations as inventory
    inventory_data = []
    for blood_group, _ in Donor.BLOOD_GROUPS:
        recent_donations = DonationHistory.objects.filter(
            donor__blood_group=blood_group,
            donation_date__gte=date.today() - timedelta(days=35)
        )
        
        total_units = recent_donations.aggregate(total=Sum('units_donated'))['total'] or 0
        
        inventory_data.append({
            'blood_group': blood_group,
            'units_available': int(total_units),
            'recent_donations': recent_donations.count(),
        })
    
    context = {
        'inventory_data': inventory_data,
    }
    return render(request, 'admin_panel/manage_inventory.html', context)
