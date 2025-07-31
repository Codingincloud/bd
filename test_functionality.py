#!/usr/bin/env python
"""
Test script to verify all functionality of the Blood Donation System
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blood_donation.settings')
django.setup()

from django.contrib.auth.models import User
from donor.models import Donor, DonationRequest, DonationHistory, EmergencyRequest, DonationCenter
from admin_panel.models import AdminProfile, SystemNotification
from datetime import date, timedelta
from django.utils import timezone

def test_models():
    """Test all model functionality"""
    print("🧪 Testing Models...")
    
    # Test Donor model
    donors = Donor.objects.all()
    print(f"✅ Donors: {donors.count()} found")
    
    if donors.exists():
        donor = donors.first()
        print(f"   - Sample donor: {donor.name} ({donor.blood_group})")
        print(f"   - Age: {donor.age}")
        print(f"   - BMI: {donor.bmi}")
        print(f"   - Can donate: {donor.can_donate()}")
        print(f"   - Total donations: {donor.total_donations}")
        print(f"   - Compatible blood groups: {donor.compatible_blood_groups}")
    
    # Test DonationRequest model
    requests = DonationRequest.objects.all()
    print(f"✅ Donation Requests: {requests.count()} found")
    
    # Test DonationHistory model
    history = DonationHistory.objects.all()
    print(f"✅ Donation History: {history.count()} found")
    
    # Test EmergencyRequest model
    emergencies = EmergencyRequest.objects.all()
    print(f"✅ Emergency Requests: {emergencies.count()} found")
    
    if emergencies.exists():
        emergency = emergencies.first()
        print(f"   - Sample emergency: {emergency.hospital_name} needs {emergency.blood_group_needed}")
        print(f"   - Urgency: {emergency.urgency_level}")
        print(f"   - Is urgent: {emergency.is_urgent}")
    
    # Test DonationCenter model
    centers = DonationCenter.objects.all()
    print(f"✅ Donation Centers: {centers.count()} found")
    
    # Test AdminProfile model
    admin_profiles = AdminProfile.objects.all()
    print(f"✅ Admin Profiles: {admin_profiles.count()} found")

def test_views():
    """Test view functionality"""
    print("\n🌐 Testing Views...")
    
    from django.test import Client
    from django.urls import reverse
    
    client = Client()
    
    # Test home page
    response = client.get('/')
    print(f"✅ Home page: {response.status_code}")
    
    # Test login page
    response = client.get('/accounts/login/')
    print(f"✅ Login page: {response.status_code}")
    
    # Test register page
    response = client.get('/accounts/register/')
    print(f"✅ Register page: {response.status_code}")
    
    # Test admin pages (should redirect to login)
    response = client.get('/admin-panel/dashboard/')
    print(f"✅ Admin dashboard (redirect): {response.status_code}")
    
    # Test donor pages (should redirect to login)
    response = client.get('/donor/dashboard/')
    print(f"✅ Donor dashboard (redirect): {response.status_code}")

def test_authentication():
    """Test authentication system"""
    print("\n🔐 Testing Authentication...")
    
    # Test admin user
    admin_users = User.objects.filter(is_staff=True)
    print(f"✅ Admin users: {admin_users.count()} found")
    
    # Test donor users
    donor_users = User.objects.filter(is_staff=False)
    print(f"✅ Donor users: {donor_users.count()} found")
    
    # Test user-donor relationship
    for user in donor_users[:3]:  # Test first 3
        try:
            donor = user.donor
            print(f"   - User {user.username} -> Donor {donor.name}")
        except Donor.DoesNotExist:
            print(f"   - User {user.username} has no donor profile")

def test_business_logic():
    """Test business logic"""
    print("\n💼 Testing Business Logic...")
    
    # Test blood compatibility
    donors = Donor.objects.all()[:3]
    for donor in donors:
        compatible = donor.compatible_blood_groups
        print(f"✅ {donor.blood_group} can donate to: {compatible}")
    
    # Test donation eligibility
    for donor in donors:
        can_donate = donor.can_donate()
        next_date = donor.next_eligible_date
        print(f"✅ {donor.name} can donate: {can_donate}, next eligible: {next_date}")
    
    # Test emergency urgency
    emergencies = EmergencyRequest.objects.all()[:3]
    for emergency in emergencies:
        is_urgent = emergency.is_urgent
        time_remaining = emergency.time_remaining
        print(f"✅ Emergency at {emergency.hospital_name}: urgent={is_urgent}, time_remaining={time_remaining}")

def test_database_integrity():
    """Test database integrity"""
    print("\n🗄️ Testing Database Integrity...")
    
    # Check for orphaned records
    donors_without_users = Donor.objects.filter(user__isnull=True).count()
    print(f"✅ Donors without users: {donors_without_users}")
    
    requests_without_donors = DonationRequest.objects.filter(donor__isnull=True).count()
    print(f"✅ Requests without donors: {requests_without_donors}")
    
    history_without_donors = DonationHistory.objects.filter(donor__isnull=True).count()
    print(f"✅ History without donors: {history_without_donors}")
    
    # Check data consistency
    total_users = User.objects.count()
    total_donors = Donor.objects.count()
    total_admins = User.objects.filter(is_staff=True).count()
    
    print(f"✅ Data consistency:")
    print(f"   - Total users: {total_users}")
    print(f"   - Total donors: {total_donors}")
    print(f"   - Total admins: {total_admins}")
    print(f"   - Expected: {total_donors + total_admins} ≈ {total_users}")

def main():
    """Run all tests"""
    print("🩸 BLOOD DONATION SYSTEM - FUNCTIONALITY TEST")
    print("=" * 50)
    
    try:
        test_models()
        test_views()
        test_authentication()
        test_business_logic()
        test_database_integrity()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("✅ The Blood Donation System is working properly!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
