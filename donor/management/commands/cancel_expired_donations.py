"""
Management command to automatically cancel approved donation requests
that weren't completed within 2 hours of the scheduled appointment time.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from donor.models import DonationRequest
from utils.notification_service import NotificationService


class Command(BaseCommand):
    help = 'Automatically cancel approved donations not completed within 2 hours of appointment time'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=2,
            help='Number of hours after appointment time to wait before auto-cancelling (default: 2)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run in dry-run mode (show what would be cancelled without actually cancelling)'
        )

    def handle(self, *args, **options):
        hours_threshold = options['hours']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.NOTICE(
            f'\n{"=" * 70}\n'
            f'Auto-Cancel Expired Donations\n'
            f'{"=" * 70}\n'
            f'Threshold: {hours_threshold} hours after appointment time\n'
            f'Mode: {"DRY RUN" if dry_run else "LIVE"}\n'
            f'{"=" * 70}\n'
        ))
        
        now = timezone.now()
        current_date = now.date()
        current_time = now.time()
        
        # Get all approved donations
        approved_requests = DonationRequest.objects.filter(
            status='approved'
        ).select_related('donor__user')
        
        cancelled_count = 0
        checked_count = 0
        
        for request in approved_requests:
            checked_count += 1
            
            # Combine date and time for comparison
            appointment_datetime = datetime.combine(
                request.requested_date,
                request.preferred_time
            )
            
            # Make it timezone-aware
            if timezone.is_naive(appointment_datetime):
                appointment_datetime = timezone.make_aware(appointment_datetime)
            
            # Calculate the deadline (appointment time + threshold hours)
            deadline = appointment_datetime + timedelta(hours=hours_threshold)
            
            # Check if we've passed the deadline
            if now > deadline:
                time_passed = now - appointment_datetime
                hours_passed = time_passed.total_seconds() / 3600
                
                self.stdout.write(
                    self.style.WARNING(
                        f'\n[EXPIRED] Request #{request.id}\n'
                        f'  Donor: {request.donor.name}\n'
                        f'  Blood Group: {request.donor.blood_group}\n'
                        f'  Scheduled: {request.requested_date} at {request.preferred_time}\n'
                        f'  Time Passed: {hours_passed:.1f} hours\n'
                        f'  Deadline: {deadline.strftime("%Y-%m-%d %H:%M")}\n'
                    )
                )
                
                if not dry_run:
                    # Cancel the request
                    request.status = 'cancelled'
                    request.admin_notes = (
                        f'Automatically cancelled - not completed within {hours_threshold} hours '
                        f'of scheduled appointment time ({appointment_datetime.strftime("%Y-%m-%d %H:%M")}). '
                        f'Cancelled at {now.strftime("%Y-%m-%d %H:%M")}.'
                    )
                    request.save()
                    
                    # Notify the donor
                    try:
                        NotificationService.create_notification(
                            user=request.donor.user,
                            title='Donation Appointment Auto-Cancelled',
                            message=(
                                f'Your blood donation scheduled for {request.requested_date} at '
                                f'{request.preferred_time} has been automatically cancelled because '
                                f'it was not confirmed as completed within {hours_threshold} hours of the '
                                f'appointment time. Please schedule a new appointment if you would like to donate.'
                            ),
                            notification_type='warning',
                            related_object=request
                        )
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✓ Cancelled and donor notified')
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'  ✗ Cancelled but notification failed: {e}')
                        )
                    
                    cancelled_count += 1
                else:
                    self.stdout.write(
                        self.style.NOTICE(f'  [DRY RUN] Would be cancelled')
                    )
                    cancelled_count += 1
        
        # Summary
        self.stdout.write(
            self.style.NOTICE(
                f'\n{"=" * 70}\n'
                f'Summary\n'
                f'{"=" * 70}\n'
                f'Total Approved Requests Checked: {checked_count}\n'
                f'{"Would Be" if dry_run else ""} Cancelled: {cancelled_count}\n'
                f'{"=" * 70}\n'
            )
        )
        
        if cancelled_count > 0:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        '\nThis was a DRY RUN. No changes were made.\n'
                        'Remove --dry-run flag to actually cancel the donations.\n'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✓ Successfully cancelled {cancelled_count} expired donation request(s).\n'
                    )
                )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✓ No expired donation requests found.\n'
                )
            )
