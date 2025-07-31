"""
ASGI config for blood_donation project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blood_donation.settings')
application = get_asgi_application()
