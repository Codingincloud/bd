from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from donor.models import Donor
from admin_panel.models import AdminProfile
from datetime import date
import re

def validate_registration_data(data):
    """Validate registration form data"""
    errors = []
    
    # Username validation
    username = data.get('username', '').strip()
    if not username:
        errors.append('Username is required.')
    elif len(username) < 3:
        errors.append('Username must be at least 3 characters long.')
    elif User.objects.filter(username=username).exists():
        errors.append('Username already exists.')
    
    # Password validation
    password = data.get('password', '')
    if not password:
        errors.append('Password is required.')
    elif len(password) < 6:
        errors.append('Password must be at least 6 characters long.')
    
    # Email validation
    email = data.get('email', '').strip()
    if not email:
        errors.append('Email address is required.')
    else:
        try:
            validate_email(email)
            if User.objects.filter(email=email).exists():
                errors.append('Email address already registered.')
        except ValidationError:
            errors.append('Please enter a valid email address.')
    
    # Role validation
    role = data.get('role')
    if role not in ['donor', 'admin']:
        errors.append('Please select a valid role.')
    
    # Role-specific validation
    if role == 'donor':
        blood_group = data.get('blood_group')
        if not blood_group:
            errors.append('Blood group is required for donors.')
        
        contact_no = data.get('contact_no', '').strip()
        if not contact_no:
            errors.append('Contact number is required.')
        elif not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', contact_no):
            errors.append('Please enter a valid contact number.')
    
    return errors

def register_view(request):
    if request.method == 'POST':
        # Validate form data
        errors = validate_registration_data(request.POST)
        if errors:
            return render(request, 'accounts/register.html', {
                'errors': errors,
                'form_data': request.POST
            })
        
        username = request.POST.get('username').strip()
        password = request.POST.get('password')
        email = request.POST.get('email').strip()
        role = request.POST.get('role')

        try:
            with transaction.atomic():
                user = User.objects.create_user(username=username, password=password, email=email)
                
                if role == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                    
                    name = request.POST.get('admin_name', '').strip()
                    contact_no = request.POST.get('admin_contact_no', '').strip()
                    address = request.POST.get('admin_address', '').strip()

                    # Get admin location fields
                    admin_city = request.POST.get('admin_city', '').strip()
                    admin_state = request.POST.get('admin_state', '').strip()
                    admin_postal_code = request.POST.get('admin_postal_code', '').strip()
                    admin_country = request.POST.get('admin_country', 'Nepal').strip()

                    # Set user's full name
                    if name:
                        name_parts = name.split(' ', 1)
                        user.first_name = name_parts[0]
                        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
                        user.save()

                    AdminProfile.objects.create(
                        user=user,
                        name=name,
                        contact_no=contact_no,
                        address=address,
                        city=admin_city,
                        state=admin_state,
                        postal_code=admin_postal_code,
                        country=admin_country,
                        email=email
                    )
                    
                else:
                    # For donors, create comprehensive profile
                    name = request.POST.get('name', '').strip()
                    blood_group = request.POST.get('blood_group')
                    contact_no = request.POST.get('contact_no', '').strip()
                    address = request.POST.get('address', '').strip()
                    date_of_birth = request.POST.get('date_of_birth')
                    gender = request.POST.get('gender', 'M')
                    weight = request.POST.get('weight', '60.0')
                    
                    # Set user's full name
                    if name:
                        name_parts = name.split(' ', 1)
                        user.first_name = name_parts[0]
                        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
                        user.save()

                    # Parse date of birth
                    try:
                        if date_of_birth:
                            dob = date.fromisoformat(date_of_birth)
                        else:
                            dob = date(1990, 1, 1)  # Default
                    except ValueError:
                        dob = date(1990, 1, 1)  # Default if invalid date
                    
                    # Parse weight
                    try:
                        weight_float = float(weight)
                        if weight_float < 45 or weight_float > 200:
                            weight_float = 60.0  # Default if out of range
                    except (ValueError, TypeError):
                        weight_float = 60.0  # Default if invalid

                    # Get location fields
                    city = request.POST.get('city', '').strip()
                    state = request.POST.get('state', '').strip()
                    postal_code = request.POST.get('postal_code', '').strip()
                    country = request.POST.get('country', 'Nepal').strip()

                    # Create donor profile
                    Donor.objects.create(
                        user=user,
                        blood_group=blood_group,
                        phone_number=contact_no,
                        address=address,
                        city=city,
                        state=state,
                        postal_code=postal_code,
                        country=country,
                        date_of_birth=dob,
                        gender=gender,
                        weight=weight_float,
                        is_eligible=True
                    )
                
                # Send welcome email
                try:
                    subject = 'Welcome to Blood Donation System'
                    message = f"""
Dear {username},

Welcome to the Blood Donation Management System!

Your {role} account has been successfully created.

Login Details:
- Username: {username}
- Role: {role.title()}

You can access the system at: http://localhost:8000/accounts/login/

Thank you for joining our mission to save lives through blood donation.

Best regards,
Blood Donation System Team
                    """

                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Failed to send welcome email: {e}")

                login(request, user)
                messages.success(request, f'Registration successful! Welcome to the Blood Donation System.')
                if role == 'admin':
                    return redirect('admin_panel:dashboard')
                else:
                    return redirect('donor:donor_dashboard')
                    
        except IntegrityError:
            return render(request, 'accounts/register.html', {'error': 'Username already exists.'})
        except Exception as e:
            return render(request, 'accounts/register.html', {'error': f'Registration failed: {str(e)}'})
    
    return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        role = request.POST.get('role')
        
        # Basic validation
        if not username or not password:
            return render(request, 'accounts/login.html', {
                'error': 'Please enter both username and password.',
                'username': username,
                'role': role
            })
        
        if not role:
            return render(request, 'accounts/login.html', {
                'error': 'Please select your role.',
                'username': username
            })
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                return render(request, 'accounts/login.html', {
                    'error': 'Your account has been deactivated. Please contact support.',
                    'username': username,
                    'role': role
                })
            
            # Check role compatibility
            if role == 'admin' and user.is_staff:
                login(request, user)
                return redirect('admin_panel:dashboard')
            elif role == 'donor' and not user.is_staff:
                # Check if donor profile exists
                try:
                    user.donor  # Just check if donor profile exists
                    login(request, user)
                    return redirect('donor:donor_dashboard')
                except Donor.DoesNotExist:
                    return render(request, 'accounts/login.html', {
                        'error': 'Donor profile not found. Please contact support or register again.',
                        'username': username,
                        'role': role
                    })
            else:
                return render(request, 'accounts/login.html', {
                    'error': 'Selected role does not match your account type.',
                    'username': username,
                    'role': role
                })
        else:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid username or password.',
                'username': username,
                'role': role
            })
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    """Enhanced logout with proper cleanup"""
    logout(request)
    return redirect('accounts:login')

class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view with better error handling"""
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')

    def form_valid(self, form):
        """Override to add custom logic and better error handling"""
        email = form.cleaned_data['email']

        # Check if user exists with this email
        try:
            user = User.objects.get(email=email)
            # Send the email
            result = super().form_valid(form)
            messages.success(
                self.request,
                f'Password reset instructions have been sent to {email}'
            )
            return result
        except User.DoesNotExist:
            # For security, we don't reveal if email exists or not
            messages.success(
                self.request,
                'If an account with that email exists, password reset instructions have been sent.'
            )
            return redirect(self.success_url)
        except Exception as e:
            # Handle email sending errors
            messages.error(
                self.request,
                'There was an error sending the password reset email. Please try again later.'
            )
            return self.form_invalid(form)
