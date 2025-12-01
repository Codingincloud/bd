# Blood Donor Information Management System (BDIMS)

A comprehensive web-based Blood Donation Management System built with Django for managing blood donations, donors, and emergency blood requests.

## Quick Start

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/BDIMS.git
cd BDIMS
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run database migrations**
```bash
python manage.py migrate
```

4. **Collect static files (CSS/JS)**
```bash
python manage.py collectstatic --noinput
```

5. **Create admin user (optional)**
```bash
python manage.py createsuperuser
```

6. **Start the server**
```bash
python manage.py runserver
```

7. **Open in browser**
```
http://127.0.0.1:8000/
```

That's it! CSS and all features will work automatically in any browser.

---

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
- **Database**: SQLite (default) / PostgreSQL (optional)
- **Frontend**: HTML5, CSS3, JavaScript
- **Maps**: Leaflet.js for interactive location selection
- **Charts**: Chart.js for visualizations

## Configuration

The project is pre-configured to work with SQLite database. For PostgreSQL, edit `blood_donation/settings.py`:

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

## Project Structure

```
BDIMS/
├── accounts/           # Authentication system
├── admin_panel/        # Admin dashboard
├── donor/             # Donor features
├── blood_donation/    # Project settings
├── static/            # CSS, JS files (source)
├── staticfiles/       # Collected static files (auto-generated)
├── templates/         # HTML templates
├── utils/             # Helper functions
└── requirements.txt   # Dependencies
```

## Troubleshooting

### CSS Not Loading?
```bash
python manage.py collectstatic --noinput --clear
```
Then press `Ctrl+F5` in your browser to hard refresh.

### Port Already in Use?
```bash
python manage.py runserver 8001
```

---

## License

Academic project - 5th Semester, 2025

## Support

For issues or questions, please open an issue on GitHub.

**Note**: This is an academic project. Ensure proper security audits before production use.
