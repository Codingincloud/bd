# Blood Donor Information Management System (BDIMS)

A comprehensive web-based Blood Donation Management System built with Django for managing blood donations, donors, and emergency blood requests.

## Features

### For Donors
- User registration and secure authentication
- Personalized dashboard with donation statistics
- Health metrics tracking (hemoglobin, blood pressure, weight)
- Donation scheduling system
- Emergency blood request alerts
- Interactive map for location updates
- Blood inventory checker

### For Administrators
- Admin dashboard with analytics
- Donor management and tracking
- Donation request approval workflow
- Blood inventory management
- Emergency request creation
- System-wide notifications
- Report generation

## Technology Stack

- **Backend**: Django 5.2.8
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Maps**: Leaflet.js for interactive location selection
- **Charts**: Chart.js for visualizations

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 13+

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Codingincloud/BDIMS.git
cd BDIMS
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure database**

Edit `blood_donation/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bdims_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Populate initial data (optional)**
```bash
python manage.py populate_hospitals
```

7. **Run development server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`

## Project Structure

```
BDIMS/
├── accounts/           # Authentication system
├── admin_panel/        # Admin dashboard
├── donor/             # Donor features
├── blood_donation/    # Project settings
├── static/            # CSS, JS, images
├── templates/         # HTML templates
├── utils/             # Helper functions
└── requirements.txt   # Dependencies
```

## User Roles

**Donor**
- Register and manage profile
- Schedule donations
- Track health metrics
- Respond to emergencies

**Admin**
- Manage donors and requests
- Control blood inventory
- Create emergency requests
- View analytics

## Key Features

### Interactive Map
- Click-to-select location
- GPS auto-detection
- Search functionality
- Reverse geocoding

### Health Tracking
- Hemoglobin monitoring
- Blood pressure tracking
- Eligibility checking

### Emergency System
- Real-time alerts
- Blood type matching
- Hospital integration

## Security

- CSRF protection
- Secure password hashing
- Role-based access control
- Session management

## Development

Run in debug mode for development:
```bash
# In settings.py
DEBUG = True
```

## Production Deployment

1. Set `DEBUG = False`
2. Configure `ALLOWED_HOSTS`
3. Set strong `SECRET_KEY`
4. Use HTTPS
5. Collect static files:
```bash
python manage.py collectstatic
```
6. Use production WSGI server (gunicorn/uWSGI)

## License

Academic project - 5th Semester, 2025

## Support

For issues: [GitHub Issues](https://github.com/Codingincloud/BDIMS/issues)

---

**Note**: This is an academic/development project. Ensure proper security audits before production use.
