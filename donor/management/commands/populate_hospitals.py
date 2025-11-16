from django.core.management.base import BaseCommand
from donor.models import Hospital, DonationCenter
import random

class Command(BaseCommand):
    help = 'Populates the database with initial hospital and donation center data'

    def handle(self, *args, **options):
        # Major cities in Nepal with their coordinates
        NEPAL_CITIES = [
            {'name': 'Kathmandu', 'lat': 27.7172, 'lng': 85.3240},
            {'name': 'Pokhara', 'lat': 28.2096, 'lng': 83.9856},
            {'name': 'Lalitpur', 'lat': 27.6667, 'lng': 85.3167},
            {'name': 'Bharatpur', 'lat': 27.6833, 'lng': 84.4167},
            {'name': 'Biratnagar', 'lat': 26.4833, 'lng': 87.2833},
            {'name': 'Birgunj', 'lat': 27.0000, 'lng': 84.8667},
            {'name': 'Dharan', 'lat': 26.8167, 'lng': 87.2667},
            {'name': 'Butwal', 'lat': 27.7000, 'lng': 83.4500},
            {'name': 'Bhaktapur', 'lat': 27.6722, 'lng': 85.4278},
            {'name': 'Hetauda', 'lat': 27.4167, 'lng': 85.0333},
        ]

        HOSPITAL_TYPES = [
            ('government', 'Government Hospital'),
            ('private', 'Private Hospital'),
            ('blood_bank', 'Blood Bank'),
            ('medical_college', 'Medical College'),
        ]

        HOSPITAL_NAMES = [
            'City Hospital', 'Metro Medical Center', 'Nepal Red Cross',
            'Life Care Hospital', 'Nobel Medical College', 'Grande Hospital',
            'Norvic Hospital', 'Teaching Hospital', 'Bir Hospital',
            'Patan Hospital', 'Civil Hospital', 'Community Medical Center'
        ]

        # Create Hospitals
        for city in NEPAL_CITIES:
            for i in range(2, 5):  # 2-4 hospitals per city
                hospital_type = random.choice(HOSPITAL_TYPES)
                hospital = Hospital.objects.create(
                    name=f"{random.choice(HOSPITAL_NAMES)} - {city['name']}",
                    address=f"{random.randint(1, 100)} {city['name']} Road, {city['name']}",
                    city=city['name'],
                    state='Bagmati' if city['name'] in ['Kathmandu', 'Lalitpur', 'Bhaktapur'] else 'Province 1',
                    phone_number=f"98{random.randint(10000000, 99999999)}",
                    email=f"contact@hospital{random.randint(1, 1000)}.com",
                    latitude=city['lat'] + (random.random() * 0.2 - 0.1),  # Add some randomness to coordinates
                    longitude=city['lng'] + (random.random() * 0.2 - 0.1),
                    hospital_type=hospital_type[0],
                    has_blood_bank=random.choice([True, False]),
                    accepts_donations=random.choice([True, False]),
                    emergency_contact=f"98{random.randint(10000000, 99999999)}",
                    operating_hours=random.choice(['24/7', '9AM-5PM', '8AM-8PM']),
                    services=random.choice([
                        "Blood Donation, Blood Testing, Emergency Care",
                        "Blood Donation, Laboratory Services",
                        "Blood Testing, Donation Services",
                        "Emergency Care, Blood Bank"
                    ]),
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'Created hospital: {hospital.name}'))

        # Create Donation Centers (some hospitals will also be donation centers)
        donation_centers = Hospital.objects.filter(accepts_donations=True)[:10]  # Get first 10 donation centers
        
        for i, hospital in enumerate(donation_centers):
            center = DonationCenter.objects.create(
                name=f"{hospital.name} Donation Center",
                address=hospital.address,
                city=hospital.city,
                state=hospital.state,
                phone_number=hospital.phone_number,
                email=hospital.email,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created donation center: {center.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated hospitals and donation centers!'))
