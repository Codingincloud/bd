# Import Django basic modules - learned from tutorial
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta, date, datetime
import json
import csv

# Import my app models
from donor.models import Donor, DonationRequest, DonationHistory, EmergencyRequest, Hospital
from admin_panel.models import AdminProfile
from utils.notification_service import NotificationService

@login_required
def dashboard(request):
    # Check if user is admin - simple check
    if not request.user.is_staff:
        messages.error(request, 'You must be an admin to access this page.')
        return redirect('donor:donor_dashboard')
    
    # Redirect superadmin to dedicated dashboard
    if request.user.is_superuser:
        return redirect('admin_panel:superadmin_dashboard')
    
    # Count total donors in database
    total_donors = Donor.objects.count()
    
    # Count total donations
    total_donations = DonationHistory.objects.count()
    
    # Count pending donation requests
    pending_requests = DonationRequest.objects.filter(status='pending').count()
    
    # Count active emergency requests
    active_emergencies = EmergencyRequest.objects.filter(status='active').count()
    
    # Get today's date
    today = date.today()
    
    # Filter donations made today
    today_donations = DonationHistory.objects.filter(donation_date=today).count()
    
    # Filter requests created today
    today_requests = DonationRequest.objects.filter(created_at__date=today).count()
    
    # Calculate first day of current month
    month_start = today.replace(day=1)
    
    # Count donations this month
    month_donations = DonationHistory.objects.filter(donation_date__gte=month_start).count()
    
    # Count new donors this month
    month_new_donors = Donor.objects.filter(user__date_joined__date__gte=month_start).count()
    
    # Create dictionary to store blood inventory
    from donor.models import BloodInventory, Hospital
    blood_inventory = {}
    
    # List of all blood groups
    blood_groups_list = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    
    # Get admin's hospital if they have one
    try:
        admin_hospital = request.user.hospital
    except:
        admin_hospital = None
    
    # Loop through each blood group and get inventory for admin's hospital
    for blood_group in blood_groups_list:
        if admin_hospital:
            try:
                # Get inventory for admin's specific hospital
                inventory = BloodInventory.objects.get(
                    blood_group=blood_group,
                    hospital=admin_hospital
                )
                blood_inventory[blood_group] = int(inventory.units_available)
            except BloodInventory.DoesNotExist:
                # If not found, create new record for this hospital
                BloodInventory.objects.create(
                    blood_group=blood_group,
                    hospital=admin_hospital,
                    units_available=0,
                    units_reserved=0,
                    updated_by=request.user,
                    notes='Created from dashboard'
                )
                blood_inventory[blood_group] = 0
        else:
            # Sum up inventory across all hospitals for system-wide view
            total_units = BloodInventory.objects.filter(
                blood_group=blood_group
            ).aggregate(total=Sum('units_available'))['total'] or 0
            blood_inventory[blood_group] = int(total_units)
    
    # Get recent donations (last 5)
    recent_donations = DonationHistory.objects.all().order_by('-created_at')[:5]
    
    # Get recent requests (last 5)
    recent_requests = DonationRequest.objects.all().order_by('-created_at')[:5]
    
    # Get pending approvals (maximum 10)
    pending_approvals = DonationRequest.objects.filter(status='pending').order_by('requested_date')[:10]
    
    # Get urgent emergency requests
    urgent_emergencies = EmergencyRequest.objects.filter(
        status='active',
        urgency_level='high'
    ).order_by('required_by')[:5]
    
    # Create list to store blood group statistics
    blood_group_stats = []
    for blood_group in blood_groups_list:
        # Count donors for this blood group
        donor_count = Donor.objects.filter(blood_group=blood_group).count()
        
        # Count donations for this blood group
        donation_count = DonationHistory.objects.filter(donor__blood_group=blood_group).count()
        
        # Add to statistics list
        blood_group_stats.append({
            'blood_group': blood_group,
            'donors': donor_count,
            'donations': donation_count,
            'inventory': blood_inventory.get(blood_group, 0)
        })
    
    # Get admin notifications
    admin_notifications = NotificationService.get_system_notifications('admins', user=request.user)[:5]

    # Calculate active donors (donated in last 90 days)
    ninety_days_ago = today - timedelta(days=90)
    active_donors = Donor.objects.filter(last_donation_date__gte=ninety_days_ago).count()

    # Add pending users count for superadmin
    pending_users_count = 0
    if request.user.is_superuser:
        from django.contrib.auth.models import User
        pending_users_count = User.objects.filter(is_staff=True, is_active=False).count()

    # Create context dictionary with all data for template
    context = {
        'total_donors': total_donors,
        'active_donors': active_donors,
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
        'admin_notifications': admin_notifications,
        'pending_users_count': pending_users_count,
    }
    
    # Render template with context data
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
def create_emergency_request(request):
    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, 'Only admins can create emergency requests.')
        return redirect('donor:donor_dashboard')
    
    # Check if admin has a hospital
    try:
        admin_hospital = request.user.hospital
    except:
        messages.error(request, 'You must have a hospital assigned to create emergency requests.')
        return redirect('admin_panel:dashboard')
    
    # Handle form submission
    if request.method == 'POST':
        # Get form data from POST request
        blood_group = request.POST.get('blood_group')
        units_needed = request.POST.get('units_needed')
        contact_person = request.POST.get('contact_person')
        contact_phone = request.POST.get('contact_phone')
        urgency_level = request.POST.get('urgency_level', 'high')
        required_by = request.POST.get('required_by')
        notes = request.POST.get('notes', '')

        # Simple validation
        if not blood_group:
            messages.error(request, 'Blood group is required')
        elif not units_needed:
            messages.error(request, 'Units needed is required')
        elif not contact_person:
            messages.error(request, 'Contact person is required')
        elif not contact_phone:
            messages.error(request, 'Contact phone is required')
        elif not required_by:
            messages.error(request, 'Required by date/time is required')
        else:
            # All validations passed, create emergency request for admin's hospital
            try:
                from datetime import datetime
                from django.utils import timezone as tz
                
                # Convert string to datetime
                required_by_dt = datetime.strptime(required_by, '%Y-%m-%dT%H:%M')
                required_by_dt = tz.make_aware(required_by_dt)
                
                # Create new emergency request in database for this hospital only
                emergency_request = EmergencyRequest.objects.create(
                    hospital=admin_hospital,
                    blood_group_needed=blood_group,
                    units_needed=int(units_needed),
                    hospital_name=admin_hospital.name,
                    contact_person=contact_person,
                    contact_phone=contact_phone,
                    location=f"{admin_hospital.address}, {admin_hospital.city}",
                    urgency_level=urgency_level,
                    required_by=required_by_dt,
                    notes=notes,
                    status='active'
                )

                # Send notification to compatible donors
                try:
                    NotificationService.notify_emergency_request(emergency_request)
                    messages.success(request, f'Emergency request created for {admin_hospital.name}! {blood_group} donors notified.')
                except:
                    messages.warning(request, 'Emergency created but notification failed.')

                return redirect('admin_panel:manage_emergencies')
            except Exception as e:
                messages.error(request, f'Error creating request: {e}')
    
    # For GET request, show form with pre-filled hospital info
    blood_groups_list = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    context = {
        'blood_groups': blood_groups_list,
        'hospital': admin_hospital,
    }
    return render(request, 'admin_panel/create_emergency_request.html', context)


@login_required
def approve_donation_request(request, request_id):
    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, 'Only admins can approve requests.')
        return redirect('donor:donor_dashboard')
    
    if request.method == 'POST':
        # Get the donation request from database
        donation_request = get_object_or_404(DonationRequest, id=request_id)

        # Get custom message from form
        custom_message = request.POST.get('approval_message', '').strip()

        # If no message provided, use default
        if not custom_message:
            custom_message = f'Your donation request for {donation_request.requested_date} has been approved.'

        # Update request status
        donation_request.status = 'approved'
        donation_request.save()

        # Send notification to donor
        NotificationService.create_user_notification(
            user=donation_request.donor.user,
            title='Donation Request Approved ✅',
            message=custom_message,
            notification_type='request_approved',
            action_url='/donor/dashboard/'
        )

        messages.success(request, f'Request approved for {donation_request.donor.user.get_full_name()}')

    return redirect('admin_panel:manage_requests')


@login_required
def reject_donation_request(request, request_id):
    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, 'Only admins can reject requests.')
        return redirect('donor:donor_dashboard')
    
    if request.method == 'POST':
        # Get the donation request
        donation_request = get_object_or_404(DonationRequest, id=request_id)

        # Get rejection reason
        rejection_reason = request.POST.get('rejection_reason', 'Not specified')

        # Update status
        donation_request.status = 'rejected'
        donation_request.rejection_reason = rejection_reason
        donation_request.save()

        # Notify donor
        NotificationService.create_user_notification(
            user=donation_request.donor.user,
            title='Donation Request Rejected',
            message=f'Your donation request has been rejected. Reason: {rejection_reason}',
            notification_type='request_rejected'
        )

        messages.success(request, f'Request rejected for {donation_request.donor.user.get_full_name()}')

    return redirect('admin_panel:manage_requests')

@login_required

def mark_donation_completed(request, request_id):
    """Mark a donation as completed and create donation history"""
    if request.method == 'POST':
        try:
            from donor.models import DonationRequest, DonationHistory
            donation_request = get_object_or_404(DonationRequest, id=request_id)

            units_collected = request.POST.get('units_collected', '1')
            donation_center_name = request.POST.get('donation_center_name', 'Main Center')
            notes = request.POST.get('notes', '')

            # Mark request as completed
            donation_request.status = 'completed'
            donation_request.completed_at = timezone.now()
            donation_request.save()

            # Create donation history record
            DonationHistory.objects.create(
                donor=donation_request.donor,
                donation_date=donation_request.requested_date,
                donation_center_name=donation_center_name,
                units_donated=float(units_collected),
                notes=notes
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
def my_hospital(request):
    """View and edit hospital details"""
    from donor.models import Hospital

    try:
        hospital = request.user.hospital
    except Hospital.DoesNotExist:
        messages.error(request, 'Hospital not found for your account. Please contact support.')
        return redirect('admin_panel:dashboard')

    if request.method == 'POST':
        # Update hospital details
        hospital.name = request.POST.get('name', hospital.name)
        hospital.phone_number = request.POST.get('phone_number', hospital.phone_number)
        hospital.email = request.POST.get('email', hospital.email)
        hospital.address = request.POST.get('address', hospital.address)
        hospital.city = request.POST.get('city', hospital.city)
        hospital.state = request.POST.get('state', hospital.state)
        hospital.hospital_type = request.POST.get('hospital_type', hospital.hospital_type)
        hospital.operating_hours = request.POST.get('operating_hours', hospital.operating_hours)
        hospital.emergency_contact = request.POST.get('emergency_contact', hospital.emergency_contact)
        hospital.services = request.POST.get('services', hospital.services)
        
        try:
            hospital.save()
            messages.success(request, 'Hospital details updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating hospital: {e}')

        return redirect('admin_panel:my_hospital')

    context = {
        'hospital': hospital,
    }
    return render(request, 'admin_panel/my_hospital.html', context)

@login_required
def donor_tracking(request):
    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, 'Only admins can view donor tracking.')
        return redirect('donor:donor_dashboard')
    
    # Get all donors from database
    donors = Donor.objects.all().order_by('-user__date_joined')

    # Check if there's a search query
    search_query = request.GET.get('search', '')
    if search_query:
        # Filter donors by search term
        donors = donors.filter(user__first_name__icontains=search_query) | \
                 donors.filter(user__last_name__icontains=search_query) | \
                 donors.filter(user__email__icontains=search_query) | \
                 donors.filter(blood_group__icontains=search_query) | \
                 donors.filter(city__icontains=search_query) | \
                 donors.filter(phone_number__icontains=search_query)

    # Check for blood group filter
    blood_group_filter = request.GET.get('blood_group', '')
    if blood_group_filter:
        donors = donors.filter(blood_group=blood_group_filter)

    # Check for city filter
    city_filter = request.GET.get('city', '')
    if city_filter:
        donors = donors.filter(city__icontains=city_filter)

    # Check for status filter
    status_filter = request.GET.get('status', '')
    if status_filter == 'eligible':
        # Show only donors who can donate (90 days since last donation)
        ninety_days_ago = date.today() - timedelta(days=90)
        donors = donors.filter(last_donation_date__lte=ninety_days_ago) | donors.filter(last_donation_date__isnull=True)
    elif status_filter == 'not_eligible':
        # Show only donors who cannot donate yet
        ninety_days_ago = date.today() - timedelta(days=90)
        donors = donors.filter(last_donation_date__gt=ninety_days_ago)

    # Check eligibility for each donor
    for donor in donors:
        donor.is_eligible, _ = donor.can_donate()

    # Pagination - show 20 donors per page
    from django.core.paginator import Paginator
    paginator = Paginator(donors, 20)
    page_number = request.GET.get('page')
    donors = paginator.get_page(page_number)

    # Calculate statistics for dashboard
    total_donors = Donor.objects.count()
    
    ninety_days_ago = date.today() - timedelta(days=90)
    active_donors = Donor.objects.filter(last_donation_date__gte=ninety_days_ago).count()
    
    eligible_donors = Donor.objects.filter(last_donation_date__lte=ninety_days_ago).count()
    
    this_month_start = date.today().replace(day=1)
    recent_donors = Donor.objects.filter(user__date_joined__date__gte=this_month_start).count()

    # Create context for template
    blood_groups_list = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    context = {
        'donors': donors,
        'total_donors': total_donors,
        'active_donors': active_donors,
        'eligible_donors': eligible_donors,
        'recent_donors': recent_donors,
        'blood_groups': blood_groups_list,
    }
    return render(request, 'admin_panel/donor_tracking.html', context)

@login_required

def donor_detail(request, donor_id):
    """View detailed information about a specific donor"""
    donor = get_object_or_404(Donor, id=donor_id)

    # Get donation history
    donation_history = DonationHistory.objects.filter(donor=donor).order_by('-donation_date')[:10]

    # Get donation requests
    donation_requests = DonationRequest.objects.filter(donor=donor).order_by('-created_at')[:10]

    # Get emergency requests the donor is compatible with
    compatible_groups = donor.compatible_blood_groups
    emergency_requests = EmergencyRequest.objects.filter(
        blood_group_needed__in=compatible_groups,
        status='active'
    ).order_by('-urgency_level', '-created_at')[:5]

    # Check eligibility
    can_donate, eligibility_message = donor.can_donate()

    context = {
        'donor': donor,
        'donation_history': donation_history,
        'donation_requests': donation_requests,
        'emergency_requests': emergency_requests,
        'can_donate': can_donate,
        'eligibility_message': eligibility_message,
        'compatible_groups': compatible_groups,
    }
    return render(request, 'admin_panel/donor_detail.html', context)


@login_required

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

def manage_requests(request):
    """Manage donation requests"""
    donation_requests = DonationRequest.objects.select_related('donor__user').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        donation_requests = donation_requests.filter(status=status_filter)
    
    # Calculate statistics
    total_requests = donation_requests.count()
    pending_requests = donation_requests.filter(status='pending').count()
    approved_requests = donation_requests.filter(status='approved').count()
    rejected_requests = donation_requests.filter(status='rejected').count()
    completed_requests = donation_requests.filter(status='completed').count()
    cancelled_requests = donation_requests.filter(status='cancelled').count()
    
    context = {
        'donation_requests': donation_requests,
        'status_filter': status_filter,
        'status_choices': DonationRequest.STATUS_CHOICES,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'completed_requests': completed_requests,
        'cancelled_requests': cancelled_requests,
    }
    return render(request, 'admin_panel/manage_requests.html', context)

@login_required

def complete_donation_request(request, request_id):
    """Mark a donation request as completed"""
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('admin_panel:manage_requests')
    
    try:
        donation_request = get_object_or_404(DonationRequest, id=request_id)
        
        # Only approved requests can be completed
        if donation_request.status != 'approved':
            messages.error(request, f'Cannot complete a {donation_request.status} request. Only approved requests can be completed.')
            return redirect('admin_panel:manage_requests')
        
        # Mark as completed
        donation_request.status = 'completed'
        donation_request.completed_at = timezone.now()
        donation_request.save()
        
        # Update donor's last donation date
        donor = donation_request.donor
        donor.last_donation_date = donation_request.requested_date
        donor.save()
        
        # Create donation history record
        try:
            history = DonationHistory.objects.create(
                donor=donor,
                donation_date=donation_request.requested_date,
                donation_center_name=f"Scheduled Appointment at {donation_request.preferred_time}",
                units_donated=1,
                notes=f"Completed from request #{donation_request.id}. Appointment was scheduled and confirmed."
            )
            print(f"✓ DonationHistory created successfully: {history.id}")
        except Exception as hist_error:
            print(f"✗ ERROR creating DonationHistory: {hist_error}")
            import traceback
            traceback.print_exc()
            messages.warning(request, f'Donation marked as completed but history record failed: {str(hist_error)}')
        
        # Notify donor
        try:
            NotificationService.create_notification(
                user=donor.user,
                title='Donation Completed',
                message=f'Your blood donation scheduled for {donation_request.requested_date} has been successfully completed. Thank you for saving lives!',
                notification_type='success',
                related_object=donation_request
            )
        except Exception as e:
            print(f"Error creating notification: {e}")
        
        messages.success(request, f'Donation request for {donor.name} has been marked as completed and added to donation history.')
        return redirect('admin_panel:manage_requests')
        
    except Exception as e:
        messages.error(request, f'Error completing donation request: {str(e)}')
        return redirect('admin_panel:manage_requests')

@login_required

def cancel_donation_request(request, request_id):
    """Cancel a donation request"""
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('admin_panel:manage_requests')
    
    try:
        donation_request = get_object_or_404(DonationRequest, id=request_id)
        
        # Can only cancel pending or approved requests
        if donation_request.status not in ['pending', 'approved']:
            messages.error(request, f'Cannot cancel a {donation_request.status} request.')
            return redirect('admin_panel:manage_requests')
        
        old_status = donation_request.status
        donation_request.status = 'cancelled'
        donation_request.admin_notes = request.POST.get('reason', 'Cancelled by admin')
        donation_request.save()
        
        # Notify donor
        try:
            NotificationService.create_notification(
                user=donation_request.donor.user,
                title='Donation Cancelled',
                message=f'Your blood donation scheduled for {donation_request.requested_date} has been cancelled. Reason: {donation_request.admin_notes}',
                notification_type='warning',
                related_object=donation_request
            )
        except Exception as e:
            print(f"Error creating notification: {e}")
        
        messages.warning(request, f'Donation request for {donation_request.donor.name} has been cancelled.')
        return redirect('admin_panel:manage_requests')
        
    except Exception as e:
        messages.error(request, f'Error cancelling donation request: {str(e)}')
        return redirect('admin_panel:manage_requests')

@login_required

def manage_emergencies(request):
    """Manage emergency requests - collaborative system where all hospitals can see and help each other"""
    # Get admin's hospital for tracking who helps
    admin_hospital = request.user.hospital
    
    # All hospitals see all emergencies (collaborative system)
    emergencies = EmergencyRequest.objects.select_related('hospital').prefetch_related('responses__donor').order_by('-urgency_level', '-created_at')
    
    # Add flag to identify own vs other hospital emergencies
    for emergency in emergencies:
        emergency.is_own_hospital = (emergency.hospital == admin_hospital)
    
    # Emergency response is handled by separate view functions: resolve_emergency
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        emergencies = emergencies.filter(status=status_filter)
    
    # Get all emergencies for different tabs (respecting hospital filter)
    all_emergencies = emergencies.order_by('-urgency_level', '-created_at')
    active_emergencies_list = all_emergencies.filter(status='active')
    fulfilled_emergencies_list = all_emergencies.filter(status='fulfilled')
    expired_emergencies_list = all_emergencies.filter(status='expired')
    
    # Calculate statistics - using only valid EmergencyRequest.STATUS_CHOICES
    total_emergencies = emergencies.count()
    active_emergencies = active_emergencies_list.count()
    fulfilled_emergencies = fulfilled_emergencies_list.count()
    expired_emergencies = expired_emergencies_list.count()
    
    # Count by urgency level (only for active emergencies)
    critical_emergencies = active_emergencies_list.filter(urgency_level='critical').count()
    high_emergencies = active_emergencies_list.filter(urgency_level='high').count()
    medium_emergencies = active_emergencies_list.filter(urgency_level='medium').count()
    
    context = {
        'emergencies': emergencies,
        'status_filter': status_filter,
        'status_choices': EmergencyRequest.STATUS_CHOICES,
        'total_emergencies': total_emergencies,
        'active_emergencies': active_emergencies,
        'fulfilled_emergencies': fulfilled_emergencies,
        'expired_emergencies': expired_emergencies,
        'critical_emergencies': critical_emergencies,
        'high_emergencies': high_emergencies,
        'medium_emergencies': medium_emergencies,
    }
    return render(request, 'admin_panel/manage_emergencies.html', context)


@login_required

def edit_admin_profile(request):
    """Edit admin profile information"""
    try:
        admin_profile = request.user.adminprofile
    except AdminProfile.DoesNotExist:
        messages.error(request, 'Admin profile not found. Please contact support.')
        return redirect('admin_panel:dashboard')
    
    if request.method == 'POST':
        try:
            # Update user information
            user = admin_profile.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            
            # Update admin profile information
            admin_profile.name = request.POST.get('name', '')
            admin_profile.contact_no = request.POST.get('contact_no', '')
            admin_profile.address = request.POST.get('address', '')
            admin_profile.email = request.POST.get('email', '')
            
            # Update location information
            admin_profile.city = request.POST.get('city', '')
            admin_profile.state = request.POST.get('state', '')
            admin_profile.postal_code = request.POST.get('postal_code', '')
            admin_profile.country = request.POST.get('country', 'Nepal')
            
            # Update coordinates if provided
            latitude = request.POST.get('latitude', '')
            longitude = request.POST.get('longitude', '')
            if latitude and longitude:
                try:
                    admin_profile.latitude = float(latitude)
                    admin_profile.longitude = float(longitude)
                except ValueError:
                    pass  # Keep existing coordinates if invalid
            
            admin_profile.save()
            messages.success(request, 'Admin profile updated successfully!')
            return redirect('admin_panel:edit_admin_profile')
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    context = {
        'admin_profile': admin_profile,
    }
    return render(request, 'admin_panel/edit_admin_profile.html', context)

@login_required

def admin_profile(request):
    """View admin profile information"""
    try:
        admin_profile = request.user.adminprofile
    except AdminProfile.DoesNotExist:
        messages.error(request, 'Admin profile not found. Please contact support.')
        return redirect('admin_panel:dashboard')
    
    # Get admin statistics
    total_donors = Donor.objects.count()
    total_donations = DonationHistory.objects.count()
    pending_requests = DonationRequest.objects.filter(status='pending').count()
    active_emergencies = EmergencyRequest.objects.filter(status='active').count()
    
    # Get recent activities
    recent_donations = DonationHistory.objects.select_related('donor__user').order_by('-created_at')[:5]
    recent_requests = DonationRequest.objects.select_related('donor__user').order_by('-created_at')[:5]
    
    context = {
        'admin_profile': admin_profile,
        'total_donors': total_donors,
        'total_donations': total_donations,
        'pending_requests': pending_requests,
        'active_emergencies': active_emergencies,
        'recent_donations': recent_donations,
        'recent_requests': recent_requests,
    }
    return render(request, 'admin_panel/admin_profile.html', context)

@login_required

def manage_inventory(request):
    """Manage blood inventory with update capabilities"""
    from donor.models import BloodInventory, Hospital

    # Get admin's hospital
    try:
        hospital = request.user.hospital
    except Hospital.DoesNotExist:
        messages.error(request, 'Hospital not found for your account.')
        return redirect('admin_panel:dashboard')

    if request.method == 'POST':
        # Handle inventory updates
        blood_group = request.POST.get('blood_group')
        action = request.POST.get('action')
        units = request.POST.get('units', 0)
        notes = request.POST.get('notes', '')

        try:
            units = float(units)
            inventory, _ = BloodInventory.objects.get_or_create(
                hospital=hospital,
                blood_group=blood_group,
                defaults={'units_available': 0, 'units_reserved': 0}
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

    # Get current inventory for this hospital
    inventory_data = []
    for blood_group, blood_group_display in Donor.BLOOD_GROUPS:
        try:
            inventory = BloodInventory.objects.get(hospital=hospital, blood_group=blood_group)
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

    # Calculate summary statistics
    total_units = sum(item['units_available'] for item in inventory_data)
    critical_groups = sum(1 for item in inventory_data if item['status'] == 'critical')
    low_groups = sum(1 for item in inventory_data if item['status'] == 'low')
    adequate_groups = sum(1 for item in inventory_data if item['status'] in ['medium', 'good'])
    
    # Critical alerts
    critical_alerts = [item for item in inventory_data if item['status'] == 'critical']

    context = {
        'inventory_data': inventory_data,
        'blood_groups': Donor.BLOOD_GROUPS,
        'total_units': total_units,
        'critical_groups': critical_groups,
        'low_groups': low_groups,
        'adequate_groups': adequate_groups,
        'critical_alerts': critical_alerts,
    }
    return render(request, 'admin_panel/manage_inventory.html', context)


@login_required

def change_password(request):
    """Change admin password"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('admin_panel:edit_admin_profile')
        
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return redirect('admin_panel:edit_admin_profile')
        
        if len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('admin_panel:edit_admin_profile')
        
        request.user.set_password(new_password1)
        request.user.save()
        messages.success(request, 'Password changed successfully!')
        return redirect('admin_panel:admin_profile')
    
    return redirect('admin_panel:edit_admin_profile')


@login_required

def edit_donor(request, donor_id):
    """Edit donor profile"""
    donor = get_object_or_404(Donor, id=donor_id)
    
    if request.method == 'POST':
        # Update donor information
        donor.blood_group = request.POST.get('blood_group', donor.blood_group)
        donor.phone_number = request.POST.get('phone_number', donor.phone_number)
        donor.address = request.POST.get('address', donor.address)
        donor.city = request.POST.get('city', donor.city)
        donor.state = request.POST.get('state', donor.state)
        donor.weight = request.POST.get('weight', donor.weight)
        donor.height = request.POST.get('height', donor.height)
        donor.is_eligible = request.POST.get('is_eligible') == 'on'
        donor.medical_conditions = request.POST.get('medical_conditions', donor.medical_conditions)
        
        # Update user information
        user = donor.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        
        try:
            donor.save()
            user.save()
            messages.success(request, f'Donor {donor.name} updated successfully.')
            return redirect('admin_panel:donor_detail', donor_id=donor.id)
        except Exception as e:
            messages.error(request, f'Error updating donor: {str(e)}')
    
    context = {
        'donor': donor,
        'blood_groups': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
    }
    return render(request, 'admin_panel/edit_donor.html', context)


@login_required
def reactivate_donor(request, donor_id):
    """Reactivate an inactive donor account"""
    if not request.user.is_staff:
        messages.error(request, 'Only admins can reactivate donor accounts.')
        return redirect('donor:donor_dashboard')
    
    if request.method == 'POST':
        try:
            donor = get_object_or_404(Donor, id=donor_id)
            
            # Reactivate the user account
            donor.user.is_active = True
            donor.user.save()
            
            # Notify the donor
            try:
                NotificationService.create_user_notification(
                    user=donor.user,
                    title='Account Reactivated',
                    message=f'Your account has been reactivated by an administrator. You can now log in and access all features.',
                    notification_type='success'
                )
            except Exception as e:
                print(f"Notification error: {e}")
            
            messages.success(request, f'Donor account for {donor.name} has been reactivated successfully.')
            return redirect('admin_panel:donor_detail', donor_id=donor.id)
            
        except Exception as e:
            messages.error(request, f'Error reactivating account: {str(e)}')
            return redirect('admin_panel:donor_detail', donor_id=donor_id)
    
    return redirect('admin_panel:donor_detail', donor_id=donor_id)


@login_required

def reports(request):
    """Generate comprehensive system reports"""
    from django.db.models import Count, Sum, Avg
    from datetime import datetime, timedelta
    import calendar
    
    # Get date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Set default date range (last 30 days)
    if not start_date:
        start_date = (timezone.now().date() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = timezone.now().date().strftime('%Y-%m-%d')
    
    # Convert to date objects
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start_date_obj = timezone.now().date() - timedelta(days=30)
        end_date_obj = timezone.now().date()
        start_date = start_date_obj.strftime('%Y-%m-%d')
        end_date = end_date_obj.strftime('%Y-%m-%d')
    
    # Basic statistics
    total_donors = Donor.objects.count()
    total_donations = DonationHistory.objects.filter(
        donation_date__range=[start_date_obj, end_date_obj]
    ).count()
    active_donors = Donor.objects.filter(
        last_donation_date__gte=timezone.now().date() - timedelta(days=90)
    ).count()
    
    # Monthly statistics
    current_month = timezone.now().date().replace(day=1)
    monthly_donations = DonationHistory.objects.filter(
        donation_date__gte=current_month
    ).count()
    
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    last_month_donations = DonationHistory.objects.filter(
        donation_date__range=[last_month, current_month - timedelta(days=1)]
    ).count()
    
    # Yearly statistics
    current_year = timezone.now().date().replace(month=1, day=1)
    yearly_donations = DonationHistory.objects.filter(
        donation_date__gte=current_year
    ).count()
    
    # Calculate monthly average
    months_in_year = timezone.now().month
    average_monthly = yearly_donations // months_in_year if months_in_year > 0 else 0
    
    # Blood group distribution
    blood_group_stats = {}
    max_count = 0
    for blood_group, _ in Donor.BLOOD_GROUPS:
        count = Donor.objects.filter(blood_group=blood_group).count()
        blood_group_stats[blood_group.replace('+', '_positive').replace('-', '_negative')] = count
        if count > max_count:
            max_count = count
    
    # Location distribution
    location_stats = {}
    max_location_count = 0
    city_counts = Donor.objects.exclude(city='').values('city').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    for item in city_counts:
        location_stats[item['city']] = item['count']
        if item['count'] > max_location_count:
            max_location_count = item['count']
    
    # Donation centers performance (mock data since we don't have actual center tracking)
    center_stats = {}
    max_center_count = 0
    
    # Get donation centers from DonationHistory if available
    try:
        from donor.models import DonationCenter
        centers = DonationCenter.objects.all()
        for center in centers:
            # Count donations for this center (using center name matching)
            count = DonationHistory.objects.filter(
                donation_center_name__icontains=center.name,
                donation_date__range=[start_date_obj, end_date_obj]
            ).count()
            if count > 0:
                center_stats[center.name] = count
                if count > max_center_count:
                    max_center_count = count
    except:
        # Fallback to generic center data
        center_donations = DonationHistory.objects.filter(
            donation_date__range=[start_date_obj, end_date_obj]
        ).values('donation_center_name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        for item in center_donations:
            if item['donation_center_name']:
                center_stats[item['donation_center_name']] = item['count']
                if item['count'] > max_center_count:
                    max_center_count = item['count']
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_donors': total_donors,
        'total_donations': total_donations,
        'active_donors': active_donors,
        'monthly_donations': monthly_donations,
        'last_month_donations': last_month_donations,
        'yearly_donations': yearly_donations,
        'average_monthly': average_monthly,
        'blood_group_stats': blood_group_stats,
        'max_count': max_count,
        'location_stats': location_stats,
        'max_location_count': max_location_count,
        'center_stats': center_stats,
        'max_center_count': max_center_count,
    }
    
    return render(request, 'admin_panel/reports.html', context)


@login_required

def export_donors(request):
    """Export donors data to CSV with filter support"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="donors_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Name', 'Email', 'Phone', 'Blood Group', 'City', 'State',
        'Date of Birth', 'Weight (kg)', 'Registration Date', 'Last Donation', 
        'Total Donations', 'Emergency Contact', 'Eligibility Status'
    ])
    
    donors = Donor.objects.select_related('user').annotate(
        donation_count=Count('donationhistory')
    )
    
    # Apply filters from query parameters
    search_query = request.GET.get('search', '')
    if search_query:
        donors = donors.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(blood_group__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    blood_group_filter = request.GET.get('blood_group', '')
    if blood_group_filter:
        donors = donors.filter(blood_group=blood_group_filter)
    
    city_filter = request.GET.get('city', '')
    if city_filter:
        donors = donors.filter(city__icontains=city_filter)
    
    donors = donors.order_by('id')
    
    for donor in donors:
        eligible, message = donor.can_donate()
        writer.writerow([
            donor.id,
            donor.name or donor.user.get_full_name() or donor.user.username,
            donor.user.email,
            donor.phone_number or 'N/A',
            donor.blood_group,
            donor.city or 'N/A',
            donor.state or 'N/A',
            donor.date_of_birth.strftime('%Y-%m-%d') if donor.date_of_birth else 'N/A',
            donor.weight if donor.weight else 'N/A',
            donor.created_at.strftime('%Y-%m-%d') if donor.created_at else 'N/A',
            donor.last_donation_date.strftime('%Y-%m-%d') if donor.last_donation_date else 'Never',
            donor.donation_count,
            'Yes' if donor.allow_emergency_contact else 'No',
            'Eligible' if eligible else f'Not Eligible - {message}'
        ])
    
    return response



@login_required

def export_donations(request):
    """Export donations data to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="donations_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Donor Name', 'Donor Email', 'Blood Group', 'Donation Date',
        'Center Name', 'Units Donated', 'Notes'
    ])
    
    donations = DonationHistory.objects.select_related(
        'donor__user'
    ).order_by('-donation_date')
    
    for donation in donations:
        writer.writerow([
            donation.id,
            donation.donor.name,
            donation.donor.user.email,
            donation.donor.blood_group,
            donation.donation_date.strftime('%Y-%m-%d'),
            donation.donation_center_name,
            donation.units_donated,
            donation.notes
        ])
    
    return response


@login_required

def export_reports(request):
    """Export comprehensive report to PDF"""
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    import io
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        # Create the HttpResponse object with PDF headers
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="blood_donation_report.pdf"'
        
        # Create the PDF object
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Title
        title = Paragraph("Blood Donation System - Comprehensive Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Generate date
        from datetime import datetime
        date_para = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style)
        elements.append(date_para)
        elements.append(Spacer(1, 12))
        
        # Statistics
        stats_heading = Paragraph("System Statistics", heading_style)
        elements.append(stats_heading)
        
        total_donors = Donor.objects.count()
        total_donations = DonationHistory.objects.count()
        active_donors = Donor.objects.filter(
            last_donation_date__gte=timezone.now().date() - timedelta(days=90)
        ).count()
        
        stats_data = [
            ['Metric', 'Value'],
            ['Total Donors', str(total_donors)],
            ['Total Donations', str(total_donations)],
            ['Active Donors (Last 90 days)', str(active_donors)],
        ]
        
        stats_table = Table(stats_data)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 12))
        
        # Blood Group Distribution
        bg_heading = Paragraph("Blood Group Distribution", heading_style)
        elements.append(bg_heading)
        
        bg_data = [['Blood Group', 'Number of Donors']]
        for blood_group, _ in Donor.BLOOD_GROUPS:
            count = Donor.objects.filter(blood_group=blood_group).count()
            bg_data.append([blood_group, str(count)])
        
        bg_table = Table(bg_data)
        bg_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(bg_table)
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and write it to the response
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        
        return response
        
    except ImportError:
        # Fallback to simple text response if reportlab is not available
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="blood_donation_report.txt"'
        
        report_content = f"""
BLOOD DONATION SYSTEM - COMPREHENSIVE REPORT
Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

SYSTEM STATISTICS:
- Total Donors: {Donor.objects.count()}
- Total Donations: {DonationHistory.objects.count()}
- Active Donors (Last 90 days): {Donor.objects.filter(last_donation_date__gte=timezone.now().date() - timedelta(days=90)).count()}

BLOOD GROUP DISTRIBUTION:
"""
        
        for blood_group, _ in Donor.BLOOD_GROUPS:
            count = Donor.objects.filter(blood_group=blood_group).count()
            report_content += f"- {blood_group}: {count} donors\n"
        
        response.write(report_content)
        return response



@login_required

@login_required

def resolve_emergency(request, emergency_id):
    """Mark an emergency request as resolved - ONLY the hospital that created it can resolve"""
    try:
        admin_hospital = request.user.hospital
        # Only allow the hospital that created the emergency to resolve it
        emergency = get_object_or_404(EmergencyRequest, id=emergency_id, hospital=admin_hospital)
    except EmergencyRequest.DoesNotExist:
        messages.error(request, 'You can only resolve emergencies created by your hospital.')
        return redirect('admin_panel:manage_emergencies')
    
    if request.method == 'POST':
        try:
            # Validate resolution
            if emergency.status == 'fulfilled':
                messages.info(request, f'Emergency is already resolved.')
                return redirect('admin_panel:manage_emergencies')
            elif emergency.status == 'expired':
                messages.warning(request, f'Cannot resolve expired emergency.')
                return redirect('admin_panel:manage_emergencies')
            
            # Get resolution details from form
            units_fulfilled = request.POST.get('units_fulfilled', emergency.units_needed)
            donor_name = request.POST.get('donor_name', '').strip()
            donor_contact = request.POST.get('donor_contact', '').strip()
            resolution_notes = request.POST.get('resolution_notes', '').strip()
            
            # Get admin info
            admin_name = request.user.get_full_name() or request.user.username
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
            
            # Mark as fulfilled
            emergency.status = 'fulfilled'
            
            # Build resolution note
            resolution_note = f"✅ RESOLVED by {admin_hospital.name}\n"
            resolution_note += f"Resolved by: Admin {admin_name}\n"
            resolution_note += f"Units fulfilled: {units_fulfilled}\n"
            resolution_note += f"Date: {timestamp}\n"
            
            if donor_name:
                resolution_note += f"Donor: {donor_name}\n"
            if donor_contact:
                resolution_note += f"Donor Contact: {donor_contact}\n"
            if resolution_notes:
                resolution_note += f"Notes: {resolution_notes}\n"
            
            if emergency.notes:
                emergency.notes = f"{emergency.notes}\n\n{resolution_note}"
            else:
                emergency.notes = resolution_note
            
            emergency.save()
            
            # Notify donors who responded
            from utils.notification_service import NotificationService
            for response in emergency.responses.all():
                try:
                    NotificationService.create_notification(
                        user=response.donor.user,
                        notification_type='emergency_resolved',
                        title='Emergency Resolved',
                        message=f'The emergency request from {emergency.hospital_name} has been resolved. Thank you for your response!',
                        related_object=emergency
                    )
                except Exception as e:
                    print(f"Notification error: {e}")
            
            messages.success(request, f'✅ Emergency resolved successfully!')
            return redirect('admin_panel:manage_emergencies')
            
        except Exception as e:
            messages.error(request, f'Error resolving emergency: {str(e)}')
            return redirect('admin_panel:manage_emergencies')
    
    # GET request - show resolution form
    # Get all donors for dropdown selection
    from donor.models import Donor
    all_donors = Donor.objects.select_related('user').filter(user__is_active=True).order_by('user__first_name')
    
    context = {
        'emergency': emergency,
        'is_helping_other_hospital': False,  # Always own hospital now
        'all_donors': all_donors,
    }
    return render(request, 'admin_panel/resolve_emergency.html', context)
    
    messages.error(request, 'Invalid request method.')
    return redirect('admin_panel:manage_emergencies')


@login_required

def update_inventory(request):
    """Update blood inventory - admins can only update their own hospital's inventory"""
    # Check if admin has a hospital
    try:
        admin_hospital = request.user.hospital
    except:
        messages.error(request, 'You must have a hospital assigned to manage inventory.')
        return redirect('admin_panel:dashboard')
    
    if request.method == 'POST':
        try:
            from donor.models import BloodInventory
            
            blood_group = request.POST.get('blood_group')
            action = request.POST.get('action')
            units = int(request.POST.get('units', 0))
            notes = request.POST.get('notes', '')
            
            if not blood_group or not action:
                messages.error(request, 'Blood group and action are required.')
                return redirect('admin_panel:manage_inventory')
            
            # Get or create inventory record for THIS HOSPITAL ONLY
            inventory, created = BloodInventory.objects.get_or_create(
                blood_group=blood_group,
                hospital=admin_hospital,
                defaults={'units_available': 0, 'units_reserved': 0}
            )
            
            # Perform action
            if action == 'add':
                inventory.units_available += units
                messages.success(request, f'Added {units} units to {blood_group} inventory at {admin_hospital.name}.')
            elif action == 'remove':
                if inventory.units_available >= units:
                    inventory.units_available -= units
                    messages.success(request, f'Removed {units} units from {blood_group} inventory at {admin_hospital.name}.')
                else:
                    messages.error(request, f'Cannot remove {units} units. Only {inventory.units_available} units available.')
                    return redirect('admin_panel:manage_inventory')
            elif action == 'set':
                inventory.units_available = units
                messages.success(request, f'Set {blood_group} inventory to {units} units at {admin_hospital.name}.')
            
            # Update notes and metadata
            if notes:
                inventory.notes = f"{timezone.now().strftime('%Y-%m-%d %H:%M')}: {notes}"
            
            inventory.last_updated = timezone.now()
            inventory.updated_by = request.user
            inventory.save()
            
        except Exception as e:
            messages.error(request, f'Error updating inventory: {str(e)}')
    
    return redirect('admin_panel:manage_inventory')


# Notification views for admin panel
@login_required

def all_notifications(request):
    """View all notifications for admin"""
    user_notifications = NotificationService.get_user_notifications(request.user, unread_only=False)
    system_notifications = NotificationService.get_system_notifications('admins', user=request.user)
    
    # Combine and sort notifications
    all_notifications = list(user_notifications) + list(system_notifications)
    all_notifications.sort(key=lambda x: x.created_at, reverse=True)
    
    unread_count = NotificationService.get_notification_count(request.user, unread_only=True)
    
    context = {
        'notifications': all_notifications,
        'unread_count': unread_count,
    }
    return render(request, 'admin_panel/all_notifications.html', context)


@login_required

def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    if request.method == 'POST':
        try:
            NotificationService.mark_notification_read(request.user, notification_id)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required

def mark_all_notifications_read(request):
    """Mark all notifications as read for admin"""
    if request.method == 'POST':
        try:
            NotificationService.mark_all_notifications_read(request.user)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required

def export_donors_csv(request):
    """Export donor list to CSV file"""
    from django.http import HttpResponse
    from django.db.models import Count, Q
    from datetime import datetime
    
    # Get the same filtered donors as in donor_tracking view
    donors = Donor.objects.select_related('user').annotate(
        donation_count=Count('donationhistory')
    )
    
    # Apply filters if present
    search_query = request.GET.get('search', '')
    if search_query:
        donors = donors.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(blood_group__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    blood_group_filter = request.GET.get('blood_group', '')
    if blood_group_filter:
        donors = donors.filter(blood_group=blood_group_filter)
    
    city_filter = request.GET.get('city', '')
    if city_filter:
        donors = donors.filter(city__icontains=city_filter)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="donors_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    # Write header
    writer.writerow([
        'ID', 'Name', 'Email', 'Phone', 'Blood Group', 
        'City', 'State', 'Date of Birth', 'Weight (kg)', 
        'Last Donation', 'Total Donations', 'Emergency Contact'
    ])
    
    # Write data
    for donor in donors:
        eligible, _ = donor.can_donate()
        writer.writerow([
            donor.id,
            donor.user.get_full_name() or donor.user.username,
            donor.user.email,
            donor.phone_number or 'N/A',
            donor.blood_group,
            donor.city or 'N/A',
            donor.state or 'N/A',
            donor.date_of_birth.strftime('%Y-%m-%d') if donor.date_of_birth else 'N/A',
            donor.weight if donor.weight else 'N/A',
            donor.last_donation_date.strftime('%Y-%m-%d') if donor.last_donation_date else 'Never',
            donor.donation_count,
            'Yes' if donor.allow_emergency_contact else 'No'
        ])
    
    return response

