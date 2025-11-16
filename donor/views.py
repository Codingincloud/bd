from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import date, timedelta
import json
from utils.notification_service import NotificationService
from .models import Donor, DonationRequest, DonationHistory, EmergencyRequest, DonationCenter, Hospital
from .forms import LocationUpdateForm, SimpleLocationForm, MedicalInfoUpdateForm, HealthMetricsForm
from .models import HealthMetrics
from datetime import timedelta, datetime, date

@login_required
def donor_dashboard(request):
    try:
        donor = request.user.donor
        
        # Get donation history
        donation_history = DonationHistory.objects.filter(donor=donor).order_by('-donation_date')[:5]
        
        # Get donation requests by status
        all_requests = DonationRequest.objects.filter(donor=donor)
        pending_requests = all_requests.filter(status='pending').order_by('requested_date')
        approved_requests = all_requests.filter(status='approved').order_by('requested_date')
        completed_requests = all_requests.filter(status='completed').order_by('-completed_at')
        cancelled_requests = all_requests.filter(status='cancelled').count()
        rejected_requests = all_requests.filter(status='rejected').count()
        
        # Get emergency requests where this donor can help
        can_receive_from_donor = {
            'O-': ['O-'],
            'O+': ['O-', 'O+'],
            'A-': ['O-', 'A-'],
            'A+': ['O-', 'O+', 'A-', 'A+'],
            'B-': ['O-', 'B-'],
            'B+': ['O-', 'O+', 'B-', 'B+'],
            'AB-': ['O-', 'A-', 'B-', 'AB-'],
            'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        }
        
        all_emergencies = EmergencyRequest.objects.filter(
            status='active',
            required_by__gte=timezone.now()
        ).order_by('-urgency_level', 'required_by')
        
        # Filter compatible emergencies
        emergency_requests = []
        for req in all_emergencies:
            blood_donors = can_receive_from_donor.get(req.blood_group_needed, [])
            if donor.blood_group in blood_donors:
                emergency_requests.append(req)
                if len(emergency_requests) >= 5:
                    break
        
        # Calculate statistics
        from django.db import models
        total_donations = DonationHistory.objects.filter(donor=donor).count()
        total_units_donated = DonationHistory.objects.filter(donor=donor).aggregate(
            total=models.Sum('units_donated')
        )['total'] or 0
        
        # Total completed appointments (from requests)
        total_completed_appointments = completed_requests.count()

        # Get notifications for the user (recent ones for dashboard) - reduced queries
        user_notifications = NotificationService.get_user_notifications(request.user, unread_only=False)[:3]
        system_notifications = NotificationService.get_system_notifications('donors', user=request.user)[:2]
        unread_count = NotificationService.get_notification_count(request.user, unread_only=True)
        
        # Get donation eligibility
        can_donate, eligibility_message = donor.can_donate()
        
        # Calculate impact statistics
        lives_helped = total_donations * 3  # Each donation can help up to 3 people
        
        # Get latest health metrics
        latest_health_metrics = HealthMetrics.objects.filter(donor=donor).order_by('-recorded_at').first()
        
        # Get recent health metrics for trends (last 6 months)
        six_months_ago = timezone.now() - timedelta(days=180)
        health_metrics_history = HealthMetrics.objects.filter(
            donor=donor,
            recorded_at__gte=six_months_ago
        ).order_by('recorded_at')
        
        # Calculate days until next eligible donation
        days_until_eligible = None
        if donor.next_eligible_date:
            delta = donor.next_eligible_date - date.today()
            days_until_eligible = delta.days if delta.days > 0 else 0

        context = {
            'donor': donor,
            'can_donate': can_donate,
            'eligibility_message': eligibility_message,
            'donation_history': donation_history,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
            'completed_requests': completed_requests,
            'cancelled_requests': cancelled_requests,
            'rejected_requests': rejected_requests,
            'emergency_requests': emergency_requests,
            'total_donations': total_donations,
            'total_units_donated': total_units_donated,
            'total_completed_appointments': total_completed_appointments,
            'next_eligible_date': donor.next_eligible_date,
            'user_notifications': user_notifications,
            'system_notifications': system_notifications,
            'unread_count': unread_count,
            'lives_helped': lives_helped,
            'latest_health_metrics': latest_health_metrics,
            'health_metrics_history': health_metrics_history,
            'days_until_eligible': days_until_eligible,
        }
        return render(request, 'donor/donor_dashboard.html', context)
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
        return redirect('accounts:login')

@login_required
def schedule_donation(request):
    try:
        donor = request.user.donor
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
        return redirect('accounts:login')
    
    # Check donation eligibility
    eligible, eligibility_message = donor.can_donate()
    
    if request.method == 'POST':
        try:
            # Parse the date and time from form
            requested_date = request.POST.get('requested_date')
            preferred_time = request.POST.get('preferred_time')
            donation_center_id = request.POST.get('donation_center')
            
            if not requested_date or not preferred_time:
                messages.error(request, 'Please select both date and time for your donation.')
                return redirect('donor:schedule_donation')
            
            # Get donation center if specified
            donation_center = None
            if donation_center_id:
                try:
                    donation_center = DonationCenter.objects.get(id=donation_center_id, is_active=True)
                except DonationCenter.DoesNotExist:
                    pass
            
            donation_request = DonationRequest(
                donor=donor,
                donation_center=donation_center,
                requested_date=requested_date,
                preferred_time=preferred_time,
                notes=request.POST.get('notes', '')
            )
            donation_request.save()

            # Create notification for donation scheduled
            NotificationService.notify_donation_scheduled(donation_request)

            # Send confirmation email
            try:
                if donor.user.email:
                    subject = 'Donation Appointment Scheduled - Blood Donation System'
                    center_info = f"- Location: {donation_request.donation_center.name}, {donation_request.donation_center.city}" if donation_request.donation_center else "- Location: To be determined"
                    message = f"""
Dear {donor.user.get_full_name() or donor.user.username},

Your blood donation appointment has been successfully scheduled!

Appointment Details:
- Date: {donation_request.requested_date}
- Time: {donation_request.preferred_time}
{center_info}
- Blood Type: {donor.blood_group}
- Status: Pending Approval

{f"Notes: {donation_request.notes}" if donation_request.notes else ""}

Please ensure you:
- Get adequate rest the night before
- Eat a healthy meal before donating
- Stay hydrated
- Bring a valid ID

Your appointment is currently pending approval. You will receive another email once it's confirmed.

Thank you for your commitment to saving lives through blood donation!

Best regards,
Blood Donation System Team
                    """
                    
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [donor.user.email],
                        fail_silently=True,
                    )
            except Exception as e:
                print(f"Failed to send confirmation email: {e}")
            
            messages.success(request, 'Donation appointment scheduled successfully! You can view your scheduled appointment in your donation history.')
            return redirect('donor:donation_history')
            
        except Exception as e:
            import traceback
            print(f"Error scheduling donation: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f'Error scheduling appointment: {str(e)}')
    
    # Calculate next eligible date
    next_eligible_date = None
    if donor.last_donation_date:
        next_eligible_date = donor.last_donation_date + timedelta(days=56)  # 8 weeks
    
    # Get active donation centers
    donation_centers = DonationCenter.objects.filter(is_active=True).order_by('city', 'name')
    
    context = {
        'donor': donor,
        'today': date.today(),
        'next_eligible_date': next_eligible_date,
        'eligible': eligible,
        'eligibility_message': eligibility_message,
        'donation_centers': donation_centers,
    }
    return render(request, 'donor/schedule_donation.html', context)

@login_required
def donation_history(request):
    try:
        donor = request.user.donor
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
        return redirect('accounts:login')
    
    # Get completed donation history
    history = DonationHistory.objects.filter(donor=donor).order_by('-donation_date')
    
    # Get all donation requests (not just pending)
    donation_requests = DonationRequest.objects.filter(donor=donor).order_by('-requested_date')
    pending_requests = donation_requests.filter(status='pending')
    approved_requests = donation_requests.filter(status='approved')
    completed_requests = donation_requests.filter(status='completed')
    cancelled_requests = donation_requests.filter(status='cancelled')
    rejected_requests = donation_requests.filter(status='rejected')
    
    context = {
        'donor': donor,
        'donation_history': history,
        'donation_requests': donation_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'completed_requests': completed_requests,
        'cancelled_requests': cancelled_requests,
        'rejected_requests': rejected_requests,
    }
    return render(request, 'donor/donation_history.html', context)

@login_required
def emergency_requests(request):
    try:
        donor = request.user.donor
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
        return redirect('accounts:login')
    
    # Get emergency requests where this donor can help
    # Build reverse compatibility: which blood groups can receive from this donor
    can_receive_from_donor = {
        'O-': ['O-'],
        'O+': ['O-', 'O+'],
        'A-': ['O-', 'A-'],
        'A+': ['O-', 'O+', 'A-', 'A+'],
        'B-': ['O-', 'B-'],
        'B+': ['O-', 'O+', 'B-', 'B+'],
        'AB-': ['O-', 'A-', 'B-', 'AB-'],
        'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],  # Universal recipient
    }
    
    # Get all active emergency requests
    all_emergencies = EmergencyRequest.objects.filter(
        status='active',
        required_by__gte=timezone.now()
    )
    
    # Filter to only include requests where donor's blood type can help
    compatible_requests = []
    for req in all_emergencies:
        blood_donors = can_receive_from_donor.get(req.blood_group_needed, [])
        if donor.blood_group in blood_donors:
            compatible_requests.append(req)
    
    # Sort by urgency and deadline (urgency_level is a string: critical > high > medium > low)
    urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    compatible_requests.sort(key=lambda x: (urgency_order.get(x.urgency_level, 99), x.required_by))
    
    # Calculate statistics
    critical_count = sum(1 for r in compatible_requests if r.urgency_level == 'critical')
    high_count = sum(1 for r in compatible_requests if r.urgency_level == 'high')
    medium_count = sum(1 for r in compatible_requests if r.urgency_level == 'medium')
    
    context = {
        'donor': donor,
        'emergency_requests': compatible_requests,
        'total_emergencies': len(compatible_requests),
        'critical_emergencies': critical_count,
        'high_emergencies': high_count,
        'medium_emergencies': medium_count,
        'compatible_groups': donor.compatible_blood_groups,
    }
    return render(request, 'donor/emergency_requests.html', context)

@login_required
def profile(request):
    """View donor profile"""
    try:
        donor = request.user.donor
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
        return redirect('accounts:login')
    
    context = {
        'donor': donor,
    }
    return render(request, 'donor/profile.html', context)

@login_required
def edit_profile(request):
    try:
        donor = request.user.donor
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        try:
            # Get and validate form data
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            
            # Validate required fields
            if not first_name:
                messages.error(request, 'First name is required.')
                return render(request, 'donor/edit_profile.html', {'donor': donor})
            
            if not email:
                messages.error(request, 'Email address is required.')
                return render(request, 'donor/edit_profile.html', {'donor': donor})
            
            # Validate email format
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            from django.contrib.auth.models import User
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, 'Please enter a valid email address.')
                return render(request, 'donor/edit_profile.html', {'donor': donor})
            
            # Check if email is already used by another user
            if User.objects.filter(email=email).exclude(id=donor.user.id).exists():
                messages.error(request, 'This email address is already registered to another account.')
                return render(request, 'donor/edit_profile.html', {'donor': donor})
            
            # Validate phone number format
            if phone_number:
                import re
                if not re.match(r'^\\+?[\\d\\s\\-\\(\\)]{10,15}$', phone_number):
                    messages.error(request, 'Please enter a valid phone number (10-15 digits).')
                    return render(request, 'donor/edit_profile.html', {'donor': donor})
            
            # Update user information
            user = donor.user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            
            # Update donor information
            donor.phone_number = phone_number
            donor.address = request.POST.get('address', '')

            # Update location information
            donor.city = request.POST.get('city', '')
            donor.state = request.POST.get('state', '')
            donor.postal_code = request.POST.get('postal_code', '')
            donor.country = request.POST.get('country', 'Nepal')

            # Update coordinates if provided
            latitude = request.POST.get('latitude', '')
            longitude = request.POST.get('longitude', '')
            if latitude and longitude:
                try:
                    donor.latitude = float(latitude)
                    donor.longitude = float(longitude)
                except ValueError:
                    pass  # Keep existing coordinates if invalid

            donor.weight = request.POST.get('weight', donor.weight)
            donor.height = request.POST.get('height', donor.height)
            donor.medical_conditions = request.POST.get('medical_conditions', '')
            donor.emergency_contact_name = request.POST.get('emergency_contact_name', '')
            donor.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
            donor.allow_emergency_contact = 'allow_emergency_contact' in request.POST
            
            # Handle date of birth
            dob = request.POST.get('date_of_birth')
            if dob:
                try:
                    donor.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
                except ValueError:
                    pass  # Keep existing date if invalid
            
            donor.save()
            messages.success(request, f'Profile updated successfully, {first_name}! Your information has been saved.')
            return redirect('donor:edit_profile')
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    context = {
        'donor': donor,
    }
    return render(request, 'donor/edit_profile.html', context)


@login_required
def change_password(request):
    """Change donor password"""
    try:
        donor = request.user.donor
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password1 = request.POST.get('new_password1', '')
        new_password2 = request.POST.get('new_password2', '')
        
        # Validate inputs
        if not old_password:
            messages.error(request, 'Please enter your current password.')
            return redirect('donor:edit_profile')
        
        if not new_password1 or not new_password2:
            messages.error(request, 'Please enter and confirm your new password.')
            return redirect('donor:edit_profile')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect. Please try again.')
            return redirect('donor:edit_profile')
        
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match. Please make sure both passwords are identical.')
            return redirect('donor:edit_profile')
        
        if len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long for security.')
            return redirect('donor:edit_profile')
        
        # Additional password strength validation
        import re
        if not re.search(r'[A-Za-z]', new_password1):
            messages.error(request, 'Password must contain at least one letter.')
            return redirect('donor:edit_profile')
        
        if not re.search(r'[0-9]', new_password1):
            messages.error(request, 'Password must contain at least one number.')
            return redirect('donor:edit_profile')
        
        request.user.set_password(new_password1)
        request.user.save()
        messages.success(request, 'Password changed successfully! Your account is now more secure.')
        
        # Keep user logged in and redirect back to edit profile
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)
        return redirect('donor:edit_profile')
    
    return redirect('donor:edit_profile')


@login_required
def update_location(request):
    """Simple location update for donors"""
    donor = get_object_or_404(Donor, user=request.user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'simple')

        if form_type == 'simple':
            form = SimpleLocationForm(request.POST)
            if form.is_valid():
                location_choice = form.cleaned_data['location_choice']
                custom_city = form.cleaned_data.get('custom_city', '').strip()
                custom_address = form.cleaned_data.get('custom_address', '').strip()

                if location_choice == 'other':
                    # Validate custom input
                    if not custom_city:
                        messages.error(request, 'Please enter your city name when selecting "Other".')
                        context = {
                            'donor': donor,
                            'simple_form': form,
                            'detailed_form': LocationUpdateForm(instance=donor),
                        }
                        return render(request, 'donor/update_location.html', context)
                    
                    # Use custom input
                    donor.city = custom_city
                    donor.address = custom_address or f"{custom_city}, Nepal"
                    donor.state = 'Nepal'

                    # Set basic coordinates for Nepal (can be updated via GPS later)
                    donor.latitude = 27.7172  # Default to Kathmandu coordinates
                    donor.longitude = 85.3240
                    
                elif location_choice:
                    # Use predefined location with basic coordinates
                    location_map = {
                        'kathmandu': {'name': 'Kathmandu', 'lat': 27.7172, 'lng': 85.3240},
                        'pokhara': {'name': 'Pokhara', 'lat': 28.2096, 'lng': 83.9856},
                        'lalitpur': {'name': 'Lalitpur', 'lat': 27.6588, 'lng': 85.3247},
                        'bhaktapur': {'name': 'Bhaktapur', 'lat': 27.6710, 'lng': 85.4298},
                        'biratnagar': {'name': 'Biratnagar', 'lat': 26.4525, 'lng': 87.2718},
                        'birgunj': {'name': 'Birgunj', 'lat': 27.0104, 'lng': 84.8803},
                        'dharan': {'name': 'Dharan', 'lat': 26.8147, 'lng': 87.2789},
                        'hetauda': {'name': 'Hetauda', 'lat': 27.4287, 'lng': 85.0326},
                        'janakpur': {'name': 'Janakpur', 'lat': 26.7288, 'lng': 85.9266},
                        'butwal': {'name': 'Butwal', 'lat': 27.7000, 'lng': 83.4500},
                    }

                    location_data = location_map.get(location_choice)
                    if location_data:
                        donor.city = location_data['name']
                        donor.address = f"{location_data['name']}, Nepal"
                        donor.state = 'Nepal'
                        donor.latitude = location_data['lat']
                        donor.longitude = location_data['lng']
                    else:
                        messages.error(request, 'Invalid location selected. Please try again.')
                        context = {
                            'donor': donor,
                            'simple_form': form,
                            'detailed_form': LocationUpdateForm(instance=donor),
                        }
                        return render(request, 'donor/update_location.html', context)
                else:
                    messages.error(request, 'Please select a location.')
                    context = {
                        'donor': donor,
                        'simple_form': form,
                        'detailed_form': LocationUpdateForm(instance=donor),
                    }
                    return render(request, 'donor/update_location.html', context)

                donor.save()

                # Create notification for location update
                try:
                    NotificationService.notify_location_updated(donor)
                except Exception as e:
                    print(f"Notification error: {e}")

                messages.success(request, f'Location updated to {donor.city} successfully! You can now be located by emergency blood requests in your area.')
                return redirect('donor:update_location')
            else:
                # Form validation errors
                messages.error(request, 'Please correct the errors in the form.')

        elif form_type == 'detailed':
            form = LocationUpdateForm(request.POST, instance=donor)
            if form.is_valid():
                # Validate city and address
                if not form.cleaned_data.get('city'):
                    messages.error(request, 'City is required for detailed location update.')
                    context = {
                        'donor': donor,
                        'simple_form': SimpleLocationForm(),
                        'detailed_form': form,
                    }
                    return render(request, 'donor/update_location.html', context)
                
                form.save()

                # Create notification for location update
                try:
                    NotificationService.notify_location_updated(donor)
                except Exception as e:
                    print(f"Notification error: {e}")

                messages.success(request, f'Detailed location updated successfully! Your full address: {donor.full_location}')
                return redirect('donor:update_location')
            else:
                # Form validation errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        simple_form = SimpleLocationForm()
        detailed_form = LocationUpdateForm(instance=donor)

    context = {
        'donor': donor,
        'simple_form': simple_form if request.method == 'GET' else SimpleLocationForm(),
        'detailed_form': detailed_form if request.method == 'GET' else LocationUpdateForm(instance=donor),
    }
    return render(request, 'donor/update_location.html', context)

@login_required
def detect_location(request):
    """Auto-detect user location using GPS with detailed information"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            if latitude and longitude:
                # Use enhanced geocoding service to get detailed location
                from utils.geocoding import geocoding_service
                location_info = geocoding_service.reverse_geocode(latitude, longitude)

                if location_info and location_info.get('success'):
                    # Prepare comprehensive location data
                    response_data = {
                        'success': True,
                        'location': {
                            # Main display information
                            'display_name': location_info.get('display_name', ''),
                            'formatted_address': location_info.get('formatted_address', ''),

                            # Address components for form filling
                            'house_number': location_info.get('house_number', ''),
                            'road': location_info.get('road', ''),
                            'neighbourhood': location_info.get('neighbourhood', ''),
                            'tole': location_info.get('tole', ''),
                            'ward': location_info.get('ward', ''),
                            'city': location_info.get('city', ''),
                            'municipality': location_info.get('municipality', ''),
                            'vdc_municipality': location_info.get('vdc_municipality', ''),
                            'district': location_info.get('district', ''),
                            'state': location_info.get('state', ''),
                            'postcode': location_info.get('postcode', ''),
                            'country': location_info.get('country', 'Nepal'),
                            'country_code': location_info.get('country_code', 'NP'),

                            # Coordinates
                            'latitude': location_info.get('latitude'),
                            'longitude': location_info.get('longitude'),

                            # Quality indicators (removed confidence display)
                            'place_type': location_info.get('place_type', ''),

                            # Suggested full address for the address field
                            'suggested_address': format_suggested_address(location_info),
                        }
                    }

                    return JsonResponse(response_data)
                else:
                    # Fallback with basic coordinate information
                    return JsonResponse({
                        'success': True,
                        'location': {
                            'display_name': f"Location: {latitude:.4f}, {longitude:.4f}",
                            'formatted_address': f"Coordinates: {latitude:.4f}, {longitude:.4f}",
                            'city': 'Unknown Location',
                            'country': 'Nepal',
                            'country_code': 'NP',
                            'latitude': float(latitude),
                            'longitude': float(longitude),
                            'suggested_address': f"Near {latitude:.4f}, {longitude:.4f}",
                            'note': 'Exact address could not be determined'
                        }
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid coordinates provided'
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Location detection failed: {str(e)}'
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def format_suggested_address(location_info):
    """Format a suggested address string for the address field"""
    parts = []

    # Start with house number and road
    if location_info.get('house_number'):
        parts.append(location_info['house_number'])
    if location_info.get('road'):
        parts.append(location_info['road'])

    # Add neighbourhood/tole
    if location_info.get('neighbourhood'):
        parts.append(location_info['neighbourhood'])
    elif location_info.get('tole'):
        parts.append(location_info['tole'])

    # Add ward if available
    if location_info.get('ward'):
        parts.append(f"Ward {location_info['ward']}")

    # Add city/municipality
    if location_info.get('city'):
        parts.append(location_info['city'])
    elif location_info.get('municipality'):
        parts.append(location_info['municipality'])

    # Add district if different from city
    if location_info.get('district') and location_info.get('district') != location_info.get('city'):
        parts.append(location_info['district'])

    # Add postcode if available
    if location_info.get('postcode'):
        parts.append(location_info['postcode'])

    return ', '.join(filter(None, parts)) or 'Address details not available'

@login_required
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read (keep it in system)"""
    if request.method == 'POST':
        try:
            from admin_panel.models import UserNotification
            notification = UserNotification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except UserNotification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user"""
    if request.method == 'POST':
        from admin_panel.models import UserNotification
        UserNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def all_notifications(request):
    """View all notifications for the user"""
    try:
        donor = request.user.donor
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
        return redirect('accounts:login')
    
    # Show all notifications (read and unread)
    user_notifications = NotificationService.get_user_notifications(request.user, unread_only=False)
    unread_count = NotificationService.get_notification_count(request.user, unread_only=True)

    context = {
        'donor': donor,
        'user_notifications': user_notifications,
        'unread_count': unread_count,
    }
    return render(request, 'donor/all_notifications.html', context)

@login_required
def dismiss_system_notification(request, notification_id):
    """Dismiss a system notification for the current user"""
    if request.method == 'POST':
        success = NotificationService.mark_system_notification_read(notification_id, request.user)
        return JsonResponse({'success': success})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def save_detected_location(request):
    """Save the detected location data to donor profile"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)

            donor = get_object_or_404(Donor, user=request.user)

            # Update donor location information
            if data.get('city'):
                donor.city = data['city']
            if data.get('country'):
                donor.country = data['country']
            if data.get('suggested_address'):
                donor.address = data['suggested_address']
            if data.get('latitude'):
                donor.latitude = float(data['latitude'])
            if data.get('longitude'):
                donor.longitude = float(data['longitude'])

            donor.save()

            # Create notification for location update
            NotificationService.notify_location_updated(donor)

            return JsonResponse({
                'success': True,
                'message': 'Location saved successfully!'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Failed to save location: {str(e)}'
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def compatibility_check(request):
    """Blood compatibility checker"""
    try:
        donor = request.user.donor
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
        return redirect('accounts:login')

    # Blood compatibility rules
    compatibility_data = {
        'A+': {
            'can_donate_to': ['A+', 'AB+'],
            'can_receive_from': ['A+', 'A-', 'O+', 'O-'],
            'universal_donor': False,
            'universal_receiver': False
        },
        'A-': {
            'can_donate_to': ['A+', 'A-', 'AB+', 'AB-'],
            'can_receive_from': ['A-', 'O-'],
            'universal_donor': False,
            'universal_receiver': False
        },
        'B+': {
            'can_donate_to': ['B+', 'AB+'],
            'can_receive_from': ['B+', 'B-', 'O+', 'O-'],
            'universal_donor': False,
            'universal_receiver': False
        },
        'B-': {
            'can_donate_to': ['B+', 'B-', 'AB+', 'AB-'],
            'can_receive_from': ['B-', 'O-'],
            'universal_donor': False,
            'universal_receiver': False
        },
        'AB+': {
            'can_donate_to': ['AB+'],
            'can_receive_from': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
            'universal_donor': False,
            'universal_receiver': True
        },
        'AB-': {
            'can_donate_to': ['AB+', 'AB-'],
            'can_receive_from': ['A-', 'B-', 'AB-', 'O-'],
            'universal_donor': False,
            'universal_receiver': False
        },
        'O+': {
            'can_donate_to': ['A+', 'B+', 'AB+', 'O+'],
            'can_receive_from': ['O+', 'O-'],
            'universal_donor': False,
            'universal_receiver': False
        },
        'O-': {
            'can_donate_to': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
            'can_receive_from': ['O-'],
            'universal_donor': True,
            'universal_receiver': False
        }
    }

    donor_blood_type = donor.blood_group
    compatibility_info = compatibility_data.get(donor_blood_type, {})

    # Get statistics about compatible donors and recipients
    total_donors = Donor.objects.count()
    compatible_recipients = Donor.objects.filter(
        blood_group__in=compatibility_info.get('can_donate_to', [])
    ).count()
    compatible_donors = Donor.objects.filter(
        blood_group__in=compatibility_info.get('can_receive_from', [])
    ).count()

    context = {
        'donor': donor,
        'compatibility_info': compatibility_info,
        'total_donors': total_donors,
        'compatible_recipients': compatible_recipients,
        'compatible_donors': compatible_donors,
        'all_blood_types': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        'compatibility_data': compatibility_data,
    }

    return render(request, 'donor/compatibility_check.html', context)

@login_required
def blood_inventory(request):
    """Show current blood stock levels"""
    try:
        donor = request.user.donor
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
        return redirect('accounts:login')

    # Get real blood inventory data from database
    from .models import BloodInventory
    blood_inventory = {}
    total_units = 0

    for blood_group, blood_group_display in Donor.BLOOD_GROUPS:
        try:
            inventory = BloodInventory.objects.get(blood_group=blood_group)
            units = inventory.units_available
            last_updated = inventory.last_updated
        except BloodInventory.DoesNotExist:
            # Create default inventory record if it doesn't exist
            inventory = BloodInventory.objects.create(
                blood_group=blood_group,
                units_available=0,
                notes='Initial inventory record'
            )
            units = 0
            last_updated = inventory.last_updated

        # Determine status based on units available
        if units <= 0:
            status = 'critical'
        elif units <= 5:
            status = 'low'
        elif units <= 15:
            status = 'adequate'
        else:
            status = 'good'

        blood_inventory[blood_group] = {
            'units': int(units),
            'status': status,
            'last_updated': last_updated.strftime('%B %d, %Y at %I:%M %p') if last_updated else 'Never'
        }
        total_units += int(units)

    # Get urgent needs (critical and low stock)
    urgent_needs = {k: v for k, v in blood_inventory.items() if v['status'] in ['critical', 'low']}

    context = {
        'donor': donor,
        'blood_inventory': blood_inventory,
        'total_units': total_units,
        'urgent_needs': urgent_needs,
    }

    return render(request, 'donor/blood_inventory.html', context)

@login_required
def donation_centers(request):
    """Show nearby donation centers"""
    try:
        donor = request.user.donor
        
        # Get search parameters with defaults
        city_filter = request.GET.get('city', '').strip()
        try:
            radius = int(request.GET.get('radius', 25))
        except (ValueError, TypeError):
            radius = 25  # Default radius in km
            
        status_filter = request.GET.get('status', '')

        # Get both hospitals and donation centers
        hospitals = Hospital.objects.filter(is_active=True, accepts_donations=True)
        donation_centers_qs = DonationCenter.objects.filter(is_active=True)

        # Filter by city if provided
        if city_filter:
            hospitals = hospitals.filter(city__icontains=city_filter)
            donation_centers_qs = donation_centers_qs.filter(city__icontains=city_filter)

        # Calculate distances and prepare hospital/center data
        centers = []
        has_location = bool(donor.latitude and donor.longitude)
        
        for hospital in hospitals:
            distance = None
            if has_location:
                try:
                    distance = hospital.distance_to_donor(donor)
                    # Filter by radius if donor has location
                    if distance and distance > radius:
                        continue
                except Exception as e:
                    # Log error but continue with other hospitals
                    print(f"Error calculating distance for hospital {hospital.id}: {str(e)}")
                    distance = None  # Skip distance filtering for this hospital

            center_data = {
                'name': hospital.name,
                'address': hospital.address,
                'city': hospital.city,
                'state': hospital.state,
                'phone': hospital.phone_number,
                'email': hospital.email,
                'hours': hospital.operating_hours or "Not specified",
                'services': getattr(hospital, 'services_list', []),
                'distance': f"{distance:.1f} km" if distance else 'N/A',
                'hospital_type': hospital.get_hospital_type_display() if hasattr(hospital, 'get_hospital_type_display') else 'Hospital',
                'id': hospital.id,
                'latitude': hospital.latitude,
                'longitude': hospital.longitude,
                'has_location': bool(hospital.latitude and hospital.longitude)
            }
            centers.append(center_data)

        # Add DonationCenter objects as well
        for dc in donation_centers_qs:
            # DonationCenter doesn't have distance calculation, so skip distance filtering
            center_data = {
                'name': dc.name,
                'address': dc.address,
                'city': dc.city,
                'state': dc.state,
                'phone': dc.phone_number,
                'email': dc.email,
                'hours': "Contact for hours",
                'services': ["Blood Donation"],
                'distance': 'N/A',
                'hospital_type': 'Donation Center',
                'id': dc.id,
                'latitude': None,
                'longitude': None,
                'has_location': False
            }
            centers.append(center_data)

        # Sort by distance if available
        if has_location:
            try:
                centers.sort(key=lambda x: float(x['distance'].replace(' km', '')) if x['distance'] != 'N/A' else float('inf'))
            except (ValueError, AttributeError):
                pass  # Skip sorting if distance parsing fails

        # Get user location for display
        user_location = None
        location_message = None
        
        if donor.city:
            user_location = f"{donor.city}, {donor.state}" if donor.state else donor.city
        elif has_location:
            user_location = f"Near coordinates: {donor.latitude:.4f}, {donor.longitude:.4f}"
        else:
            location_message = "Please update your location to find nearby centers."

        # Get all cities from both hospitals and donation centers
        hospital_cities = set(Hospital.objects.filter(is_active=True, accepts_donations=True)
                            .exclude(city__isnull=True).exclude(city='')
                            .values_list('city', flat=True))
        dc_cities = set(DonationCenter.objects.filter(is_active=True)
                       .exclude(city__isnull=True).exclude(city='')
                       .values_list('city', flat=True))
        all_cities = sorted(hospital_cities.union(dc_cities))

        context = {
            'donor': donor,
            'centers': centers,
            'user_location': user_location,
            'location_message': location_message,
            'search_radius': radius,
            'has_location': has_location,
            'cities': all_cities,
        }
        
        return render(request, 'donor/donation_centers.html', context)
        
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
        return redirect('accounts:login')
    except Exception as e:
        import traceback
        print(f"Error in donation_centers view: {str(e)}")
        print(traceback.format_exc())
        
        # Try to get donor for context, fall back to None
        try:
            donor = request.user.donor
        except:
            donor = None
            
        # Return a safe fallback context
        context = {
            'donor': donor,
            'centers': [],
            'user_location': None,
            'location_message': 'Unable to load centers at this time.',
            'search_radius': 25,
            'has_location': False,
            'cities': [],
        }
        messages.error(request, 'An error occurred while loading donation centers.')
        return render(request, 'donor/donation_centers.html', context)

@login_required
def medical_reports(request):
    """Show donor's medical reports and health tracking"""
    try:
        donor = request.user.donor
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
        return redirect('accounts:login')

    # Get latest health metrics from database
    latest_metrics = HealthMetrics.objects.filter(donor=donor).first()

    health_metrics = {}

    # Weight (from donor profile or latest metrics)
    weight_value = latest_metrics.weight if latest_metrics and latest_metrics.weight else donor.weight
    if weight_value:
        health_metrics['Weight'] = {
            'value': weight_value,
            'unit': 'kg',
            'status': 'normal' if 50 <= weight_value <= 100 else 'warning',
            'date': latest_metrics.recorded_at.strftime('%Y-%m-%d') if latest_metrics and latest_metrics.weight else 'Profile data'
        }

    # Blood Pressure
    if latest_metrics and latest_metrics.blood_pressure:
        systolic = latest_metrics.blood_pressure_systolic
        status = 'normal'
        if systolic > 140 or latest_metrics.blood_pressure_diastolic > 90:
            status = 'warning'
        elif systolic < 90 or latest_metrics.blood_pressure_diastolic < 60:
            status = 'warning'

        health_metrics['Blood Pressure'] = {
            'value': latest_metrics.blood_pressure,
            'unit': 'mmHg',
            'status': status,
            'date': latest_metrics.recorded_at.strftime('%Y-%m-%d')
        }

    # Heart Rate
    if latest_metrics and latest_metrics.resting_heart_rate:
        hr = latest_metrics.resting_heart_rate
        status = 'normal'
        if hr > 100 or hr < 60:
            status = 'warning'

        health_metrics['Heart Rate'] = {
            'value': hr,
            'unit': 'bpm',
            'status': status,
            'date': latest_metrics.recorded_at.strftime('%Y-%m-%d')
        }

    # Get all health metrics for history
    all_health_metrics = HealthMetrics.objects.filter(donor=donor)[:10]

    # Get recent donation history with health data
    recent_donations = DonationHistory.objects.filter(donor=donor).order_by('-donation_date')[:5]

    context = {
        'donor': donor,
        'health_metrics': health_metrics,
        'recent_donations': recent_donations,
        'can_donate': donor.can_donate(),
        'next_eligible_date': donor.next_eligible_date,
        'all_health_metrics': all_health_metrics,
        'latest_metrics': latest_metrics,
    }

    return render(request, 'donor/medical_reports.html', context)

@login_required
def update_medical_info(request):
    """Allow donors to update their medical information"""
    donor = get_object_or_404(Donor, user=request.user)

    if request.method == 'POST':
        form = MedicalInfoUpdateForm(request.POST, instance=donor)
        if form.is_valid():
            # Additional validation
            weight = form.cleaned_data.get('weight')
            height = form.cleaned_data.get('height')
            emergency_contact_name = form.cleaned_data.get('emergency_contact_name', '').strip()
            emergency_contact_phone = form.cleaned_data.get('emergency_contact_phone', '').strip()
            
            # Get blood pressure and heart rate from POST data
            bp_systolic = request.POST.get('blood_pressure_systolic', '').strip()
            bp_diastolic = request.POST.get('blood_pressure_diastolic', '').strip()
            heart_rate = request.POST.get('resting_heart_rate', '').strip()
            
            # Validate weight for donation eligibility
            if weight and weight < 45:
                messages.warning(request, 'Your weight is below the minimum requirement (45 kg) for blood donation. Please consult with our medical team.')
            
            # Validate emergency contact consistency
            if (emergency_contact_name and not emergency_contact_phone) or (emergency_contact_phone and not emergency_contact_name):
                messages.warning(request, 'Please provide both emergency contact name and phone number, or leave both empty.')
                context = {
                    'donor': donor,
                    'form': form,
                }
                return render(request, 'donor/update_medical_info.html', context)
            
            # Save the form
            form.save()
            
            # Save blood pressure and heart rate if provided
            if bp_systolic or bp_diastolic or heart_rate:
                try:
                    # Create health metrics record
                    health_data = {
                        'donor': donor,
                        'weight': weight if weight else donor.weight,
                    }
                    
                    if bp_systolic:
                        health_data['blood_pressure_systolic'] = int(bp_systolic)
                    if bp_diastolic:
                        health_data['blood_pressure_diastolic'] = int(bp_diastolic)
                    if heart_rate:
                        health_data['resting_heart_rate'] = int(heart_rate)
                    
                    # Validate blood pressure
                    if bp_systolic and bp_diastolic:
                        sys_val = int(bp_systolic)
                        dia_val = int(bp_diastolic)
                        if sys_val <= dia_val:
                            messages.error(request, 'Systolic blood pressure must be higher than diastolic.')
                            return render(request, 'donor/update_medical_info.html', {'donor': donor, 'form': form})
                    
                    HealthMetrics.objects.create(**health_data)
                    messages.success(request, '✅ Medical information and health metrics updated successfully!')
                except ValueError:
                    messages.warning(request, 'Medical info saved, but invalid health metrics values were provided.')
            else:
                # Provide helpful feedback
                if weight and weight >= 50:
                    messages.success(request, 'Medical information updated successfully! Your health profile is complete and you meet the weight requirement for donation.')
                else:
                    messages.success(request, 'Medical information updated successfully!')
            
            return redirect('donor:medical_reports')
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        form = MedicalInfoUpdateForm(instance=donor)
        
        # Get latest health metrics for pre-filling
        latest_metrics = HealthMetrics.objects.filter(donor=donor).order_by('-recorded_at').first()
        if latest_metrics:
            donor.latest_bp_systolic = latest_metrics.blood_pressure_systolic
            donor.latest_bp_diastolic = latest_metrics.blood_pressure_diastolic
            donor.latest_heart_rate = latest_metrics.resting_heart_rate

    context = {
        'donor': donor,
        'form': form,
    }
    return render(request, 'donor/update_medical_info.html', context)

@login_required
def add_health_metrics(request):
    """Allow donors to add their current health metrics"""
    donor = get_object_or_404(Donor, user=request.user)

    if request.method == 'POST':
        form = HealthMetricsForm(request.POST)
        if form.is_valid():
            # Validate blood pressure readings
            systolic = form.cleaned_data.get('blood_pressure_systolic')
            diastolic = form.cleaned_data.get('blood_pressure_diastolic')
            
            if systolic and diastolic:
                if systolic <= diastolic:
                    messages.error(request, 'Systolic blood pressure must be higher than diastolic pressure. Please check your readings.')
                    context = {
                        'donor': donor,
                        'form': form,
                        'recent_metrics': HealthMetrics.objects.filter(donor=donor).order_by('-recorded_at')[:5],
                    }
                    return render(request, 'donor/add_health_metrics.html', context)
                
                # Health warnings
                if systolic > 140 or diastolic > 90:
                    messages.warning(request, 'Your blood pressure readings are high. Please consult a doctor before donating blood.')
                elif systolic < 90 or diastolic < 60:
                    messages.warning(request, 'Your blood pressure readings are low. This may affect your eligibility to donate.')
            
            # Validate heart rate
            heart_rate = form.cleaned_data.get('resting_heart_rate')
            if heart_rate:
                if heart_rate < 50:
                    messages.info(request, 'Your resting heart rate is quite low. If you\'re an athlete, this is normal. Otherwise, please consult a doctor.')
                elif heart_rate > 100:
                    messages.warning(request, 'Your resting heart rate is elevated. Please ensure you are relaxed when measuring, or consult a doctor.')
            
            # Validate weight
            weight = form.cleaned_data.get('current_weight')
            if weight:
                if weight < 45:
                    messages.warning(request, 'Your weight is below the minimum requirement (45 kg) for blood donation.')
                elif weight < 50:
                    messages.info(request, 'Your weight is at the lower range. Please ensure you are well-nourished before donating.')
            
            # Create new health metrics record
            try:
                health_metrics = HealthMetrics.objects.create(
                    donor=donor,
                    weight=weight,
                    blood_pressure_systolic=systolic,
                    blood_pressure_diastolic=diastolic,
                    resting_heart_rate=heart_rate,
                    notes=form.cleaned_data.get('notes', '')
                )

                # Update donor's weight if provided
                if weight:
                    donor.weight = weight
                    donor.save()

                messages.success(request, f'Health metrics recorded successfully! Date: {health_metrics.recorded_at.strftime("%Y-%m-%d %H:%M")}')
                return redirect('donor:medical_reports')
            
            except Exception as e:
                messages.error(request, f'Error saving health metrics: {str(e)}. Please try again.')
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        # Pre-fill with current donor data
        initial_data = {}
        if donor.weight:
            initial_data['current_weight'] = donor.weight
        form = HealthMetricsForm(initial=initial_data)

    # Get recent health metrics for reference
    recent_metrics = HealthMetrics.objects.filter(donor=donor).order_by('-recorded_at')[:5]

    context = {
        'donor': donor,
        'form': form,
        'recent_metrics': recent_metrics,
    }
    return render(request, 'donor/add_health_metrics.html', context)


@login_required
def update_health_metrics(request):
    """Allow donors to update their latest health metrics"""
    donor = get_object_or_404(Donor, user=request.user)

    # Get the latest health metrics to update
    latest_metrics = HealthMetrics.objects.filter(donor=donor).first()
    
    if request.method == 'POST':
        form = HealthMetricsForm(request.POST)
        if form.is_valid():
            if latest_metrics:
                # Update existing metrics
                latest_metrics.weight = form.cleaned_data['current_weight']
                latest_metrics.blood_pressure_systolic = form.cleaned_data['blood_pressure_systolic']
                latest_metrics.blood_pressure_diastolic = form.cleaned_data['blood_pressure_diastolic']
                latest_metrics.resting_heart_rate = form.cleaned_data['resting_heart_rate']
                latest_metrics.notes = form.cleaned_data['notes']
                latest_metrics.recorded_at = timezone.now()
                latest_metrics.save()
            else:
                # Create new if none exists
                latest_metrics = HealthMetrics.objects.create(
                    donor=donor,
                    weight=form.cleaned_data['current_weight'],
                    blood_pressure_systolic=form.cleaned_data['blood_pressure_systolic'],
                    blood_pressure_diastolic=form.cleaned_data['blood_pressure_diastolic'],
                    resting_heart_rate=form.cleaned_data['resting_heart_rate'],
                    notes=form.cleaned_data['notes']
                )

            # Update donor's weight if provided
            if form.cleaned_data['current_weight']:
                donor.weight = form.cleaned_data['current_weight']
                donor.save()

            messages.success(request, 'Health metrics updated successfully!')
            return redirect('donor:medical_reports')
    else:
        # Pre-fill with latest metrics or current donor data
        initial_data = {}
        if latest_metrics:
            initial_data['current_weight'] = latest_metrics.weight
            initial_data['blood_pressure_systolic'] = latest_metrics.blood_pressure_systolic
            initial_data['blood_pressure_diastolic'] = latest_metrics.blood_pressure_diastolic
            initial_data['resting_heart_rate'] = latest_metrics.resting_heart_rate
            initial_data['notes'] = latest_metrics.notes
        elif donor.weight:
            initial_data['current_weight'] = donor.weight
        
        form = HealthMetricsForm(initial=initial_data)

    # Get recent health metrics for reference
    recent_metrics = HealthMetrics.objects.filter(donor=donor)[:5]

    context = {
        'donor': donor,
        'form': form,
        'recent_metrics': recent_metrics,
        'is_update': True,
        'latest_metrics': latest_metrics,
    }
    return render(request, 'donor/add_health_metrics.html', context)


@login_required
def respond_to_emergency(request, emergency_id):
    """Allow donors to respond to emergency requests"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            response_text = data.get('response', '')
            selected_hospital_id = data.get('hospital_id', None)
            
            donor = get_object_or_404(Donor, user=request.user)
            emergency_request = get_object_or_404(EmergencyRequest, id=emergency_id)
            
            # Get selected hospital if provided
            selected_hospital = None
            if selected_hospital_id:
                try:
                    selected_hospital = Hospital.objects.get(id=selected_hospital_id)
                except Hospital.DoesNotExist:
                    pass
            
            # Create a notification to admin about the response
            NotificationService.notify_emergency_response(
                emergency_request, 
                donor, 
                response_text,
                selected_hospital
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Response sent successfully to the hospital!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error sending response: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def cancel_request(request, request_id):
    """Cancel a pending donation request"""
    if request.method != 'POST':
        messages.error(request, 'Invalid request method. Please use the cancel button.')
        return redirect('donor:donor_dashboard')
    
    try:
        donor = get_object_or_404(Donor, user=request.user)
        donation_request = get_object_or_404(DonationRequest, id=request_id, donor=donor)
        
        # Check if request can be cancelled
        if donation_request.status == 'pending':
            donation_request.status = 'cancelled'
            donation_request.notes = f"Cancelled by donor at {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            donation_request.save()
            
            # Notify admin about cancellation
            try:
                NotificationService.create_system_notification(
                    title=f'Donation Request Cancelled',
                    message=f'Donor {donor.name} cancelled their donation scheduled for {donation_request.requested_date}',
                    notification_type='warning',
                    target_audience='admins'
                )
            except Exception as e:
                print(f"Error creating notification: {e}")
            
            messages.success(request, f'Donation request for {donation_request.requested_date} cancelled successfully. You can schedule a new appointment anytime.')
        elif donation_request.status == 'approved':
            messages.warning(request, 'This request has been approved. Please contact the donation center directly to cancel.')
        elif donation_request.status == 'completed':
            messages.error(request, 'Cannot cancel a completed donation.')
        elif donation_request.status == 'cancelled':
            messages.info(request, 'This request has already been cancelled.')
        else:
            messages.error(request, f'Cannot cancel a {donation_request.status} request.')
    
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
    except Exception as e:
        messages.error(request, f'Error cancelling request: {str(e)}')
    
    return redirect('donor:donor_dashboard')

@login_required
def get_nearest_hospitals(request):
    """API endpoint to get nearest hospitals for a donor"""
    if request.method == 'GET':
        try:
            donor = get_object_or_404(Donor, user=request.user)
            max_distance = int(request.GET.get('radius', 50))
            limit = int(request.GET.get('limit', 10))
            
            hospitals = Hospital.get_nearest_hospitals(donor, max_distance, limit)
            
            hospital_data = []
            for hospital in hospitals:
                distance = hospital.distance_to_donor(donor) if donor.latitude and donor.longitude else None
                hospital_data.append({
                    'id': hospital.id,
                    'name': hospital.name,
                    'address': hospital.address,
                    'city': hospital.city,
                    'phone': hospital.phone_number,
                    'distance': distance,
                    'hospital_type': hospital.get_hospital_type_display(),
                    'services': hospital.services_list,
                })
            
            return JsonResponse({
                'success': True,
                'hospitals': hospital_data,
                'donor_location': {
                    'city': donor.city,
                    'latitude': float(donor.latitude) if donor.latitude else None,
                    'longitude': float(donor.longitude) if donor.longitude else None,
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
