from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from donor.models import Donor
from admin_panel.models import AdminProfile
from datetime import date


class Command(BaseCommand):
    help = 'Create test accounts for admin and donor'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating test accounts...'))
        
        # Create Admin User
        try:
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
                self.stdout.write(self.style.SUCCESS('✓ Admin user created'))
            else:
                admin_user.set_password('admin123')
                admin_user.save()
                self.stdout.write(self.style.WARNING('✓ Admin user already exists - password updated'))
            
            # Create Admin Profile
            admin_profile, created = AdminProfile.objects.get_or_create(
                user=admin_user,
                defaults={
                    'phone': '+977-1-4444444',
                    'department': 'Blood Bank Management',
                    'employee_id': 'ADMIN001',
                    'city': 'Kathmandu',
                    'country': 'Nepal',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('✓ Admin profile created'))
            else:
                self.stdout.write(self.style.WARNING('✓ Admin profile already exists'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin: {e}'))

        # Create Donor User
        try:
            donor_user, created = User.objects.get_or_create(
                username='donor',
                defaults={
                    'email': 'donor@example.com',
                    'first_name': 'John',
                    'last_name': 'Donor',
                    'is_staff': False,
                    'is_superuser': False,
                }
            )
            if created:
                donor_user.set_password('donor123')
                donor_user.save()
                self.stdout.write(self.style.SUCCESS('✓ Donor user created'))
            else:
                donor_user.set_password('donor123')
                donor_user.save()
                self.stdout.write(self.style.WARNING('✓ Donor user already exists - password updated'))
            
            # Create Donor Profile
            donor_profile, created = Donor.objects.get_or_create(
                user=donor_user,
                defaults={
                    'phone_number': '+977-9841234567',
                    'blood_group': 'O+',
                    'date_of_birth': date(1990, 5, 15),
                    'gender': 'M',
                    'weight': 70.0,
                    'height': 175.0,
                    'address': 'Kathmandu, Nepal',
                    'city': 'Kathmandu',
                    'country': 'Nepal',
                    'emergency_contact_name': 'Jane Donor',
                    'emergency_contact_phone': '+977-9841234568',
                    'medical_conditions': 'None',
                    'allow_emergency_contact': True,
                    'latitude': 27.7172,
                    'longitude': 85.3240,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('✓ Donor profile created'))
            else:
                self.stdout.write(self.style.WARNING('✓ Donor profile already exists'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating donor: {e}'))

        # Create Additional Test Donor
        try:
            donor2_user, created = User.objects.get_or_create(
                username='donor2',
                defaults={
                    'email': 'donor2@example.com',
                    'first_name': 'Sarah',
                    'last_name': 'Smith',
                    'is_staff': False,
                    'is_superuser': False,
                }
            )
            if created:
                donor2_user.set_password('donor123')
                donor2_user.save()
                self.stdout.write(self.style.SUCCESS('✓ Second donor user created'))
            else:
                donor2_user.set_password('donor123')
                donor2_user.save()
                self.stdout.write(self.style.WARNING('✓ Second donor user already exists - password updated'))
            
            # Create Second Donor Profile
            donor2_profile, created = Donor.objects.get_or_create(
                user=donor2_user,
                defaults={
                    'phone_number': '+977-9851234567',
                    'blood_group': 'A+',
                    'date_of_birth': date(1985, 8, 22),
                    'gender': 'F',
                    'weight': 60.0,
                    'height': 165.0,
                    'address': 'Lalitpur, Nepal',
                    'city': 'Lalitpur',
                    'country': 'Nepal',
                    'emergency_contact_name': 'Mike Smith',
                    'emergency_contact_phone': '+977-9851234568',
                    'medical_conditions': 'None',
                    'allow_emergency_contact': True,
                    'latitude': 27.6588,
                    'longitude': 85.3247,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('✓ Second donor profile created'))
            else:
                self.stdout.write(self.style.WARNING('✓ Second donor profile already exists'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating second donor: {e}'))

        self.stdout.write(self.style.SUCCESS('\n=== TEST ACCOUNTS CREATED ==='))
        self.stdout.write(self.style.SUCCESS('Admin Login:'))
        self.stdout.write(self.style.SUCCESS('  Username: admin'))
        self.stdout.write(self.style.SUCCESS('  Password: admin123'))
        self.stdout.write(self.style.SUCCESS('  URL: http://127.0.0.1:8000/admin/'))
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('Donor Login:'))
        self.stdout.write(self.style.SUCCESS('  Username: donor'))
        self.stdout.write(self.style.SUCCESS('  Password: donor123'))
        self.stdout.write(self.style.SUCCESS('  URL: http://127.0.0.1:8000/accounts/login/'))
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('Second Donor Login:'))
        self.stdout.write(self.style.SUCCESS('  Username: donor2'))
        self.stdout.write(self.style.SUCCESS('  Password: donor123'))
        self.stdout.write(self.style.SUCCESS('  URL: http://127.0.0.1:8000/accounts/login/'))
        self.stdout.write(self.style.SUCCESS(''))
        # Create Additional Admin User
        try:
            admin2_user, created = User.objects.get_or_create(
                username='admin2',
                defaults={
                    'email': 'admin2@bloodbank.com',
                    'first_name': 'Medical',
                    'last_name': 'Director',
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            if created:
                admin2_user.set_password('admin123')
                admin2_user.save()
                self.stdout.write(self.style.SUCCESS('✓ Second admin user created'))
            else:
                admin2_user.set_password('admin123')
                admin2_user.save()
                self.stdout.write(self.style.WARNING('✓ Second admin user already exists - password updated'))

            # Create Second Admin Profile
            admin2_profile, created = AdminProfile.objects.get_or_create(
                user=admin2_user,
                defaults={
                    'phone': '+977-1-5555555',
                    'department': 'Medical Operations',
                    'employee_id': 'ADMIN002',
                    'city': 'Lalitpur',
                    'country': 'Nepal',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('✓ Second admin profile created'))
            else:
                self.stdout.write(self.style.WARNING('✓ Second admin profile already exists'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating second admin: {e}'))

        # Create Third Donor User
        try:
            donor3_user, created = User.objects.get_or_create(
                username='donor3',
                defaults={
                    'email': 'donor3@example.com',
                    'first_name': 'Michael',
                    'last_name': 'Johnson',
                    'is_staff': False,
                    'is_superuser': False,
                }
            )
            if created:
                donor3_user.set_password('donor123')
                donor3_user.save()
                self.stdout.write(self.style.SUCCESS('✓ Third donor user created'))
            else:
                donor3_user.set_password('donor123')
                donor3_user.save()
                self.stdout.write(self.style.WARNING('✓ Third donor user already exists - password updated'))

            # Create Third Donor Profile
            donor3_profile, created = Donor.objects.get_or_create(
                user=donor3_user,
                defaults={
                    'phone_number': '+977-9861234567',
                    'blood_group': 'B+',
                    'date_of_birth': date(1992, 3, 10),
                    'gender': 'M',
                    'weight': 75.0,
                    'height': 180.0,
                    'address': 'Bhaktapur, Nepal',
                    'city': 'Bhaktapur',
                    'country': 'Nepal',
                    'emergency_contact_name': 'Lisa Johnson',
                    'emergency_contact_phone': '+977-9861234568',
                    'medical_conditions': 'None',
                    'allow_emergency_contact': True,
                    'latitude': 27.6710,
                    'longitude': 85.4298,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('✓ Third donor profile created'))
            else:
                self.stdout.write(self.style.WARNING('✓ Third donor profile already exists'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating third donor: {e}'))

        self.stdout.write(self.style.SUCCESS('\n=== ALL TEST ACCOUNTS CREATED ==='))
        self.stdout.write(self.style.SUCCESS('Admin Logins:'))
        self.stdout.write(self.style.SUCCESS('  Username: admin / Password: admin123'))
        self.stdout.write(self.style.SUCCESS('  Username: admin2 / Password: admin123'))
        self.stdout.write(self.style.SUCCESS('  URL: http://127.0.0.1:8000/admin/'))
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('Donor Logins:'))
        self.stdout.write(self.style.SUCCESS('  Username: donor / Password: donor123'))
        self.stdout.write(self.style.SUCCESS('  Username: donor2 / Password: donor123'))
        self.stdout.write(self.style.SUCCESS('  Username: donor3 / Password: donor123'))
        self.stdout.write(self.style.SUCCESS('  URL: http://127.0.0.1:8000/accounts/login/'))
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('All accounts ready for testing!'))
