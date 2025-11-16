"""
Django management command to check donation records and statistics
Usage: python manage.py check_donation_records
"""
from django.core.management.base import BaseCommand
from donor.models import DonationHistory, DonationRequest, Donor


class Command(BaseCommand):
    help = 'Check donation history records and statistics'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*60)
        self.stdout.write("DONATION HISTORY CHECK")
        self.stdout.write("="*60)

        total_history = DonationHistory.objects.count()
        self.stdout.write(f"\nTotal DonationHistory records: {total_history}")

        if total_history > 0:
            self.stdout.write("\nDonation History Records:")
            for d in DonationHistory.objects.all():
                self.stdout.write(f"  - {d.donor.name} ({d.donor.blood_group})")
                self.stdout.write(f"    Date: {d.donation_date}")
                self.stdout.write(f"    Center: {d.donation_center_name}")
                self.stdout.write(f"    Units: {d.units_donated}")
                self.stdout.write("")

        self.stdout.write("\n" + "="*60)
        self.stdout.write("DONATION REQUESTS CHECK")
        self.stdout.write("="*60)

        completed_requests = DonationRequest.objects.filter(status='completed')
        self.stdout.write(f"\nTotal Completed Requests: {completed_requests.count()}")

        if completed_requests.exists():
            self.stdout.write("\nCompleted Requests:")
            for req in completed_requests:
                self.stdout.write(f"  - Request #{req.id}: {req.donor.name}")
                self.stdout.write(f"    Date: {req.requested_date} at {req.preferred_time}")
                self.stdout.write(f"    Status: {req.status}")
                self.stdout.write(f"    Completed At: {req.completed_at}")
                self.stdout.write("")

        self.stdout.write("\n" + "="*60)
        self.stdout.write("DONOR STATISTICS")
        self.stdout.write("="*60)

        for donor in Donor.objects.all()[:5]:  # Show first 5 donors
            history_count = DonationHistory.objects.filter(donor=donor).count()
            self.stdout.write(f"\n{donor.name} ({donor.blood_group}):")
            self.stdout.write(f"  - Total donations in history: {history_count}")
            self.stdout.write(f"  - Last donation date: {donor.last_donation_date}")
            self.stdout.write(f"  - Completed requests: {DonationRequest.objects.filter(donor=donor, status='completed').count()}")

        self.stdout.write("\n" + "="*60)
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n[SUCCESS] Donation records check completed successfully.\n'
            )
        )
