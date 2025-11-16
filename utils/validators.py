"""
Custom validators for the blood donation system
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date, datetime, timedelta
from django.utils import timezone

class BloodDonationValidators:
    """Collection of validators for blood donation system"""
    
    @staticmethod
    def validate_phone_number(phone):
        """
        Validate phone number format
        Accepts various formats: +977-1-XXXXXXX, 01-XXXXXXX, 98XXXXXXXX
        """
        if not phone:
            raise ValidationError(_("Phone number is required."))
        
        # Remove spaces and dashes for validation
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check for valid patterns
        patterns = [
            r'^\+977[0-9]{8,10}$',  # +977XXXXXXXXX
            r'^977[0-9]{8,10}$',    # 977XXXXXXXXX
            r'^0[0-9]{8,9}$',       # 0XXXXXXXXX
            r'^[0-9]{8,10}$',       # XXXXXXXXX
        ]
        
        if not any(re.match(pattern, clean_phone) for pattern in patterns):
            raise ValidationError(
                _("Please enter a valid phone number. Examples: +977-1-4567890, 01-4567890, 9841234567")
            )
        
        return clean_phone
    
    @staticmethod
    def validate_blood_group(blood_group):
        """Validate blood group"""
        valid_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        
        if blood_group not in valid_groups:
            raise ValidationError(
                _("Invalid blood group. Must be one of: %(groups)s") % {
                    'groups': ', '.join(valid_groups)
                }
            )
        
        return blood_group
    
    @staticmethod
    def validate_age_for_donation(birth_date):
        """
        Validate if person is eligible age for blood donation (18-65)
        """
        if not birth_date:
            raise ValidationError(_("Date of birth is required."))
        
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        if age < 18:
            raise ValidationError(
                _("You must be at least 18 years old to donate blood. Current age: %(age)d") % {'age': age}
            )
        
        if age > 65:
            raise ValidationError(
                _("Blood donation is not recommended for people over 65. Current age: %(age)d") % {'age': age}
            )
        
        return age
    
    @staticmethod
    def validate_weight_for_donation(weight):
        """
        Validate weight for blood donation (minimum 45kg)
        """
        if not weight:
            raise ValidationError(_("Weight is required for blood donation eligibility."))
        
        if weight < 45:
            raise ValidationError(
                _("Minimum weight for blood donation is 45kg. Current weight: %(weight)skg") % {'weight': weight}
            )
        
        if weight > 200:
            raise ValidationError(
                _("Please verify weight. Entered weight seems unusually high: %(weight)skg") % {'weight': weight}
            )
        
        return weight
    
    @staticmethod
    def validate_last_donation_date(last_donation_date, gender='M'):
        """
        Validate last donation date for eligibility
        Men: 3 months gap, Women: 4 months gap
        """
        if not last_donation_date:
            return True  # No previous donation
        
        today = date.today()
        gap_required = 120 if gender == 'F' else 90  # days
        
        days_since_last = (today - last_donation_date).days
        
        if days_since_last < gap_required:
            days_remaining = gap_required - days_since_last
            raise ValidationError(
                _("You must wait %(days)d more days before your next donation. "
                  "Last donation was %(last_date)s (%(days_ago)d days ago).") % {
                    'days': days_remaining,
                    'last_date': last_donation_date.strftime('%B %d, %Y'),
                    'days_ago': days_since_last
                }
            )
        
        return True
    
    @staticmethod
    def validate_emergency_request_time(required_by):
        """
        Validate emergency request timing
        """
        if not required_by:
            raise ValidationError(_("Required by date/time is mandatory for emergency requests."))
        
        # Convert to datetime if it's a string
        if isinstance(required_by, str):
            try:
                required_by = datetime.strptime(required_by, '%Y-%m-%dT%H:%M')
                required_by = timezone.make_aware(required_by)
            except ValueError:
                raise ValidationError(_("Invalid date/time format. Use YYYY-MM-DD HH:MM format."))
        
        now = timezone.now()
        
        # Check if time is in the past
        if required_by <= now:
            raise ValidationError(_("Required by time must be in the future."))
        
        # Check if time is too far in the future (more than 30 days)
        max_future = now + timedelta(days=30)
        if required_by > max_future:
            raise ValidationError(_("Emergency requests cannot be scheduled more than 30 days in advance."))
        
        return required_by
    
    @staticmethod
    def validate_donation_request_date(requested_date):
        """
        Validate donation request date
        """
        if not requested_date:
            raise ValidationError(_("Donation date is required."))
        
        today = date.today()
        
        # Check if date is in the past
        if requested_date < today:
            raise ValidationError(_("Donation date cannot be in the past."))
        
        # Check if date is too far in the future (more than 90 days)
        max_future = today + timedelta(days=90)
        if requested_date > max_future:
            raise ValidationError(_("Donation requests cannot be scheduled more than 90 days in advance."))
        
        return requested_date
    
    @staticmethod
    def validate_email_format(email):
        """
        Enhanced email validation
        """
        if not email:
            return email  # Email is optional in most cases
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValidationError(_("Please enter a valid email address."))
        
        # Check for common typos
        common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        domain = email.split('@')[1].lower()
        
        # Suggest corrections for common typos
        suggestions = {
            'gmial.com': 'gmail.com',
            'gmai.com': 'gmail.com',
            'yahooo.com': 'yahoo.com',
            'hotmial.com': 'hotmail.com',
        }
        
        if domain in suggestions:
            raise ValidationError(
                _("Did you mean %(suggestion)s? Please check your email address.") % {
                    'suggestion': email.replace(domain, suggestions[domain])
                }
            )
        
        return email
    
    @staticmethod
    def validate_medical_conditions(conditions):
        """
        Validate medical conditions input
        """
        if not conditions:
            return conditions
        
        # Check for conditions that may disqualify donation
        disqualifying_conditions = [
            'hiv', 'aids', 'hepatitis', 'cancer', 'heart disease',
            'diabetes', 'tuberculosis', 'malaria', 'syphilis'
        ]
        
        conditions_lower = conditions.lower()
        found_conditions = [cond for cond in disqualifying_conditions if cond in conditions_lower]
        
        if found_conditions:
            raise ValidationError(
                _("The following medical conditions may affect donation eligibility: %(conditions)s. "
                  "Please consult with medical staff.") % {
                    'conditions': ', '.join(found_conditions)
                }
            )
        
        return conditions

def clean_and_validate_form_data(form_data, validation_rules):
    """
    Generic function to clean and validate form data
    
    Args:
        form_data (dict): Form data to validate
        validation_rules (dict): Dictionary of field_name: validator_function
    
    Returns:
        tuple: (cleaned_data, errors)
    """
    cleaned_data = {}
    errors = {}
    
    for field_name, validator in validation_rules.items():
        if field_name in form_data:
            try:
                cleaned_data[field_name] = validator(form_data[field_name])
            except ValidationError as e:
                errors[field_name] = str(e)
        else:
            # Check if field is required
            if hasattr(validator, 'required') and validator.required:
                errors[field_name] = f"{field_name.replace('_', ' ').title()} is required."
    
    return cleaned_data, errors
