from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from .models import Donor, DonationRequest, DonationHistory, EmergencyRequest, DonationCenter
from .forms import LocationUpdateForm, SimpleLocationForm, MedicalInfoUpdateForm, HealthMetricsForm
from .models import HealthMetrics
from utils.nepal_locations import get_nepal_location
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
        
        context = {
            'donor': donor,
            'can_donate': donor.can_donate(),
            'donation_history': donation_history,
            'pending_requests': pending_requests,
            'emergency_requests': emergency_requests,
            'total_donations': total_donations,
            'total_units_donated': total_units_donated,
            'next_eligible_date': donor.next_eligible_date,
        }
        return render(request, 'donor/donor_dashboard.html', context)
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please contact support.')
        return redirect('accounts:login')

@login_required
def schedule_donation(request):
    donor = get_object_or_404(Donor, user=request.user)
    
    if not donor.can_donate():
        messages.warning(request, 'You are not eligible to donate at this time.')
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

                        # Try to get coordinates for the custom city
                        location_data = get_nepal_location(custom_city)
                        if location_data:
                            donor.latitude = location_data['lat']
                            donor.longitude = location_data['lng']
                elif location_choice:
                    # Use predefined location
                    location_data = get_nepal_location(location_choice)
                    if location_data:
                        donor.city = location_data['name']
                        donor.address = f"{location_data['name']}, Nepal"
                        donor.latitude = location_data['lat']
                        donor.longitude = location_data['lng']

                donor.save()
                messages.success(request, 'Location updated successfully!')
                return redirect('donor:update_location')

        elif form_type == 'detailed':
            form = LocationUpdateForm(request.POST, instance=donor)
            if form.is_valid():
                form.save()
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
    """Handle location detection from GPS"""
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if latitude and longitude:
            try:
                donor = request.user.donor
                donor.latitude = float(latitude)
                donor.longitude = float(longitude)
                donor.save()

                messages.success(request, f'GPS location detected and saved! ({latitude}, {longitude})')
            except (ValueError, Donor.DoesNotExist):
                messages.error(request, 'Error saving GPS location.')
        else:
            messages.error(request, 'Could not detect your location.')

    return redirect('donor:update_location')

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
