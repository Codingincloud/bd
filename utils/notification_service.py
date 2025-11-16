"""
Notification Service for Blood Donation Management System
Handles all notification creation and management
"""
from django.contrib.auth.models import User
from django.utils import timezone
from admin_panel.models import SystemNotification, UserNotification
from donor.models import DonationRequest, EmergencyRequest
from utils.constants import CAN_RECEIVE_FROM


class NotificationService:
    """Service class to handle all notification operations"""
    
    @staticmethod
    def create_system_notification(title, message, notification_type='info', 
                                 priority='medium', target_audience='all', 
                                 created_by=None, action_url='', expires_at=None):
        """Create a system-wide notification"""
        try:
            notification = SystemNotification.objects.create(
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                target_audience=target_audience,
                created_by=created_by,
                action_url=action_url,
                expires_at=expires_at
            )
            return notification
        except Exception as e:
            print(f"Error creating system notification: {e}")
            return None
    
    @staticmethod
    def create_user_notification(user, title, message, notification_type,
                               action_url='', related_donation_request=None,
                               related_emergency=None):
        """Create a notification for a specific user (avoid duplicates)"""
        try:
            # Check if similar notification already exists (within last hour)
            from django.utils import timezone
            from datetime import timedelta

            one_hour_ago = timezone.now() - timedelta(hours=1)
            existing = UserNotification.objects.filter(
                user=user,
                title=title,
                notification_type=notification_type,
                created_at__gte=one_hour_ago
            ).first()

            if existing:
                return existing  # Don't create duplicate

            notification = UserNotification.objects.create(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                action_url=action_url,
                related_donation_request=related_donation_request,
                related_emergency=related_emergency
            )
            return notification
        except Exception as e:
            print(f"Error creating user notification: {e}")
            return None
    
    @staticmethod
    def notify_donation_scheduled(donation_request):
        """Notify when a donation is scheduled"""
        donor = donation_request.donor
        
        # Create user notification
        NotificationService.create_user_notification(
            user=donor.user,
            title='Donation Scheduled',
            message=f'Your blood donation has been scheduled for {donation_request.requested_date}. Please arrive 30 minutes early.',
            notification_type='donation_scheduled',
            action_url='/donor/dashboard/',
            related_donation_request=donation_request
        )
        
        # Create system notification for admins
        admin_users = User.objects.filter(is_staff=True)
        if admin_users.exists():
            NotificationService.create_system_notification(
                title='New Donation Scheduled',
                message=f'Donation scheduled for {donor.name} ({donor.blood_group}) on {donation_request.requested_date}',
                notification_type='donation_scheduled',
                priority='medium',
                target_audience='admins',
                created_by=admin_users.first()
            )
    
    @staticmethod
    def notify_donation_reminder(donation_request):
        """Send reminder notification for upcoming donation"""
        donor = donation_request.donor
        
        NotificationService.create_user_notification(
            user=donor.user,
            title='Donation Reminder',
            message=f'Reminder: Your blood donation is scheduled for tomorrow ({donation_request.requested_date}). Please ensure you are well-rested and hydrated.',
            notification_type='donation_reminder',
            action_url='/donor/dashboard/',
            related_donation_request=donation_request
        )
    
    @staticmethod
    def notify_donation_completed(donation_history):
        """Notify when a donation is completed"""
        donor = donation_history.donor
        
        NotificationService.create_user_notification(
            user=donor.user,
            title='Donation Completed - Thank You!',
            message=f'Thank you for your blood donation on {donation_history.donation_date}. You donated {donation_history.units_donated}ml. Your next eligible donation date is in 3 months.',
            notification_type='donation_completed',
            action_url='/donor/dashboard/'
        )
    
    @staticmethod
    def notify_emergency_request(emergency_request):
        """Notify compatible donors about emergency blood request"""
        blood_group = emergency_request.blood_group_needed
        
        # Find compatible donors using constants
        from donor.models import Donor
        compatible_groups = CAN_RECEIVE_FROM.get(blood_group, [blood_group])
        
        compatible_donors = Donor.objects.filter(
            blood_group__in=compatible_groups,
            is_eligible=True,
            allow_emergency_contact=True
        )
        
        for donor in compatible_donors:
            NotificationService.create_user_notification(
                user=donor.user,
                title='🚨 Emergency Blood Request',
                message=f'URGENT: {emergency_request.hospital_name} needs {blood_group} blood. Contact: {emergency_request.contact_person}. Required by: {emergency_request.required_by}',
                notification_type='emergency_request',
                action_url='/donor/dashboard/',
                related_emergency=emergency_request
            )
        
        # Create system notification
        admin_users = User.objects.filter(is_staff=True)
        if admin_users.exists():
            NotificationService.create_system_notification(
                title=f'Emergency: {blood_group} Blood Needed',
                message=f'{emergency_request.hospital_name} urgently needs {emergency_request.units_needed} units of {blood_group} blood. Contact: {emergency_request.contact_person}',
                notification_type='emergency_request',
                priority='critical',
                target_audience='all',
                created_by=admin_users.first()
            )
    
    @staticmethod
    def notify_eligibility_restored(donor):
        """Notify donor when they become eligible to donate again"""
        NotificationService.create_user_notification(
            user=donor.user,
            title='You Can Donate Again!',
            message='Great news! You are now eligible to donate blood again. Schedule your next donation and help save lives.',
            notification_type='eligibility_restored',
            action_url='/donor/dashboard/'
        )
    
    @staticmethod
    def notify_profile_updated(user):
        """Notify when user profile is updated"""
        NotificationService.create_user_notification(
            user=user,
            title='Profile Updated',
            message='Your profile information has been successfully updated.',
            notification_type='profile_updated',
            action_url='/donor/dashboard/'
        )
    
    @staticmethod
    def notify_location_updated(donor):
        """Notify when donor location is updated"""
        NotificationService.create_user_notification(
            user=donor.user,
            title='Location Updated',
            message=f'Your location has been updated to {donor.city}, {donor.country}. This helps us find you during emergencies.',
            notification_type='location_updated',
            action_url='/donor/location/update/'
        )
    
    @staticmethod
    def notify_health_metrics_added(donor):
        """Notify when health metrics are added"""
        NotificationService.create_user_notification(
            user=donor.user,
            title='Health Metrics Recorded',
            message='Your health metrics have been recorded successfully. Keep track of your health for safe donations.',
            notification_type='health_metrics_added',
            action_url='/donor/medical-info/'
        )
    
    @staticmethod
    def notify_request_approved(donation_request):
        """Notify when donation request is approved"""
        donor = donation_request.donor
        
        NotificationService.create_user_notification(
            user=donor.user,
            title='Donation Request Approved',
            message=f'Your donation request for {donation_request.requested_date} has been approved. Please arrive on time.',
            notification_type='request_approved',
            action_url='/donor/dashboard/',
            related_donation_request=donation_request
        )
    
    @staticmethod
    def notify_request_rejected(donation_request, reason=''):
        """Notify when donation request is rejected"""
        donor = donation_request.donor
        
        message = f'Your donation request for {donation_request.requested_date} has been rejected.'
        if reason:
            message += f' Reason: {reason}'
        message += ' Please contact us if you have any questions.'
        
        NotificationService.create_user_notification(
            user=donor.user,
            title='Donation Request Rejected',
            message=message,
            notification_type='request_rejected',
            action_url='/donor/dashboard/',
            related_donation_request=donation_request
        )
    
    @staticmethod
    def get_user_notifications(user, unread_only=False):
        """Get notifications for a specific user"""
        notifications = UserNotification.objects.filter(user=user)
        
        if unread_only:
            notifications = notifications.filter(is_read=False)
        
        return notifications.order_by('-created_at')
    
    @staticmethod
    def get_system_notifications(target_audience='all', user=None):
        """Get active system notifications for a specific audience, excluding user-dismissed ones"""
        notifications = SystemNotification.objects.filter(
            is_active=True,
            target_audience__in=[target_audience, 'all']
        )

        # Filter out expired notifications and user-dismissed ones
        active_notifications = []
        for notification in notifications:
            if not notification.is_expired:
                # If user is provided, check if they've dismissed this notification
                if user and user.is_authenticated:
                    from admin_panel.models import SystemNotificationRead
                    if not SystemNotificationRead.objects.filter(
                        user=user,
                        system_notification=notification
                    ).exists():
                        active_notifications.append(notification)
                else:
                    active_notifications.append(notification)

        return active_notifications
    
    @staticmethod
    def mark_notification_read(notification_id, user):
        """Mark a user notification as read"""
        try:
            notification = UserNotification.objects.get(id=notification_id, user=user)
            notification.is_read = True
            notification.save()
            return True
        except UserNotification.DoesNotExist:
            return False
    
    @staticmethod
    def mark_all_notifications_read(user):
        """Mark all notifications as read for a user"""
        UserNotification.objects.filter(user=user, is_read=False).update(is_read=True)

    @staticmethod
    def delete_read_notifications(user):
        """Delete all read notifications for a user"""
        deleted_count = UserNotification.objects.filter(user=user, is_read=True).delete()[0]
        return deleted_count

    @staticmethod
    def mark_system_notification_read(notification_id, user):
        """Mark a system notification as read for a specific user"""
        try:
            from admin_panel.models import SystemNotification, SystemNotificationRead

            notification = SystemNotification.objects.get(id=notification_id)
            SystemNotificationRead.objects.get_or_create(
                user=user,
                system_notification=notification
            )
            return True
        except SystemNotification.DoesNotExist:
            return False
        except Exception as e:
            print(f"Error marking system notification as read: {e}")
            return False

    @staticmethod
    def cleanup_old_notifications(days=30):
        """Delete notifications older than specified days"""
        from django.utils import timezone
        from datetime import timedelta

        cutoff_date = timezone.now() - timedelta(days=days)

        # Delete old user notifications
        user_deleted = UserNotification.objects.filter(created_at__lt=cutoff_date).delete()[0]

        # Delete old system notifications
        system_deleted = SystemNotification.objects.filter(created_at__lt=cutoff_date).delete()[0]

        # Delete old system notification read records
        from admin_panel.models import SystemNotificationRead
        read_deleted = SystemNotificationRead.objects.filter(read_at__lt=cutoff_date).delete()[0]

        return user_deleted + system_deleted + read_deleted
    
    @staticmethod
    def get_notification_count(user, unread_only=True):
        """Get notification count for a user"""
        notifications = UserNotification.objects.filter(user=user)
        
        if unread_only:
            notifications = notifications.filter(is_read=False)
        
        return notifications.count()
    
    @staticmethod
    def notify_emergency_response(emergency_request, donor, response_text='', selected_hospital=None):
        """Notify admins when a donor responds to an emergency request"""
        admin_users = User.objects.filter(is_staff=True)
        
        message = f"Donor {donor.name} ({donor.blood_group}) responded to emergency request at {emergency_request.hospital_name}."
        if response_text:
            message += f" Response: {response_text}"
        if selected_hospital:
            message += f" Selected hospital: {selected_hospital.name}"
        
        for admin in admin_users:
            NotificationService.create_user_notification(
                user=admin,
                title='Emergency Response Received',
                message=message,
                notification_type='emergency_response',
                action_url='/admin-panel/emergencies/',
                related_emergency=emergency_request
            )
        
        # Also create system notification
        NotificationService.create_system_notification(
            title='Donor Responded to Emergency',
            message=message,
            notification_type='emergency_response',
            priority='high',
            target_audience='admins',
            created_by=admin_users.first() if admin_users.exists() else None
        )

