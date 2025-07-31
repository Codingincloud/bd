"""
Django management command to populate test data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from donor.models import Donor, DonationCenter, DonationRequest, DonationHistory, EmergencyRequest, HealthMetrics
from admin_panel.models import AdminProfile, SystemNotification, UserNotification


class Command(BaseCommand):
    help = 'Populate the database with comprehensive test data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🩸 CREATING COMPREHENSIVE TEST DATA'))
        self.stdout.write('=' * 50)
        
        self.create_admin_users()
        self.create_donor_users()
        self.create_donation_centers()
        self.create_sample_data()
        self.create_notifications()
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('✅ TEST DATA CREATION COMPLETE!'))
        self.stdout.write(f'📊 Summary:')
        self.stdout.write(f'   👨‍💼 Admins: {AdminProfile.objects.count()}')
        self.stdout.write(f'   🩸 Donors: {Donor.objects.count()}')
        self.stdout.write(f'   🏥 Centers: {DonationCenter.objects.count()}')
        self.stdout.write(f'   📋 Requests: {DonationRequest.objects.count()}')
        self.stdout.write(f'   📊 History: {DonationHistory.objects.count()}')
        self.stdout.write(f'   📈 Metrics: {HealthMetrics.objects.count()}')
        self.stdout.write(f'   🔔 Notifications: {SystemNotification.objects.count()}')
        
        self.stdout.write('\n🚀 Ready to test the system!')
        self.stdout.write('🔐 Login credentials:')
        self.stdout.write('   Admin: admin / admin123')
        self.stdout.write('   Admin2: admin2 / admin123')
        self.stdout.write('   Donors: donor1, donor2, donor3, donor4, donor5 / donor123')

    def create_admin_users(self):
        """Create admin users with profiles"""
        self.stdout.write('🔧 Creating Admin Users...')
        
        admin_data = [
            {
                'username': 'admin',
                'email': 'admin@bloodbank.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'password': 'admin123',
                'department': 'Administration',
                'phone': '+977-1-4444444',
                'is_superuser': True
            },
            {
                'username': 'admin2',
                'email': 'medical@bloodbank.com',
                'first_name': 'Medical',
                'last_name': 'Director',
                'password': 'admin123',
                'department': 'Medical Operations',
                'phone': '+977-1-5555555',
                'is_superuser': True
            }
        ]
        
        for data in admin_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'is_staff': True,
                    'is_superuser': data['is_superuser'],
                }
            )
            
            if created or not user.check_password(data['password']):
                user.set_password(data['password'])
                user.save()
            
            # Create admin profile
            admin_profile, profile_created = AdminProfile.objects.get_or_create(
                user=user,
                defaults={
                    'name': f"{data['first_name']} {data['last_name']}",
                    'email': data['email'],
                    'contact_no': data['phone'],
                    'department': data['department'],
                    'address': 'Kathmandu, Nepal'
                }
            )
            
            status = "Created" if created else "Updated"
            self.stdout.write(f"  ✅ {status} admin: {user.username} ({data['department']})")

    def create_donor_users(self):
        """Create donor users with profiles"""
        self.stdout.write('🩸 Creating Donor Users...')
        
        donor_data = [
            {
                'username': 'donor1',
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'password': 'donor123',
                'phone_number': '+977-9841234567',
                'blood_group': 'O+',
                'date_of_birth': date(1990, 5, 15),
                'gender': 'M',
                'weight': 70.0,
                'height': 175.0,
                'address': 'Thamel, Kathmandu',
                'city': 'Kathmandu',
                'country': 'Nepal',
                'emergency_contact_name': 'Jane Doe',
                'emergency_contact_phone': '+977-9841234568',
                'latitude': 27.7172,
                'longitude': 85.3240,
            },
            {
                'username': 'donor2',
                'email': 'sarah.smith@example.com',
                'first_name': 'Sarah',
                'last_name': 'Smith',
                'password': 'donor123',
                'phone_number': '+977-9851234567',
                'blood_group': 'A+',
                'date_of_birth': date(1985, 8, 22),
                'gender': 'F',
                'weight': 60.0,
                'height': 165.0,
                'address': 'Patan, Lalitpur',
                'city': 'Lalitpur',
                'country': 'Nepal',
                'emergency_contact_name': 'Mike Smith',
                'emergency_contact_phone': '+977-9851234568',
                'latitude': 27.6588,
                'longitude': 85.3247,
            },
            {
                'username': 'donor3',
                'email': 'michael.johnson@example.com',
                'first_name': 'Michael',
                'last_name': 'Johnson',
                'password': 'donor123',
                'phone_number': '+977-9861234567',
                'blood_group': 'B+',
                'date_of_birth': date(1992, 3, 10),
                'gender': 'M',
                'weight': 75.0,
                'height': 180.0,
                'address': 'Bhaktapur Durbar Square',
                'city': 'Bhaktapur',
                'country': 'Nepal',
                'emergency_contact_name': 'Lisa Johnson',
                'emergency_contact_phone': '+977-9861234568',
                'latitude': 27.6710,
                'longitude': 85.4298,
            },
            {
                'username': 'donor4',
                'email': 'priya.sharma@example.com',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'password': 'donor123',
                'phone_number': '+977-9871234567',
                'blood_group': 'AB+',
                'date_of_birth': date(1988, 12, 5),
                'gender': 'F',
                'weight': 55.0,
                'height': 160.0,
                'address': 'Baneshwor, Kathmandu',
                'city': 'Kathmandu',
                'country': 'Nepal',
                'emergency_contact_name': 'Raj Sharma',
                'emergency_contact_phone': '+977-9871234568',
                'latitude': 27.6915,
                'longitude': 85.3438,
            },
            {
                'username': 'donor5',
                'email': 'david.wilson@example.com',
                'first_name': 'David',
                'last_name': 'Wilson',
                'password': 'donor123',
                'phone_number': '+977-9881234567',
                'blood_group': 'O-',
                'date_of_birth': date(1995, 7, 18),
                'gender': 'M',
                'weight': 68.0,
                'height': 172.0,
                'address': 'Pokhara, Kaski',
                'city': 'Pokhara',
                'country': 'Nepal',
                'emergency_contact_name': 'Emma Wilson',
                'emergency_contact_phone': '+977-9881234568',
                'latitude': 28.2096,
                'longitude': 83.9856,
            }
        ]
        
        for data in donor_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'is_staff': False,
                    'is_superuser': False,
                }
            )
            
            if created or not user.check_password(data['password']):
                user.set_password(data['password'])
                user.save()
            
            # Create donor profile
            donor_profile, profile_created = Donor.objects.get_or_create(
                user=user,
                defaults={
                    'phone_number': data['phone_number'],
                    'blood_group': data['blood_group'],
                    'date_of_birth': data['date_of_birth'],
                    'gender': data['gender'],
                    'weight': data['weight'],
                    'height': data['height'],
                    'address': data['address'],
                    'city': data['city'],
                    'country': data['country'],
                    'emergency_contact_name': data['emergency_contact_name'],
                    'emergency_contact_phone': data['emergency_contact_phone'],
                    'medical_conditions': 'None',
                    'allow_emergency_contact': True,
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                }
            )
            
            status = "Created" if created else "Updated"
            self.stdout.write(f"  ✅ {status} donor: {user.username} ({data['blood_group']}) - {data['city']}")

    def create_donation_centers(self):
        """Create donation centers"""
        self.stdout.write('🏥 Creating Donation Centers...')
        
        centers_data = [
            {
                'name': 'Central Blood Bank',
                'address': 'Baneshwor, Kathmandu',
                'city': 'Kathmandu',
                'state': 'Bagmati Province',
                'phone_number': '+977-1-4567890',
                'email': 'central@bloodbank.gov.np',
            },
            {
                'name': 'Patan Hospital Blood Bank',
                'address': 'Lagankhel, Lalitpur',
                'city': 'Lalitpur',
                'state': 'Bagmati Province',
                'phone_number': '+977-1-5567890',
                'email': 'patan@bloodbank.org.np',
            }
        ]
        
        for data in centers_data:
            center, created = DonationCenter.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            
            status = "Created" if created else "Updated"
            self.stdout.write(f"  ✅ {status} center: {center.name} - {center.city}")

    def create_sample_data(self):
        """Create sample donation requests, history, and health metrics"""
        self.stdout.write('📊 Creating Sample Data...')
        
        donors = list(Donor.objects.all())
        if not donors:
            self.stdout.write("  ⚠️ No donors available for sample data")
            return
        
        # Create donation requests
        for i, donor in enumerate(donors[:3]):
            request, created = DonationRequest.objects.get_or_create(
                donor=donor,
                defaults={
                    'requested_date': date.today() + timedelta(days=i+1),
                    'preferred_time': '10:00:00',
                    'status': 'pending',
                    'notes': f'Regular donation request from {donor.user.first_name}'
                }
            )
            if created:
                self.stdout.write(f"  ✅ Created donation request for {donor.user.username}")
        
        # Create donation history
        centers = list(DonationCenter.objects.all())
        if centers:
            for i, donor in enumerate(donors[:2]):
                history, created = DonationHistory.objects.get_or_create(
                    donor=donor,
                    donation_center=centers[0].name,
                    defaults={
                        'donation_date': date.today() - timedelta(days=120 + i*30),
                        'units_donated': Decimal('1.0'),
                        'notes': f'Successful donation by {donor.user.first_name}'
                    }
                )
                if created:
                    self.stdout.write(f"  ✅ Created donation history for {donor.user.username}")
        
        # Create health metrics
        for donor in donors:
            metrics, created = HealthMetrics.objects.get_or_create(
                donor=donor,
                defaults={
                    'weight': donor.weight,
                    'blood_pressure_systolic': 120,
                    'blood_pressure_diastolic': 80,
                    'resting_heart_rate': 72,
                    'notes': 'Regular health checkup'
                }
            )
            if created:
                self.stdout.write(f"  ✅ Created health metrics for {donor.user.username}")

    def create_notifications(self):
        """Create sample notifications"""
        self.stdout.write('🔔 Creating Notifications...')
        
        admin_users = User.objects.filter(is_staff=True)
        if not admin_users.exists():
            self.stdout.write("  ⚠️ No admins available for notifications")
            return
        
        admin_user = admin_users.first()
        
        # System notifications
        system_notifications = [
            {
                'title': 'Blood Drive Campaign',
                'message': 'Join our monthly blood drive campaign. Help save lives!',
                'notification_type': 'info',
                'priority': 'medium',
                'target_audience': 'donors',
                'created_by': admin_user,
            },
            {
                'title': 'Emergency Blood Needed',
                'message': 'Urgent need for O- blood type. Please donate if eligible.',
                'notification_type': 'emergency_request',
                'priority': 'critical',
                'target_audience': 'donors',
                'created_by': admin_user,
            }
        ]
        
        for data in system_notifications:
            notification, created = SystemNotification.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
            if created:
                self.stdout.write(f"  ✅ Created system notification: {notification.title}")
        
        # User notifications
        donors = Donor.objects.all()[:2]
        for donor in donors:
            user_notification, created = UserNotification.objects.get_or_create(
                user=donor.user,
                title='Welcome to Blood Donation System',
                defaults={
                    'message': f'Welcome {donor.user.first_name}! Thank you for joining our blood donation community.',
                    'notification_type': 'profile_updated',
                }
            )
            if created:
                self.stdout.write(f"  ✅ Created user notification for {donor.user.username}")
