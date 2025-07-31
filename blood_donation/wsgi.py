"""
WSGI config for blood_donation project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blood_donation.settings')
application = get_wsgi_application()
