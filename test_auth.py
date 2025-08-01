#!/usr/bin/env python
"""
Test script for authentication functionality
"""
import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blood_donation.settings')
django.setup()

from donor.models import Donor
from admin_panel.models import AdminProfile

def test_donor_registration():
    """Test donor registration functionality"""
    print("Testing donor registration...")
    
    client = Client()
    
    # Test data for donor registration
    donor_data = {
        'username': 'testdonor',
        'password': 'testpass123',
        'email': 'donor@test.com',
        'role': 'donor',
        'name': 'Test Donor',
        'blood_group': 'O+',
        'contact_no': '9876543210',
        'address': 'Test Address',
        'date_of_birth': '1995-01-01',
        'gender': 'M',
        'weight': '70.0',
        'city': 'Kathmandu',
        'state': 'Bagmati',
        'country': 'Nepal'
    }
    
    try:
        response = client.post('/accounts/register/', donor_data)
        
        if response.status_code == 302:  # Redirect after successful registration
            print("✓ Donor registration successful")
            
            # Check if user was created
            user = User.objects.get(username='testdonor')
            print(f"✓ User created: {user.username}")
            
            # Check if donor profile was created
            donor = Donor.objects.get(user=user)
            print(f"✓ Donor profile created: {donor.blood_group}")
            
            return True
        else:
            print(f"✗ Donor registration failed with status: {response.status_code}")
            if hasattr(response, 'context') and response.context:
                errors = response.context.get('errors', [])
                error = response.context.get('error', '')
                if errors:
                    print(f"Validation errors: {errors}")
                if error:
                    print(f"Error: {error}")
            return False
            
    except Exception as e:
        print(f"✗ Donor registration error: {e}")
        return False

def test_admin_registration():
    """Test admin registration functionality"""
    print("\nTesting admin registration...")
    
    client = Client()
    
    # Test data for admin registration
    admin_data = {
        'username': 'testadmin',
        'password': 'testpass123',
        'email': 'admin@test.com',
        'role': 'admin',
        'admin_name': 'Test Admin',
        'admin_contact_no': '9876543211',
        'admin_address': 'Admin Address',
        'admin_city': 'Kathmandu',
        'admin_state': 'Bagmati',
        'admin_country': 'Nepal'
    }
    
    try:
        response = client.post('/accounts/register/', admin_data)
        
        if response.status_code == 302:  # Redirect after successful registration
            print("✓ Admin registration successful")
            
            # Check if user was created
            user = User.objects.get(username='testadmin')
            print(f"✓ User created: {user.username}, is_staff: {user.is_staff}")
            
            # Check if admin profile was created
            admin = AdminProfile.objects.get(user=user)
            print(f"✓ Admin profile created: {admin.name}")
            
            return True
        else:
            print(f"✗ Admin registration failed with status: {response.status_code}")
            if hasattr(response, 'context') and response.context:
                errors = response.context.get('errors', [])
                error = response.context.get('error', '')
                if errors:
                    print(f"Validation errors: {errors}")
                if error:
                    print(f"Error: {error}")
            return False
            
    except Exception as e:
        print(f"✗ Admin registration error: {e}")
        return False

def test_donor_login():
    """Test donor login functionality"""
    print("\nTesting donor login...")
    
    client = Client()
    
    login_data = {
        'username': 'testdonor',
        'password': 'testpass123',
        'role': 'donor'
    }
    
    try:
        response = client.post('/accounts/login/', login_data)
        
        if response.status_code == 302:  # Redirect after successful login
            print("✓ Donor login successful")
            return True
        else:
            print(f"✗ Donor login failed with status: {response.status_code}")
            if hasattr(response, 'context') and response.context:
                error = response.context.get('error', '')
                if error:
                    print(f"Error: {error}")
            return False
            
    except Exception as e:
        print(f"✗ Donor login error: {e}")
        return False

def test_admin_login():
    """Test admin login functionality"""
    print("\nTesting admin login...")
    
    client = Client()
    
    login_data = {
        'username': 'testadmin',
        'password': 'testpass123',
        'role': 'admin'
    }
    
    try:
        response = client.post('/accounts/login/', login_data)
        
        if response.status_code == 302:  # Redirect after successful login
            print("✓ Admin login successful")
            return True
        else:
            print(f"✗ Admin login failed with status: {response.status_code}")
            if hasattr(response, 'context') and response.context:
                error = response.context.get('error', '')
                if error:
                    print(f"Error: {error}")
            return False
            
    except Exception as e:
        print(f"✗ Admin login error: {e}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    try:
        # Delete test users and their profiles
        User.objects.filter(username__in=['testdonor', 'testadmin']).delete()
        print("✓ Test data cleaned up")
    except Exception as e:
        print(f"✗ Cleanup error: {e}")

if __name__ == '__main__':
    print("=== Blood Donation System Authentication Tests ===")
    
    # Clean up any existing test data
    cleanup_test_data()
    
    # Run tests
    donor_reg_success = test_donor_registration()
    admin_reg_success = test_admin_registration()
    
    if donor_reg_success:
        donor_login_success = test_donor_login()
    else:
        donor_login_success = False
        
    if admin_reg_success:
        admin_login_success = test_admin_login()
    else:
        admin_login_success = False
    
    # Summary
    print("\n=== Test Results ===")
    print(f"Donor Registration: {'✓ PASS' if donor_reg_success else '✗ FAIL'}")
    print(f"Admin Registration: {'✓ PASS' if admin_reg_success else '✗ FAIL'}")
    print(f"Donor Login: {'✓ PASS' if donor_login_success else '✗ FAIL'}")
    print(f"Admin Login: {'✓ PASS' if admin_login_success else '✗ FAIL'}")
    
    # Clean up
    cleanup_test_data()
    
    if all([donor_reg_success, admin_reg_success, donor_login_success, admin_login_success]):
        print("\n🎉 All tests passed! Authentication system is working properly.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
