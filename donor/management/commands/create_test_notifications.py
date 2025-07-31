"""
Django management command to create test notifications
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from utils.notification_service import NotificationService


class Command(BaseCommand):
    help = 'Create test notifications for testing the notification system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔔 CREATING TEST NOTIFICATIONS'))
        self.stdout.write('=' * 50)
        
        # Get test users
        try:
            donor_user = User.objects.get(username='donor1')
            admin_user = User.objects.filter(is_staff=True).first()
            
            if not donor_user:
                self.stdout.write(self.style.ERROR('No donor1 user found. Please run populate_test_data first.'))
                return
                
            if not admin_user:
                self.stdout.write(self.style.ERROR('No admin user found. Please run populate_test_data first.'))
                return
            
            # Create user notifications for donor
            user_notifications = [
                {
                    'title': 'Welcome to Blood Donation System',
                    'message': 'Thank you for joining our blood donation community. Your contribution saves lives!',
                    'notification_type': 'profile_updated'
                },
                {
                    'title': 'Donation Reminder',
                    'message': 'You are now eligible to donate blood again. Schedule your next donation today!',
                    'notification_type': 'eligibility_restored'
                },
                {
                    'title': 'Emergency Blood Request',
                    'message': 'Urgent need for O+ blood type at Central Hospital. Your help is needed!',
                    'notification_type': 'emergency_request'
                }
            ]
            
            for notification_data in user_notifications:
                NotificationService.create_user_notification(
                    user=donor_user,
                    **notification_data
                )
                self.stdout.write(f"  ✅ Created user notification: {notification_data['title']}")
            
            # Create system notifications
            system_notifications = [
                {
                    'title': 'Blood Drive Campaign',
                    'message': 'Join our monthly blood drive campaign this weekend. Help save lives in your community!',
                    'notification_type': 'info',
                    'priority': 'medium',
                    'target_audience': 'donors',
                    'created_by': admin_user
                },
                {
                    'title': 'System Maintenance Notice',
                    'message': 'Scheduled maintenance on Sunday 2 AM - 4 AM. System may be temporarily unavailable.',
                    'notification_type': 'maintenance',
                    'priority': 'low',
                    'target_audience': 'all',
                    'created_by': admin_user
                },
                {
                    'title': 'Critical Blood Shortage',
                    'message': 'Critical shortage of AB- blood type. Immediate donations needed at all centers.',
                    'notification_type': 'emergency_request',
                    'priority': 'critical',
                    'target_audience': 'admins',
                    'created_by': admin_user
                }
            ]
            
            for notification_data in system_notifications:
                NotificationService.create_system_notification(**notification_data)
                self.stdout.write(f"  ✅ Created system notification: {notification_data['title']}")
            
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write(self.style.SUCCESS('✅ TEST NOTIFICATIONS CREATED SUCCESSFULLY!'))
            self.stdout.write(f'📊 Summary:')
            self.stdout.write(f'   👤 User notifications: {len(user_notifications)}')
            self.stdout.write(f'   📢 System notifications: {len(system_notifications)}')
            self.stdout.write('\n🎮 Test the notifications:')
            self.stdout.write('   1. Login as donor1 / donor123')
            self.stdout.write('   2. Check notification bell icon')
            self.stdout.write('   3. Click notifications to mark as read')
            self.stdout.write('   4. Login as admin / admin123')
            self.stdout.write('   5. Check admin dashboard notifications')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating notifications: {e}'))
