from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction, DatabaseError
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
import logging

# Set up logging
logger = logging.getLogger(__name__)

def validate_registration_data(data):
    """Validate registration form data with comprehensive error checking"""
    errors = []

    try:
        # Username validation
        username = data.get('username', '').strip()
        if not username:
            errors.append('Username is required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        elif len(username) > 150:
            errors.append('Username must be less than 150 characters.')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores.')
        else:
            try:
                if User.objects.filter(username=username).exists():
                    errors.append('Username already exists.')
            except DatabaseError as e:
                logger.error(f"Database error checking username: {e}")
                errors.append('Database error occurred. Please try again.')

        # Password validation
        password = data.get('password', '')
        if not password:
            errors.append('Password is required.')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        elif len(password) > 128:
            errors.append('Password must be less than 128 characters.')
        elif not re.search(r'[A-Za-z]', password):
            errors.append('Password must contain at least one letter.')
        elif not re.search(r'[0-9]', password):
            errors.append('Password must contain at least one number.')

        # Email validation
        email = data.get('email', '').strip()
        if not email:
            errors.append('Email address is required.')
        else:
            try:
                validate_email(email)
                try:
                    if User.objects.filter(email=email).exists():
                        errors.append('Email address already registered.')
                except DatabaseError as e:
                    logger.error(f"Database error checking email: {e}")
                    errors.append('Database error occurred. Please try again.')
            except ValidationError:
                errors.append('Please enter a valid email address.')

        # Role validation
        role = data.get('role')
        if role not in ['donor', 'admin']:
            errors.append('Please select a valid role.')

        # Role-specific validation
        if role == 'donor':
            # Blood group validation
            blood_group = data.get('blood_group')
            valid_blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
            if not blood_group:
                errors.append('Blood group is required for donors.')
            elif blood_group not in valid_blood_groups:
                errors.append('Please select a valid blood group.')

            # Contact number validation
            contact_no = data.get('contact_no', '').strip()
            if not contact_no:
                errors.append('Contact number is required.')
            elif not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', contact_no):
                errors.append('Please enter a valid contact number (10-15 digits).')

            # Date of birth validation
            date_of_birth = data.get('date_of_birth')
            if date_of_birth:
                try:
                    dob = date.fromisoformat(date_of_birth)
                    today = date.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    if age < 18:
                        errors.append('You must be at least 18 years old to donate blood.')
                    elif age > 65:
                        errors.append('Blood donors must be under 65 years old.')
                except ValueError:
                    errors.append('Please enter a valid date of birth.')

            # Weight validation
            weight = data.get('weight')
            if weight:
                try:
                    weight_float = float(weight)
                    if weight_float < 45:
                        errors.append('Minimum weight for blood donation is 45 kg.')
                    elif weight_float > 200:
                        errors.append('Please enter a valid weight.')
                except (ValueError, TypeError):
                    errors.append('Please enter a valid weight.')

        elif role == 'admin':
            # Admin-specific validation
            admin_name = data.get('admin_name', '').strip()
            if not admin_name:
                errors.append('Full name is required for admin accounts.')
            elif len(admin_name) < 2:
                errors.append('Please enter your full name.')

            admin_contact = data.get('admin_contact_no', '').strip()
            if not admin_contact:
                errors.append('Contact number is required for admin accounts.')
            elif not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', admin_contact):
                errors.append('Please enter a valid contact number.')

    except Exception as e:
        logger.error(f"Unexpected error in validation: {e}")
        errors.append('An unexpected error occurred during validation. Please try again.')

    return errors

def register_view(request):
    """Enhanced registration view with comprehensive error handling and PostgreSQL support"""
    if request.method == 'POST':
        try:
            # Validate form data
            errors = validate_registration_data(request.POST)
            if errors:
                logger.warning(f"Registration validation failed: {errors}")
                return render(request, 'accounts/register.html', {
                    'errors': errors,
                    'form_data': request.POST
                })

            username = request.POST.get('username').strip()
            password = request.POST.get('password')
            email = request.POST.get('email').strip()
            role = request.POST.get('role')

            logger.info(f"Attempting to register user: {username} with role: {role}")

            # Use atomic transaction for data consistency
            with transaction.atomic():
                # Create user account
                try:
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        is_active=True
                    )
                    logger.info(f"User {username} created successfully")
                except IntegrityError as e:
                    logger.error(f"IntegrityError creating user {username}: {e}")
                    return render(request, 'accounts/register.html', {
                        'error': 'Username or email already exists. Please choose different credentials.',
                        'form_data': request.POST
                    })

                if role == 'admin':
                    # Set admin permissions
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()

                    # Get admin-specific data
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

                    # Create admin profile
                    try:
                        admin_profile = AdminProfile.objects.create(
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
                        logger.info(f"Admin profile created for user {username}")
                    except Exception as e:
                        logger.error(f"Error creating admin profile for {username}: {e}")
                        raise

                elif role == 'donor':
                    # Get donor-specific data
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

                    # Parse and validate date of birth
                    try:
                        if date_of_birth:
                            dob = date.fromisoformat(date_of_birth)
                        else:
                            dob = date(1990, 1, 1)  # Default
                    except ValueError:
                        logger.warning(f"Invalid date of birth for {username}: {date_of_birth}")
                        dob = date(1990, 1, 1)  # Default if invalid date

                    # Parse and validate weight
                    try:
                        weight_float = float(weight)
                        if weight_float < 45 or weight_float > 200:
                            weight_float = 60.0  # Default if out of range
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid weight for {username}: {weight}")
                        weight_float = 60.0  # Default if invalid

                    # Get location fields
                    city = request.POST.get('city', '').strip()
                    state = request.POST.get('state', '').strip()
                    postal_code = request.POST.get('postal_code', '').strip()
                    country = request.POST.get('country', 'Nepal').strip()

                    # Create donor profile
                    try:
                        donor_profile = Donor.objects.create(
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
                        logger.info(f"Donor profile created for user {username}")
                    except Exception as e:
                        logger.error(f"Error creating donor profile for {username}: {e}")
                        raise

                # Send welcome email (non-blocking)
                try:
                    subject = 'Welcome to Blood Donation System'
                    message = f"""
Dear {user.first_name or username},

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
                    logger.info(f"Welcome email sent to {email}")
                except Exception as e:
                    logger.warning(f"Failed to send welcome email to {email}: {e}")

                # Log the user in
                login(request, user)
                messages.success(request, f'Registration successful! Welcome to the Blood Donation System, {user.first_name or username}.')

                # Redirect based on role
                if role == 'admin':
                    logger.info(f"Admin {username} registered and logged in successfully")
                    return redirect('admin_panel:dashboard')
                else:
                    logger.info(f"Donor {username} registered and logged in successfully")
                    return redirect('donor:donor_dashboard')

        except DatabaseError as e:
            logger.error(f"Database error during registration: {e}")
            return render(request, 'accounts/register.html', {
                'error': 'Database connection error. Please try again later.',
                'form_data': request.POST
            })
        except Exception as e:
            logger.error(f"Unexpected error during registration: {e}")
            return render(request, 'accounts/register.html', {
                'error': f'Registration failed: {str(e)}. Please try again.',
                'form_data': request.POST
            })

    return render(request, 'accounts/register.html')

def login_view(request):
    """Enhanced login view with comprehensive error handling and role validation"""
    if request.method == 'POST':
        try:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            role = request.POST.get('role')

            logger.info(f"Login attempt for username: {username}, role: {role}")

            # Basic validation
            if not username or not password:
                logger.warning(f"Login failed - missing credentials for {username}")
                return render(request, 'accounts/login.html', {
                    'error': 'Please enter both username and password.',
                    'username': username,
                    'role': role
                })

            if not role:
                logger.warning(f"Login failed - no role selected for {username}")
                return render(request, 'accounts/login.html', {
                    'error': 'Please select your role.',
                    'username': username
                })

            if role not in ['admin', 'donor']:
                logger.warning(f"Login failed - invalid role {role} for {username}")
                return render(request, 'accounts/login.html', {
                    'error': 'Please select a valid role.',
                    'username': username
                })

            # Authenticate user
            try:
                user = authenticate(request, username=username, password=password)
            except DatabaseError as e:
                logger.error(f"Database error during authentication for {username}: {e}")
                return render(request, 'accounts/login.html', {
                    'error': 'Database connection error. Please try again later.',
                    'username': username,
                    'role': role
                })

            if user is not None:
                # Check if account is active
                if not user.is_active:
                    logger.warning(f"Login failed - inactive account for {username}")
                    return render(request, 'accounts/login.html', {
                        'error': 'Your account has been deactivated. Please contact support.',
                        'username': username,
                        'role': role
                    })

                # Role-based authentication and profile verification
                if role == 'admin':
                    if user.is_staff:
                        # Verify admin profile exists
                        try:
                            admin_profile = user.adminprofile
                            login(request, user)
                            logger.info(f"Admin {username} logged in successfully")
                            messages.success(request, f'Welcome back, {user.first_name or username}!')
                            return redirect('admin_panel:dashboard')
                        except AdminProfile.DoesNotExist:
                            logger.error(f"Admin profile not found for {username}")
                            return render(request, 'accounts/login.html', {
                                'error': 'Admin profile not found. Please contact support.',
                                'username': username,
                                'role': role
                            })
                        except Exception as e:
                            logger.error(f"Error accessing admin profile for {username}: {e}")
                            return render(request, 'accounts/login.html', {
                                'error': 'Error accessing admin profile. Please try again.',
                                'username': username,
                                'role': role
                            })
                    else:
                        logger.warning(f"Login failed - user {username} is not admin but selected admin role")
                        return render(request, 'accounts/login.html', {
                            'error': 'You do not have admin privileges. Please select the correct role.',
                            'username': username,
                            'role': role
                        })

                elif role == 'donor':
                    if not user.is_staff:
                        # Verify donor profile exists
                        try:
                            donor_profile = user.donor
                            login(request, user)
                            logger.info(f"Donor {username} logged in successfully")
                            messages.success(request, f'Welcome back, {user.first_name or username}!')
                            return redirect('donor:donor_dashboard')
                        except Donor.DoesNotExist:
                            logger.error(f"Donor profile not found for {username}")
                            return render(request, 'accounts/login.html', {
                                'error': 'Donor profile not found. Please contact support or register again.',
                                'username': username,
                                'role': role
                            })
                        except Exception as e:
                            logger.error(f"Error accessing donor profile for {username}: {e}")
                            return render(request, 'accounts/login.html', {
                                'error': 'Error accessing donor profile. Please try again.',
                                'username': username,
                                'role': role
                            })
                    else:
                        logger.warning(f"Login failed - admin user {username} selected donor role")
                        return render(request, 'accounts/login.html', {
                            'error': 'Admin accounts cannot login as donors. Please select the correct role.',
                            'username': username,
                            'role': role
                        })
            else:
                logger.warning(f"Login failed - invalid credentials for {username}")
                return render(request, 'accounts/login.html', {
                    'error': 'Invalid username or password. Please check your credentials.',
                    'username': username,
                    'role': role
                })

        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            return render(request, 'accounts/login.html', {
                'error': 'An unexpected error occurred. Please try again.',
                'username': request.POST.get('username', ''),
                'role': request.POST.get('role', '')
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
