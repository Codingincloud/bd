from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from admin_panel.models import AdminProfile


class Command(BaseCommand):
    help = 'Fix admin user profile'

    def handle(self, *args, **options):
        try:
            admin_user = User.objects.get(username='admin')
            
            # Check if AdminProfile exists
            try:
                profile = admin_user.adminprofile
                self.stdout.write(
                    self.style.SUCCESS('✅ AdminProfile already exists')
                )
            except AdminProfile.DoesNotExist:
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
                    self.style.SUCCESS('✅ AdminProfile created!')
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('❌ Admin user does not exist')
            )
