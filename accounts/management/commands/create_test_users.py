from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from datetime import date
from donor.models import Donor, Hospital, BloodInventory
from admin_panel.models import AdminProfile


class Command(BaseCommand):
    help = 'Create test users (3 admins and 3 donors)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Creating test users...'))

        try:
            with transaction.atomic():
                # Create 3 Admin users with hospitals
                admin_data = [
                    {
                        'username': 'admin_kathmandu',
                        'password': 'Admin@123',
                        'email': 'admin@tuth.edu.np',
                        'first_name': 'Dr. Ramesh',
                        'last_name': 'Sharma',
                        'hospital_name': 'Tribhuvan University Teaching Hospital',
                        'hospital_city': 'Kathmandu',
                        'hospital_phone': '01-4412303',
                    },
                    {
                        'username': 'admin_pokhara',
                        'password': 'Admin@123',
                        'email': 'admin@gandaki.edu.np',
                        'first_name': 'Dr. Binod',
                        'last_name': 'Gurung',
                        'hospital_name': 'Gandaki Medical College',
                        'hospital_city': 'Pokhara',
                        'hospital_phone': '061-535555',
                    },
                    {
                        'username': 'admin_lalitpur',
                        'password': 'Admin@123',
                        'email': 'admin@pahs.edu.np',
                        'first_name': 'Dr. Sushila',
                        'last_name': 'Thapa',
                        'hospital_name': 'Patan Hospital',
                        'hospital_city': 'Lalitpur',
                        'hospital_phone': '01-5522278',
                    },
                ]

                for data in admin_data:
                    # Create user
                    user = User.objects.create_user(
                        username=data['username'],
                        password=data['password'],
                        email=data['email'],
                        first_name=data['first_name'],
                        last_name=data['last_name'],
                        is_staff=True,
                        is_superuser=True,
                    )

                    # Create hospital
                    hospital = Hospital.objects.create(
                        admin_user=user,
                        name=data['hospital_name'],
                        city=data['hospital_city'],
                        phone_number=data['hospital_phone'],
                        email=data['email'],
                        address=f"{data['hospital_city']}, Nepal",
                        state='Nepal',
                        hospital_type='government',
                    )

                    # Initialize blood inventory for hospital
                    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
                    for blood_group in blood_groups:
                        BloodInventory.objects.create(
                            hospital=hospital,
                            blood_group=blood_group,
                            units_available=0
                        )

                    # Create admin profile
                    AdminProfile.objects.create(
                        user=user,
                        name=f"{data['first_name']} {data['last_name']}",
                        contact_no=data['hospital_phone'],
                        address=f"{data['hospital_city']}, Nepal",
                        city=data['hospital_city'],
                        state='Nepal',
                        email=data['email'],
                        department='Blood Bank',
                    )

                    self.stdout.write(self.style.SUCCESS(f'✓ Created admin: {data["username"]} with hospital: {data["hospital_name"]}'))

                # Create 3 Donor users
                donor_data = [
                    {
                        'username': 'ram_sharma',
                        'password': 'Ram@123',
                        'email': 'ram.sharma@email.com',
                        'first_name': 'Ram',
                        'last_name': 'Sharma',
                        'name': 'Ram Sharma',
                        'blood_group': 'O+',
                        'city': 'Kathmandu',
                        'contact_no': '9841234567',
                        'weight': 65.0,
                        'gender': 'M',
                    },
                    {
                        'username': 'sita_gurung',
                        'password': 'Sita@123',
                        'email': 'sita.gurung@email.com',
                        'first_name': 'Sita',
                        'last_name': 'Gurung',
                        'name': 'Sita Gurung',
                        'blood_group': 'A+',
                        'city': 'Pokhara',
                        'contact_no': '9846789012',
                        'weight': 58.0,
                        'gender': 'F',
                    },
                    {
                        'username': 'hari_thapa',
                        'password': 'Hari@123',
                        'email': 'hari.thapa@email.com',
                        'first_name': 'Hari',
                        'last_name': 'Thapa',
                        'name': 'Hari Thapa',
                        'blood_group': 'B+',
                        'city': 'Lalitpur',
                        'contact_no': '9851122334',
                        'weight': 72.0,
                        'gender': 'M',
                    },
                ]

                for data in donor_data:
                    # Create user
                    user = User.objects.create_user(
                        username=data['username'],
                        password=data['password'],
                        email=data['email'],
                        first_name=data['first_name'],
                        last_name=data['last_name'],
                        is_staff=False,
                        is_superuser=False,
                    )

                    # Create donor profile
                    Donor.objects.create(
                        user=user,
                        blood_group=data['blood_group'],
                        date_of_birth=date(1990, 1, 1),  # Default DOB
                        city=data['city'],
                        phone_number=data['contact_no'],
                        weight=data['weight'],
                        gender=data['gender'],
                        address=f"{data['city']}, Nepal",
                        state='Nepal',
                        country='Nepal',
                    )

                    self.stdout.write(self.style.SUCCESS(f'✓ Created donor: {data["username"]} ({data["blood_group"]})'))

                self.stdout.write(self.style.SUCCESS('\n✓ All test users created successfully!'))
                self.stdout.write(self.style.SUCCESS('✓ 3 Admins with hospitals'))
                self.stdout.write(self.style.SUCCESS('✓ 3 Donors'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error creating test users: {str(e)}'))
            raise
