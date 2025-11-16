"""
Django management command to create missing DonationHistory records for completed requests
Usage: python manage.py fix_donation_history [--dry-run]
"""
from django.core.management.base import BaseCommand
from donor.models import DonationHistory, DonationRequest


class Command(BaseCommand):
    help = 'Create missing DonationHistory records for completed DonationRequests'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run in dry-run mode (show what would be fixed without actually fixing)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write(
            self.style.NOTICE('FIX MISSING DONATION HISTORY RECORDS')
        )
        self.stdout.write("="*70)
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n[DRY RUN MODE] - No changes will be made\n')
            )

        # Find all completed requests
        completed_requests = DonationRequest.objects.filter(status='completed')
        self.stdout.write(f"\nTotal completed requests: {completed_requests.count()}")

        fixed_count = 0
        already_exists_count = 0
        error_count = 0

        for req in completed_requests:
            self.stdout.write(f"\nChecking Request #{req.id} - {req.donor.name}")
            self.stdout.write(f"  Date: {req.requested_date} at {req.preferred_time}")
            
            # Check if DonationHistory already exists for this donor on this date
            existing = DonationHistory.objects.filter(
                donor=req.donor,
                donation_date=req.requested_date
            ).first()
            
            if existing:
                self.stdout.write(
                    self.style.SUCCESS(f"  [OK] DonationHistory already exists (ID: {existing.id})")
                )
                already_exists_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING("  [MISSING] DonationHistory not found")
                )
                
                if not dry_run:
                    self.stdout.write("  Creating DonationHistory record...")
                    try:
                        history = DonationHistory.objects.create(
                            donor=req.donor,
                            donation_date=req.requested_date,
                            donation_center_name=f"Scheduled Appointment at {req.preferred_time}",
                            units_donated=1,
                            notes=f"Completed from request #{req.id}. Auto-fixed by fix_donation_history command."
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f"  [CREATED] DonationHistory (ID: {history.id})")
                        )
                        fixed_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"  [ERROR] {e}")
                        )
                        import traceback
                        traceback.print_exc()
                        error_count += 1
                else:
                    self.stdout.write(
                        self.style.NOTICE("  [DRY RUN] Would create DonationHistory record")
                    )
                    fixed_count += 1

        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.NOTICE('SUMMARY'))
        self.stdout.write("="*70)
        self.stdout.write(f"Total completed requests: {completed_requests.count()}")
        self.stdout.write(f"Already had history: {already_exists_count}")
        self.stdout.write(f"{'Would be fixed' if dry_run else 'Fixed (created new)'}: {fixed_count}")
        self.stdout.write(f"Errors: {error_count}")
        self.stdout.write("="*70 + "\n")

        if fixed_count > 0:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        '[DRY RUN] Run without --dry-run to actually create the records.\n'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        '[SUCCESS] Fixed missing donation history records!\n'
                        '  Donors can now see their donation counts updated.\n'
                    )
                )
        elif already_exists_count == completed_requests.count():
            self.stdout.write(
                self.style.SUCCESS(
                    '[SUCCESS] All completed requests already have donation history records.\n'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    '[WARNING] Some records could not be fixed. Check errors above.\n'
                )
            )
