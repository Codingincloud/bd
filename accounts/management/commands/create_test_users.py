from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from donor.models import Donor
from admin_panel.models import AdminProfile
from datetime import date


class Command(BaseCommand):
    help = 'Create test admin and donor users'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Create Admin User
                admin_user, created = User.objects.get_or_create(
                    username='admin',
                    defaults={
                        'email': 'admin@bloodbank.com',
                        'first_name': 'System',
                        'last_name': 'Administrator',
                        'is_staff': True,
                        'is_superuser': True,
                    }
                )
                if created:
                    admin_user.set_password('admin123')
                    admin_user.save()
                    
                    # Create AdminProfile
                    AdminProfile.objects.create(
                        user=admin_user,
                        name='System Administrator',
                        contact_no='+977-9841234567',
                        address='Blood Bank Headquarters, Kathmandu',
                        city='Kathmandu',
                        state='Bagmati',
                        postal_code='44600',
                        country='Nepal',
                        email='admin@bloodbank.com',
                        department='Blood Bank Management'
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Admin user created: username=admin, password=admin123')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Admin user already exists: username=admin')
                    )

                # Create Donor User
                donor_user, created = User.objects.get_or_create(
                    username='donor',
                    defaults={
                        'email': 'donor@bloodbank.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'is_staff': False,
                        'is_superuser': False,
                    }
                )
                if created:
                    donor_user.set_password('donor123')
                    donor_user.save()
                    
                    # Create Donor Profile
                    Donor.objects.create(
                        user=donor_user,
                        blood_group='O+',
                        date_of_birth=date(1990, 5, 15),
                        gender='M',
                        phone_number='+977-9851234567',
                        address='Thamel, Kathmandu',
                        city='Kathmandu',
                        state='Bagmati',
                        postal_code='44600',
                        country='Nepal',
                        weight=70.0,
                        height=175.0,
                        is_eligible=True,
                        emergency_contact_name='Jane Doe',
                        emergency_contact_phone='+977-9861234567',
                        allow_emergency_contact=True
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Donor user created: username=donor, password=donor123')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Donor user already exists: username=donor')
                    )

                # Create another donor with different blood group
                donor2_user, created = User.objects.get_or_create(
                    username='donor2',
                    defaults={
                        'email': 'donor2@bloodbank.com',
                        'first_name': 'Sarah',
                        'last_name': 'Smith',
                        'is_staff': False,
                        'is_superuser': False,
                    }
                )
                if created:
                    donor2_user.set_password('donor123')
                    donor2_user.save()
                    
                    # Create Donor Profile
                    Donor.objects.create(
                        user=donor2_user,
                        blood_group='A+',
                        date_of_birth=date(1985, 8, 22),
                        gender='F',
                        phone_number='+977-9841234568',
                        address='Patan, Lalitpur',
                        city='Lalitpur',
                        state='Bagmati',
                        postal_code='44700',
                        country='Nepal',
                        latitude=27.6683,
                        longitude=85.3206,
                        weight=60.0,
                        height=165.0,
                        is_eligible=True,
                        emergency_contact_name='Mike Smith',
                        emergency_contact_phone='+977-9851234568',
                        allow_emergency_contact=True
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Donor2 user created: username=donor2, password=donor123')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Donor2 user already exists: username=donor2')
                    )

                self.stdout.write(
                    self.style.SUCCESS('\n🎉 Test users creation completed!')
                )
                self.stdout.write('📋 Login Credentials:')
                self.stdout.write('👨‍💼 Admin: username=admin, password=admin123')
                self.stdout.write('🩸 Donor1: username=donor, password=donor123')
                self.stdout.write('🩸 Donor2: username=donor2, password=donor123')
                self.stdout.write('\n🌐 Access URLs:')
                self.stdout.write('🔗 Login: http://127.0.0.1:8000/accounts/login/')
                self.stdout.write('🔗 Register: http://127.0.0.1:8000/accounts/register/')
                self.stdout.write('🔗 Admin Panel: http://127.0.0.1:8000/admin-panel/dashboard/')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating test users: {str(e)}')
            )
