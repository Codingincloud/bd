from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from utils.notification_service import NotificationService
from .models import Donor, DonationRequest, DonationHistory, EmergencyRequest, DonationCenter
from .forms import LocationUpdateForm, SimpleLocationForm, MedicalInfoUpdateForm, HealthMetricsForm
from .models import HealthMetrics
# Removed Nepal locations dependency
from datetime import datetime, timedelta

@login_required
def donor_dashboard(request):
    try:
        donor = request.user.donor
        
        # Get donation history
        donation_history = DonationHistory.objects.filter(donor=donor).order_by('-donation_date')[:5]
        
        # Get pending requests
        pending_requests = DonationRequest.objects.filter(
            donor=donor,
            status='pending'
        ).order_by('requested_date')
        
        # Get emergency requests for donor's blood type
        emergency_requests = EmergencyRequest.objects.filter(
            blood_group_needed=donor.blood_group,
            status='active',
            required_by__gte=timezone.now()
        )[:5]
        
        # Calculate statistics
        total_donations = DonationHistory.objects.filter(donor=donor).count()
        total_units_donated = DonationHistory.objects.filter(donor=donor).aggregate(
            total=models.Sum('units_donated')
        )['total'] or 0

        # Get notifications for the user (recent ones for dashboard)
        user_notifications = NotificationService.get_user_notifications(request.user, unread_only=False)[:5]
        system_notifications = NotificationService.get_system_notifications('donors', user=request.user)[:3]
        unread_count = NotificationService.get_notification_count(request.user, unread_only=True)
        
        # Get donation eligibility
        can_donate, eligibility_message = donor.can_donate()

        context = {
            'donor': donor,
            'can_donate': can_donate,
            'eligibility_message': eligibility_message,
            'donation_history': donation_history,
            'pending_requests': pending_requests,
            'emergency_requests': emergency_requests,
            'total_donations': total_donations,
            'total_units_donated': total_units_donated,
            'next_eligible_date': donor.next_eligible_date,
            'user_notifications': user_notifications,
            'system_notifications': system_notifications,
            'unread_count': unread_count,
        }
        return render(request, 'donor/donor_dashboard.html', context)
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
        return redirect('accounts:login')

@login_required
def schedule_donation(request):
    donor = get_object_or_404(Donor, user=request.user)
    
    # Check donation eligibility
    eligible, eligibility_message = donor.can_donate()
    if not eligible:
        messages.warning(request, f'You are not eligible to donate at this time. {eligibility_message}')
        return redirect('donor:donor_dashboard')
    
    if request.method == 'POST':
        try:
            donation_request = DonationRequest(
                donor=donor,
                requested_date=request.POST['requested_date'],
                preferred_time=request.POST['preferred_time'],
                notes=request.POST.get('notes', '')
            )
            donation_request.save()

            # Create notification for donation scheduled
            NotificationService.notify_donation_scheduled(donation_request)

            # Send confirmation email
            try:
                if donor.user.email:
                    subject = 'Donation Appointment Scheduled - Blood Donation System'
                    message = f"""
Dear {donor.user.get_full_name() or donor.user.username},

Your blood donation appointment has been successfully scheduled!

Appointment Details:
- Date: {donation_request.requested_date}
- Time: {donation_request.preferred_time}
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
            
            messages.success(request, 'Donation appointment scheduled successfully!')
            return redirect('donor:donor_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error scheduling appointment: {str(e)}')
    
    return render(request, 'donor/schedule_donation.html', {'donor': donor})

@login_required
def donation_history(request):
    donor = get_object_or_404(Donor, user=request.user)
    history = DonationHistory.objects.filter(donor=donor).order_by('-donation_date')
    
    context = {
        'donor': donor,
        'donation_history': history,
    }
    return render(request, 'donor/donation_history.html', context)

@login_required
def emergency_requests(request):
    donor = get_object_or_404(Donor, user=request.user)
    
    # Get emergency requests for compatible blood types
    compatible_groups = donor.compatible_blood_groups
    emergency_requests = EmergencyRequest.objects.filter(
        blood_group_needed__in=compatible_groups,
        status='active',
        required_by__gte=timezone.now()
    ).order_by('-urgency_level', 'required_by')
    
    context = {
        'donor': donor,
        'emergency_requests': emergency_requests,
        'compatible_groups': compatible_groups,
    }
    return render(request, 'donor/emergency_requests.html', context)

@login_required
def edit_profile(request):
    donor = get_object_or_404(Donor, user=request.user)
    
    if request.method == 'POST':
        try:
            # Update user information
            user = donor.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            
            # Update donor information
            donor.phone_number = request.POST.get('phone_number', '')
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
            messages.success(request, 'Profile updated successfully!')
            return redirect('donor:edit_profile')
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    context = {
        'donor': donor,
    }
    return render(request, 'donor/edit_profile.html', context)

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
                custom_city = form.cleaned_data['custom_city']
                custom_address = form.cleaned_data['custom_address']

                if location_choice == 'other':
                    # Use custom input
                    if custom_city:
                        donor.city = custom_city
                        donor.address = custom_address or f"{custom_city}, Nepal"

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
                        donor.latitude = location_data['lat']
                        donor.longitude = location_data['lng']

                donor.save()

                # Create notification for location update
                NotificationService.notify_location_updated(donor)

                messages.success(request, 'Location updated successfully!')
                return redirect('donor:update_location')

        elif form_type == 'detailed':
            form = LocationUpdateForm(request.POST, instance=donor)
            if form.is_valid():
                form.save()

                # Create notification for location update
                NotificationService.notify_location_updated(donor)

                messages.success(request, 'Detailed location updated successfully!')
                return redirect('donor:update_location')
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
    # Show all notifications (read and unread)
    user_notifications = NotificationService.get_user_notifications(request.user, unread_only=False)
    unread_count = NotificationService.get_notification_count(request.user, unread_only=True)

    context = {
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
    donor = get_object_or_404(Donor, user=request.user)

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
    donor = get_object_or_404(Donor, user=request.user)

    # Simulate blood inventory data (in real system, this would come from database)
    blood_inventory = {
        'A+': {'units': 45, 'status': 'adequate', 'last_updated': '2 hours ago'},
        'A-': {'units': 12, 'status': 'low', 'last_updated': '1 hour ago'},
        'B+': {'units': 38, 'status': 'adequate', 'last_updated': '3 hours ago'},
        'B-': {'units': 8, 'status': 'critical', 'last_updated': '30 minutes ago'},
        'AB+': {'units': 15, 'status': 'low', 'last_updated': '2 hours ago'},
        'AB-': {'units': 5, 'status': 'critical', 'last_updated': '1 hour ago'},
        'O+': {'units': 52, 'status': 'good', 'last_updated': '4 hours ago'},
        'O-': {'units': 18, 'status': 'low', 'last_updated': '1 hour ago'},
    }

    # Calculate total units
    total_units = sum(data['units'] for data in blood_inventory.values())

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
    donor = get_object_or_404(Donor, user=request.user)

    # Sample donation centers (in real system, this would come from database)
    centers = [
        {
            'name': 'Central Blood Bank',
            'address': 'Kathmandu Medical College, Sinamangal, Kathmandu',
            'phone': '+977-1-4412303',
            'hours': '24/7',
            'services': ['Blood Collection', 'Blood Testing', 'Emergency Supply'],
            'distance': '2.5 km' if donor.city == 'Kathmandu' else 'N/A'
        },
        {
            'name': 'Nepal Red Cross Society',
            'address': 'Kalimati, Kathmandu',
            'phone': '+977-1-4270650',
            'hours': '9:00 AM - 5:00 PM',
            'services': ['Blood Collection', 'Voluntary Donation Camps'],
            'distance': '3.2 km' if donor.city == 'Kathmandu' else 'N/A'
        },
        {
            'name': 'Bir Hospital Blood Bank',
            'address': 'Mahaboudha, Kathmandu',
            'phone': '+977-1-4221119',
            'hours': '24/7',
            'services': ['Blood Collection', 'Emergency Supply', 'Blood Testing'],
            'distance': '1.8 km' if donor.city == 'Kathmandu' else 'N/A'
        },
        {
            'name': 'Patan Hospital Blood Bank',
            'address': 'Lagankhel, Lalitpur',
            'phone': '+977-1-5522266',
            'hours': '24/7',
            'services': ['Blood Collection', 'Blood Testing', 'Emergency Supply'],
            'distance': '4.1 km' if donor.city in ['Kathmandu', 'Lalitpur'] else 'N/A'
        }
    ]

    context = {
        'donor': donor,
        'centers': centers,
    }

    return render(request, 'donor/donation_centers.html', context)

@login_required
def medical_reports(request):
    """Show donor's medical reports and health tracking"""
    donor = get_object_or_404(Donor, user=request.user)

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

    # Sample donation history with health checks
    recent_donations = [
        {
            'date': '2024-01-15',
            'center': 'Central Blood Bank',
            'hemoglobin': 14.2,
            'blood_pressure': '120/80',
            'status': 'successful',
            'next_eligible': '2024-04-15'
        },
        {
            'date': '2023-10-10',
            'center': 'Nepal Red Cross',
            'hemoglobin': 13.8,
            'blood_pressure': '118/78',
            'status': 'successful',
            'next_eligible': '2024-01-10'
        }
    ]

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
            form.save()
            messages.success(request, 'Medical information updated successfully!')
            return redirect('donor:medical_reports')
    else:
        form = MedicalInfoUpdateForm(instance=donor)

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
            # Create new health metrics record
            health_metrics = HealthMetrics.objects.create(
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

            messages.success(request, 'Health metrics recorded successfully!')
            return redirect('donor:medical_reports')
    else:
        # Pre-fill with current donor data
        initial_data = {}
        if donor.weight:
            initial_data['current_weight'] = donor.weight
        form = HealthMetricsForm(initial=initial_data)

    # Get recent health metrics for reference
    recent_metrics = HealthMetrics.objects.filter(donor=donor)[:5]

    context = {
        'donor': donor,
        'form': form,
        'recent_metrics': recent_metrics,
    }
    return render(request, 'donor/add_health_metrics.html', context)

@login_required
def cancel_request(request, request_id):
    donor = get_object_or_404(Donor, user=request.user)
    donation_request = get_object_or_404(DonationRequest, id=request_id, donor=donor)
    
    if donation_request.status == 'pending':
        donation_request.status = 'cancelled'
        donation_request.save()
        messages.success(request, 'Donation request cancelled successfully.')
    else:
        messages.error(request, 'Cannot cancel this request.')
    
    return redirect('donor:donor_dashboard')
