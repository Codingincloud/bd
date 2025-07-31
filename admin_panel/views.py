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

    # Get admin notifications
    from utils.notification_service import NotificationService
    admin_notifications = NotificationService.get_system_notifications('admins', user=request.user)[:5]

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
        'admin_notifications': admin_notifications,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def create_emergency_request(request):
    """Create emergency blood request"""
    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        units_needed = request.POST.get('units_needed')
        hospital_name = request.POST.get('hospital_name')
        contact_person = request.POST.get('contact_person')
        contact_phone = request.POST.get('contact_phone')
        urgency_level = request.POST.get('urgency_level', 'high')
        notes = request.POST.get('notes', '')

        if blood_group and units_needed and hospital_name:
            try:
                from donor.models import EmergencyRequest
                emergency_request = EmergencyRequest.objects.create(
                    blood_group=blood_group,
                    units_needed=int(units_needed),
                    hospital_name=hospital_name,
                    contact_person=contact_person,
                    contact_phone=contact_phone,
                    urgency_level=urgency_level,
                    notes=notes,
                    created_by=request.user,
                    status='active'
                )

                # Notify compatible donors
                from utils.notification_service import NotificationService
                NotificationService.notify_emergency_request(emergency_request)

                messages.success(request, f'Emergency request created successfully! Compatible {blood_group} donors have been notified.')
                return redirect('admin_panel:manage_emergencies')

            except Exception as e:
                messages.error(request, f'Error creating emergency request: {e}')
        else:
            messages.error(request, 'Please fill in all required fields.')

    # Get blood group choices
    from donor.models import Donor
    blood_groups = Donor.BLOOD_GROUPS

    context = {
        'blood_groups': blood_groups,
    }
    return render(request, 'admin_panel/create_emergency_request.html', context)

@login_required
@user_passes_test(is_admin)
def approve_donation_request(request, request_id):
    """Approve a donation request"""
    if request.method == 'POST':
        try:
            from donor.models import DonationRequest
            donation_request = get_object_or_404(DonationRequest, id=request_id)

            donation_request.status = 'approved'
            donation_request.approved_by = request.user
            donation_request.approved_at = timezone.now()
            donation_request.save()

            # Notify donor
            from utils.notification_service import NotificationService
            NotificationService.create_user_notification(
                user=donation_request.donor.user,
                title='Donation Request Approved',
                message=f'Your donation request for {donation_request.requested_date} has been approved. Please arrive on time.',
                notification_type='request_approved'
            )

            messages.success(request, f'Donation request approved for {donation_request.donor.user.get_full_name()}')

        except Exception as e:
            messages.error(request, f'Error approving request: {e}')

    return redirect('admin_panel:manage_requests')

@login_required
@user_passes_test(is_admin)
def reject_donation_request(request, request_id):
    """Reject a donation request"""
    if request.method == 'POST':
        try:
            from donor.models import DonationRequest
            donation_request = get_object_or_404(DonationRequest, id=request_id)

            rejection_reason = request.POST.get('rejection_reason', 'Not specified')

            donation_request.status = 'rejected'
            donation_request.rejection_reason = rejection_reason
            donation_request.rejected_by = request.user
            donation_request.rejected_at = timezone.now()
            donation_request.save()

            # Notify donor
            from utils.notification_service import NotificationService
            NotificationService.create_user_notification(
                user=donation_request.donor.user,
                title='Donation Request Rejected',
                message=f'Your donation request has been rejected. Reason: {rejection_reason}',
                notification_type='request_rejected'
            )

            messages.success(request, f'Donation request rejected for {donation_request.donor.user.get_full_name()}')

        except Exception as e:
            messages.error(request, f'Error rejecting request: {e}')

    return redirect('admin_panel:manage_requests')

@login_required
@user_passes_test(is_admin)
def mark_donation_completed(request, request_id):
    """Mark a donation as completed and create donation history"""
    if request.method == 'POST':
        try:
            from donor.models import DonationRequest, DonationHistory
            donation_request = get_object_or_404(DonationRequest, id=request_id)

            units_collected = request.POST.get('units_collected', '1')
            donation_center = request.POST.get('donation_center', 'Main Center')
            notes = request.POST.get('notes', '')

            # Mark request as completed
            donation_request.status = 'completed'
            donation_request.completed_at = timezone.now()
            donation_request.save()

            # Create donation history record
            DonationHistory.objects.create(
                donor=donation_request.donor,
                donation_date=donation_request.requested_date,
                donation_center=donation_center,
                units_donated=float(units_collected),
                notes=notes,
                related_request=donation_request
            )

            # Update donor's last donation date
            donation_request.donor.last_donation_date = donation_request.requested_date
            donation_request.donor.save()

            # Notify donor
            from utils.notification_service import NotificationService
            NotificationService.create_user_notification(
                user=donation_request.donor.user,
                title='Thank You for Your Donation!',
                message=f'Your blood donation on {donation_request.requested_date} has been recorded. Thank you for saving lives!',
                notification_type='donation_completed'
            )

            messages.success(request, f'Donation marked as completed for {donation_request.donor.user.get_full_name()}')

        except Exception as e:
            messages.error(request, f'Error marking donation as completed: {e}')

    return redirect('admin_panel:manage_requests')

@login_required
@user_passes_test(is_admin)
def manage_blood_centers(request):
    """Manage blood donation centers"""
    from donor.models import DonationCenter

    if request.method == 'POST':
        # Add new blood center
        name = request.POST.get('name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')

        if name and address and city:
            try:
                DonationCenter.objects.create(
                    name=name,
                    address=address,
                    city=city,
                    state=state or 'Nepal',
                    phone_number=phone_number,
                    email=email
                )
                messages.success(request, f'Blood center "{name}" added successfully!')
            except Exception as e:
                messages.error(request, f'Error adding blood center: {e}')
        else:
            messages.error(request, 'Please fill in all required fields.')

    # Get all blood centers
    blood_centers = DonationCenter.objects.all().order_by('name')

    context = {
        'blood_centers': blood_centers,
    }
    return render(request, 'admin_panel/manage_blood_centers.html', context)

@login_required
@user_passes_test(is_admin)
def delete_blood_center(request, center_id):
    """Delete a blood center"""
    if request.method == 'POST':
        try:
            from donor.models import DonationCenter
            center = get_object_or_404(DonationCenter, id=center_id)
            center_name = center.name
            center.delete()
            messages.success(request, f'Blood center "{center_name}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting blood center: {e}')

    return redirect('admin_panel:manage_blood_centers')

@login_required
@user_passes_test(is_admin)
def donor_tracking(request):
    """Track donor locations and activities"""
    from donor.models import Donor
    from django.db.models import Count, Q

    # Get all donors with their latest information
    donors = Donor.objects.select_related('user').annotate(
        total_donations=Count('donationhistory'),
        pending_requests=Count('donationrequest', filter=Q(donationrequest__status='pending')),
        approved_requests=Count('donationrequest', filter=Q(donationrequest__status='approved'))
    ).order_by('-created_at')

    # Filter by search query if provided
    search_query = request.GET.get('search', '')
    if search_query:
        donors = donors.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(blood_group__icontains=search_query) |
            Q(city__icontains=search_query)
        )

    # Filter by blood group if provided
    blood_group_filter = request.GET.get('blood_group', '')
    if blood_group_filter:
        donors = donors.filter(blood_group=blood_group_filter)

    # Filter by eligibility status
    eligibility_filter = request.GET.get('eligibility', '')
    if eligibility_filter == 'eligible':
        # This would need to be implemented with a custom query
        pass
    elif eligibility_filter == 'not_eligible':
        # This would need to be implemented with a custom query
        pass

    # Add eligibility status to each donor
    for donor in donors:
        eligible, message = donor.can_donate()
        donor.eligibility_status = {
            'eligible': eligible,
            'message': message
        }

    context = {
        'donors': donors,
        'search_query': search_query,
        'blood_group_filter': blood_group_filter,
        'eligibility_filter': eligibility_filter,
        'blood_groups': Donor.BLOOD_GROUPS,
        'total_donors': donors.count(),
    }
    return render(request, 'admin_panel/donor_tracking.html', context)

@login_required
@user_passes_test(is_admin)
def manage_donors(request):
    """Manage donors with enhanced location-based search"""
    donors = Donor.objects.select_related('user').order_by('-created_at')

    # Enhanced search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        # Split search query into terms for better matching
        search_terms = search_query.split()
        search_filter = Q()

        for term in search_terms:
            term_filter = (
                Q(user__first_name__icontains=term) |
                Q(user__last_name__icontains=term) |
                Q(user__username__icontains=term) |
                Q(user__email__icontains=term) |
                Q(phone_number__icontains=term) |
                Q(blood_group__icontains=term) |
                Q(address__icontains=term) |
                Q(city__icontains=term) |
                Q(state__icontains=term) |
                Q(country__icontains=term) |
                Q(emergency_contact_name__icontains=term) |
                Q(emergency_contact_phone__icontains=term) |
                Q(medical_conditions__icontains=term)
            )
            search_filter &= term_filter

        donors = donors.filter(search_filter)

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

    # Filter by eligibility
    eligibility_filter = request.GET.get('eligibility', '')
    if eligibility_filter:
        if eligibility_filter == 'eligible':
            donors = donors.filter(is_eligible=True)
        elif eligibility_filter == 'not_eligible':
            donors = donors.filter(is_eligible=False)

    # Filter by gender
    gender_filter = request.GET.get('gender', '')
    if gender_filter:
        donors = donors.filter(gender=gender_filter)

    # Filter by age range
    age_min = request.GET.get('age_min', '')
    age_max = request.GET.get('age_max', '')
    if age_min:
        try:
            age_min_int = int(age_min)
            donors = donors.extra(
                where=["EXTRACT(year FROM age(date_of_birth)) >= %s"],
                params=[age_min_int]
            )
        except ValueError:
            pass
    if age_max:
        try:
            age_max_int = int(age_max)
            donors = donors.extra(
                where=["EXTRACT(year FROM age(date_of_birth)) <= %s"],
                params=[age_max_int]
            )
        except ValueError:
            pass

    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'name':
        donors = donors.order_by('user__first_name', 'user__last_name')
    elif sort_by == 'blood_group':
        donors = donors.order_by('blood_group')
    elif sort_by == 'age':
        donors = donors.order_by('date_of_birth')
    elif sort_by == 'city':
        donors = donors.order_by('city')
    elif sort_by == 'created':
        donors = donors.order_by('-created_at')

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(donors, 25)  # Show 25 donors per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get unique values for filter dropdowns
    cities = Donor.objects.exclude(city='').values_list('city', flat=True).distinct().order_by('city')
    states = Donor.objects.exclude(state='').values_list('state', flat=True).distinct().order_by('state')
    countries = Donor.objects.exclude(country='').values_list('country', flat=True).distinct().order_by('country')

    # Statistics for current filter
    total_filtered = donors.count()
    blood_group_stats = donors.values('blood_group').annotate(
        count=Count('id')
    ).order_by('blood_group')

    context = {
        'page_obj': page_obj,
        'donors': donors,
        'search_query': search_query,
        'blood_group_filter': blood_group_filter,
        'city_filter': city_filter,
        'state_filter': state_filter,
        'country_filter': country_filter,
        'eligibility_filter': eligibility_filter,
        'gender_filter': gender_filter,
        'age_min': age_min,
        'age_max': age_max,
        'sort_by': sort_by,
        'blood_groups': Donor.BLOOD_GROUPS,
        'gender_choices': Donor.GENDER_CHOICES,
        'cities': cities,
        'states': states,
        'countries': countries,
        'total_filtered': total_filtered,
        'blood_group_stats': blood_group_stats,
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
    """Manage blood inventory with update capabilities"""
    from donor.models import BloodInventory

    if request.method == 'POST':
        # Handle inventory updates
        blood_group = request.POST.get('blood_group')
        action = request.POST.get('action')
        units = request.POST.get('units', 0)
        notes = request.POST.get('notes', '')

        try:
            units = float(units)
            inventory, _ = BloodInventory.objects.get_or_create(
                blood_group=blood_group,
                defaults={'units_available': 0}
            )

            if action == 'add':
                inventory.units_available += units
                inventory.notes = f"Added {units} units. {notes}"
                messages.success(request, f'Added {units} units of {blood_group} blood.')
            elif action == 'remove':
                if inventory.units_available >= units:
                    inventory.units_available -= units
                    inventory.notes = f"Removed {units} units. {notes}"
                    messages.success(request, f'Removed {units} units of {blood_group} blood.')
                else:
                    messages.error(request, f'Cannot remove {units} units. Only {inventory.units_available} units available.')
                    return redirect('admin_panel:manage_inventory')
            elif action == 'set':
                inventory.units_available = units
                inventory.notes = f"Set to {units} units. {notes}"
                messages.success(request, f'Set {blood_group} blood inventory to {units} units.')

            inventory.last_updated = timezone.now()
            inventory.updated_by = request.user
            inventory.save()

        except ValueError:
            messages.error(request, 'Please enter a valid number for units.')
        except Exception as e:
            messages.error(request, f'Error updating inventory: {e}')

        return redirect('admin_panel:manage_inventory')

    # Get current inventory
    inventory_data = []
    for blood_group, blood_group_display in Donor.BLOOD_GROUPS:
        try:
            inventory = BloodInventory.objects.get(blood_group=blood_group)
            units_available = inventory.units_available
            last_updated = inventory.last_updated
            notes = inventory.notes
        except BloodInventory.DoesNotExist:
            units_available = 0
            last_updated = None
            notes = 'No inventory record'

        # Get recent donations for this blood group
        recent_donations = DonationHistory.objects.filter(
            donor__blood_group=blood_group,
            donation_date__gte=date.today() - timedelta(days=35)
        ).count()

        # Determine status based on units available
        if units_available <= 0:
            status = 'critical'
        elif units_available <= 5:
            status = 'low'
        elif units_available <= 15:
            status = 'medium'
        else:
            status = 'good'

        inventory_data.append({
            'blood_group': blood_group,
            'blood_group_display': blood_group_display,
            'units_available': units_available,
            'recent_donations': recent_donations,
            'last_updated': last_updated,
            'notes': notes,
            'status': status,
        })

    context = {
        'inventory_data': inventory_data,
        'blood_groups': Donor.BLOOD_GROUPS,
    }
    return render(request, 'admin_panel/manage_inventory.html', context)
