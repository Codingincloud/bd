"""
Constants for Blood Donation Management System
Define all magic numbers and commonly used values
"""

# Donation Eligibility Rules
MINIMUM_DONATION_INTERVAL_DAYS = 56  # 8 weeks between donations
MINIMUM_DONOR_AGE = 18
MAXIMUM_DONOR_AGE = 65
MINIMUM_DONOR_WEIGHT_KG = 45
MAXIMUM_DONOR_WEIGHT_KG = 200

# Health Metrics Ranges
HEMOGLOBIN_MIN_MALE = 13.0  # g/dL
HEMOGLOBIN_MIN_FEMALE = 12.5  # g/dL
HEMOGLOBIN_MAX = 18.0  # g/dL

BLOOD_PRESSURE_SYSTOLIC_MIN = 90
BLOOD_PRESSURE_SYSTOLIC_MAX = 180
BLOOD_PRESSURE_DIASTOLIC_MIN = 60
BLOOD_PRESSURE_DIASTOLIC_MAX = 100

HEART_RATE_MIN = 50  # bpm
HEART_RATE_MAX = 100  # bpm

TEMPERATURE_MIN = 36.1  # Celsius
TEMPERATURE_MAX = 37.2  # Celsius

# BMI Categories
BMI_UNDERWEIGHT = 18.5
BMI_NORMAL = 25.0
BMI_OVERWEIGHT = 30.0

# Blood Inventory Thresholds
INVENTORY_CRITICAL_THRESHOLD = 0
INVENTORY_LOW_THRESHOLD = 5
INVENTORY_MEDIUM_THRESHOLD = 15

# Units
STANDARD_DONATION_UNITS = 1.0  # Units per donation (in liters or standard units)
ML_TO_UNITS_CONVERSION = 450  # 1 unit = 450ml approximately

# Blood Compatibility Matrix
BLOOD_COMPATIBILITY = {
    'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],  # Universal donor
    'O+': ['O+', 'A+', 'B+', 'AB+'],
    'A-': ['A-', 'A+', 'AB-', 'AB+'],
    'A+': ['A+', 'AB+'],
    'B-': ['B-', 'B+', 'AB-', 'AB+'],
    'B+': ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+'],  # Universal recipient for donation, can only donate to AB+
}

# Can receive from (reverse lookup)
CAN_RECEIVE_FROM = {
    'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],  # Universal recipient
    'AB-': ['O-', 'A-', 'B-', 'AB-'],
    'A+': ['O-', 'O+', 'A-', 'A+'],
    'A-': ['O-', 'A-'],
    'B+': ['O-', 'O+', 'B-', 'B+'],
    'B-': ['O-', 'B-'],
    'O+': ['O-', 'O+'],
    'O-': ['O-'],
}

# Emergency Request Urgency Response Times (hours)
URGENCY_RESPONSE_TIME = {
    'critical': 2,   # < 2 hours
    'high': 24,      # < 24 hours
    'medium': 72,    # 24-72 hours
    'low': 168,      # 1 week
}

# Notification Settings
NOTIFICATION_CLEANUP_DAYS = 30  # Days after which to clean up old notifications
NOTIFICATION_BATCH_SIZE = 100  # Batch size for bulk notification creation

# Activity Scoring
ACTIVITY_SCORE_PER_REQUEST = 2
ACTIVITY_SCORE_PER_DONATION = 5
ACTIVITY_HIGH_THRESHOLD = 10
ACTIVITY_MEDIUM_THRESHOLD = 5

# Distance Calculations
EARTH_RADIUS_KM = 6371  # Earth's radius in kilometers for Haversine formula
DEFAULT_SEARCH_RADIUS_KM = 50  # Default radius for location-based donor search
MAX_SEARCH_RADIUS_KM = 200  # Maximum search radius

# Pagination
DEFAULT_PAGE_SIZE = 20
DONATION_HISTORY_PAGE_SIZE = 10
REQUEST_LIST_PAGE_SIZE = 25
ADMIN_DASHBOARD_RECENT_COUNT = 10

# Session Settings
SESSION_COOKIE_AGE_HOURS = 24

# File Upload
MAX_PROFILE_IMAGE_SIZE_MB = 5
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']

# Status Choices Constants
STATUS_PENDING = 'pending'
STATUS_APPROVED = 'approved'
STATUS_COMPLETED = 'completed'
STATUS_CANCELLED = 'cancelled'
STATUS_REJECTED = 'rejected'
STATUS_ACTIVE = 'active'
STATUS_FULFILLED = 'fulfilled'
STATUS_EXPIRED = 'expired'

# Time Formats
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DISPLAY_DATE_FORMAT = '%B %d, %Y'
DISPLAY_DATETIME_FORMAT = '%B %d, %Y at %I:%M %p'
