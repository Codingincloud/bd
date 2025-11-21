# Blood Donor Information Management System (BDIMS)

## Project Overview
A comprehensive web-based Blood Donation Management System built with Django 5.2.8, designed for managing blood donations, donors, blood centers, and emergency blood requests in Nepal.

## Features

### For Donors
- ✅ User registration and authentication with role-based access
- ✅ Personalized dashboard with donation statistics
- ✅ Health metrics tracking (hemoglobin, blood pressure, weight)
- ✅ Donation scheduling with time slot selection
- ✅ Complete donation history with detailed records
- ✅ Blood center locator with 11 real Nepal blood centers
- ✅ Emergency blood request alerts
- ✅ Blood inventory availability checker
- ✅ Lives saved impact counter
- ✅ Pre-donation checklist and educational tips

### For Administrators
- ✅ Comprehensive admin dashboard with analytics
- ✅ Donor tracking and management
- ✅ Donation request approval workflow
- ✅ Blood inventory management with units tracking
- ✅ Emergency request creation and management
- ✅ Donor detail views with complete history
- ✅ System-wide notifications
- ✅ Blood group distribution analytics
- ✅ CSV export functionality
- ✅ PDF report generation (ReportLab)

## Technology Stack

- **Backend**: Django 5.2.8
- **Database**: PostgreSQL (with SQLite fallback)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js 4.4.0
- **PDF Generation**: ReportLab
- **Geocoding**: GeoPy
- **Authentication**: Django Auth with custom middleware

## Installation & Setup

### Prerequisites
- Python 3.12 or higher
- PostgreSQL 13+ (optional, SQLite fallback available)
- pip package manager

### Step 1: Clone the Repository
```bash
git clone https://github.com/Codingincloud/blood-donation-system.git
cd BDIMS
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` file:
```env
# For PostgreSQL (recommended for production)
USE_SQLITE=False
DB_NAME=blood_donation_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# For SQLite (development/testing)
USE_SQLITE=True
```

### Step 4: Setup Database

**For PostgreSQL:**
```bash
# Create database
createdb blood_donation_db

# Run migrations
python manage.py migrate
```

**For SQLite (Development):**
```bash
# Just run migrations
python manage.py migrate
```

### Step 5: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 6: Run Development Server
```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000/`

## Database Configuration

The system supports both PostgreSQL and SQLite:

### PostgreSQL (Production)
Set `USE_SQLITE=False` in `.env` and configure:
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT

### SQLite (Development)
Set `USE_SQLITE=True` in `.env` for automatic SQLite fallback.

## Project Structure

```
BDIMS/
├── accounts/           # User authentication module
├── admin_panel/        # Admin dashboard and management
├── donor/             # Donor features and views
├── blood_donation/    # Main project settings
├── static/            # Static files (CSS, JS, images)
├── templates/         # HTML templates
├── utils/             # Utility functions (geocoding, notifications)
├── requirements.txt   # Python dependencies
├── manage.py         # Django management script
└── .env              # Environment configuration
```

## Key Features Details

### Health Metrics Tracking
- Hemoglobin level monitoring
- Blood pressure tracking
- Weight recording
- Eligibility status calculation

### Donation Management
- Request approval workflow
- Automated eligibility checking
- 90-day donation interval enforcement
- Units donated tracking

### Blood Inventory
- Real-time stock levels
- Reserved units tracking
- Blood group availability
- 30-day donation trends

### Emergency Requests
- Urgency level classification
- Blood group compatibility
- Hospital contact information
- Active request management

## User Roles

1. **Donor**
   - Register and manage profile
   - Schedule donations
   - Track health metrics
   - View donation history

2. **Admin**
   - Manage donors and requests
   - Control blood inventory
   - Create emergency requests
   - Generate reports

## Security Features

- ✅ CSRF protection
- ✅ XSS filtering
- ✅ Secure session management
- ✅ Password validation
- ✅ Role-based access control
- ✅ HTTP security headers

## Testing

The system includes comprehensive testing:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test donor
python manage.py test admin_panel
```

## Development

### Running in Debug Mode
```env
DJANGO_DEBUG=True
```

### Logging
Logs are configured for:
- Console output (INFO level)
- File logging (debug.log)
- Database query logging (DEBUG mode)

## Deployment

### Production Checklist
- [ ] Set `DJANGO_DEBUG=False`
- [ ] Configure PostgreSQL
- [ ] Set strong `SECRET_KEY`
- [ ] Enable SSL (`SECURE_SSL_REDIRECT=True`)
- [ ] Configure ALLOWED_HOSTS
- [ ] Setup SMTP email backend
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Use gunicorn/uwsgi for WSGI
- [ ] Setup nginx for static files
- [ ] Enable HSTS headers

## Blood Centers

System includes 11 real blood centers across Nepal:
- Kathmandu (4 centers)
- Lalitpur (2 centers)
- Bhaktapur (1 center)
- Pokhara (1 center)
- Bharatpur (1 center)
- Birgunj (1 center)
- Biratnagar (1 center)

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is developed as a 5th semester academic project.

## Support

For issues and questions:
- GitHub Issues: [blood-donation-system/issues](https://github.com/Codingincloud/blood-donation-system/issues)
- Email: support@example.com

## Credits

- Developer: cloud
- Institution☁️
- Semester: 5th
- Year: 2025

## Version History

- **v1.0.0** (November 2025)
  - Initial release
  - Complete donor management
  - Admin dashboard
  - Health metrics tracking
  - Emergency requests
  - Blood inventory system

---

**Note**: This is a development/academic project. For production use, ensure proper security audits and compliance with healthcare regulations.
