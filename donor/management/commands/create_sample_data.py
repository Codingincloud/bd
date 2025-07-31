from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import random

from donor.models import (
    Donor, DonationRequest, DonationHistory, EmergencyRequest, DonationCenter
)
from admin_panel.models import AdminProfile

class Command(BaseCommand):
    help = 'Create sample data for testing the blood donation system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create donation centers
        centers_data = [
            {
                'name': 'Central Blood Bank',
                'address': 'Soaltee-Mode, Kathmandu',
                'city': 'Kathmandu',
                'state': 'Bagmati Province',
                'phone_number': '01-4444444',
                'email': 'central@bloodbank.np'
            },
            {
                'name': 'Bir Hospital Blood Bank',
                'address': 'Bir Hospital, Kathmandu',
                'city': 'Kathmandu',
                'state': 'Bagmati Province',
                'phone_number': '01-4555555',
                'email': 'bir@hospital.np'
            },
            {
                'name': 'Teaching Hospital Blood Bank',
                'address': 'Maharajgunj, Kathmandu',
                'city': 'Kathmandu',
                'state': 'Bagmati Province',
                'phone_number': '01-4666666',
                'email': 'teaching@hospital.np'
            },
        ]

        centers = []
        for center_data in centers_data:
            center, created = DonationCenter.objects.get_or_create(
                name=center_data['name'],
                defaults=center_data
            )
            centers.append(center)
            if created:
                self.stdout.write(f'Created donation center: {center.name}')

        # Create sample donors
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        sample_names = [
            'Ram Sharma', 'Sita Poudel', 'Hari Thapa', 'Gita Gurung',
            'Krishna Shrestha', 'Maya Tamang', 'Bikash Rai', 'Sunita Magar',
            'Rajesh Karki', 'Kamala Bhattarai', 'Suresh Adhikari', 'Radha Khadka'
        ]

        donors_created = 0
        for i, name in enumerate(sample_names):
            username = f'donor{i+1}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='password123',
                    first_name=name.split()[0],
                    last_name=name.split()[1] if len(name.split()) > 1 else ''
                )

                donor = Donor.objects.create(
                    user=user,
                    blood_group=random.choice(blood_groups),
                    date_of_birth=date(1990, 1, 1) + timedelta(days=random.randint(0, 10000)),
                    gender=random.choice(['M', 'F']),
                    phone_number=f'98{random.randint(10000000, 99999999)}',
                    address=f'Address {i+1}, Kathmandu',
                    weight=random.uniform(50, 90),
                    height=random.uniform(150, 180),
                    is_eligible=True
                )
                donors_created += 1

        self.stdout.write(f'Created {donors_created} sample donors')

        # Create sample donation requests
        donors = Donor.objects.all()
        requests_created = 0
        for i in range(15):
            donor = random.choice(donors)
            request_date = timezone.now().date() - timedelta(days=random.randint(0, 30))
            
            donation_request = DonationRequest.objects.create(
                donor=donor,
                requested_date=request_date,
                preferred_time=timezone.now().time().replace(hour=random.randint(9, 17), minute=0),
                status=random.choice(['pending', 'approved', 'completed', 'cancelled']),
                notes=f'Sample request {i+1}'
            )
            requests_created += 1

        self.stdout.write(f'Created {requests_created} sample donation requests')

        # Create sample donation history
        history_created = 0
        for i in range(20):
            donor = random.choice(donors)
            donation_date = timezone.now().date() - timedelta(days=random.randint(1, 365))
            
            history = DonationHistory.objects.create(
                donor=donor,
                donation_date=donation_date,
                donation_center=random.choice(centers).name,
                units_donated=random.choice([0.5, 1.0, 1.5]),
                blood_pressure=f'{random.randint(110, 140)}/{random.randint(70, 90)}',
                hemoglobin_level=random.uniform(12.0, 16.0),
                notes=f'Sample donation {i+1}'
            )
            
            # Update donor's last donation date
            if not donor.last_donation_date or donation_date > donor.last_donation_date:
                donor.last_donation_date = donation_date
                donor.save()
            
            history_created += 1

        self.stdout.write(f'Created {history_created} sample donation history records')

        # Create sample emergency requests
        emergency_created = 0
        for i in range(8):
            emergency = EmergencyRequest.objects.create(
                blood_group_needed=random.choice(blood_groups),
                units_needed=random.randint(1, 5),
                hospital_name=f'Hospital {i+1}',
                contact_person=f'Dr. Contact {i+1}',
                contact_phone=f'98{random.randint(10000000, 99999999)}',
                location=f'Location {i+1}, Kathmandu',
                urgency_level=random.choice(['low', 'medium', 'high', 'critical']),
                required_by=timezone.now() + timedelta(days=random.randint(1, 7)),
                status=random.choice(['active', 'fulfilled', 'expired']),
                notes=f'Emergency request {i+1}'
            )
            emergency_created += 1

        self.stdout.write(f'Created {emergency_created} sample emergency requests')

        # Create admin profile for the superuser
        try:
            admin_user = User.objects.get(username='admin')
            if not hasattr(admin_user, 'adminprofile'):
                AdminProfile.objects.create(
                    user=admin_user,
                    name='System Administrator',
                    contact_no='01-1234567',
                    address='Admin Office, Kathmandu',
                    email='admin@blooddonation.np',
                    department='Blood Bank Management'
                )
                self.stdout.write('Created admin profile')
        except User.DoesNotExist:
            pass

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {donors_created} donors\n'
                f'- {requests_created} donation requests\n'
                f'- {history_created} donation history records\n'
                f'- {emergency_created} emergency requests\n'
                f'- {len(centers)} donation centers'
            )
        )
