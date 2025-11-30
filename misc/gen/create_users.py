import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(r'C:\Users\Acer\OneDrive\Videos\om\BDIMS_version_last\BDIMS')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blood_donation.settings')
django.setup()

from django.contrib.auth.models import User
from donor.models import Donor, Hospital, BloodInventory
from admin_panel.models import AdminProfile
from datetime import date, datetime

print("Starting user creation script...")

# 10 Donor Data with complete information
donors_data = [
    {
        'username': 'ram_sharma', 'password': 'Ram@12345', 'email': 'ram.sharma@email.com',
        'first_name': 'Ram', 'last_name': 'Sharma', 'blood_group': 'O+',
        'dob': date(1995, 5, 15), 'gender': 'M', 'phone': '+977-9841234567',
        'address': 'Thamel, Ward 26', 'city': 'Kathmandu', 'state': 'Bagmati',
        'postal_code': '44600', 'weight': 72.5, 'height': 175.0,
        'latitude': 27.7172, 'longitude': 85.3240,
        'emergency_name': 'Sita Sharma', 'emergency_phone': '+977-9841234568',
        'medical_conditions': 'None'
    },
    {
        'username': 'sita_gurung', 'password': 'Sita@12345', 'email': 'sita.gurung@email.com',
        'first_name': 'Sita', 'last_name': 'Gurung', 'blood_group': 'A+',
        'dob': date(1998, 8, 22), 'gender': 'F', 'phone': '+977-9851234567',
        'address': 'Lakeside, Ward 6', 'city': 'Pokhara', 'state': 'Gandaki',
        'postal_code': '33700', 'weight': 58.0, 'height': 162.0,
        'latitude': 28.2096, 'longitude': 83.9856,
        'emergency_name': 'Krishna Gurung', 'emergency_phone': '+977-9851234568',
        'medical_conditions': 'None'
    },
    {
        'username': 'hari_thapa', 'password': 'Hari@12345', 'email': 'hari.thapa@email.com',
        'first_name': 'Hari', 'last_name': 'Thapa', 'blood_group': 'B+',
        'dob': date(1992, 3, 10), 'gender': 'M', 'phone': '+977-9861234567',
        'address': 'Pulchowk, Ward 3', 'city': 'Lalitpur', 'state': 'Bagmati',
        'postal_code': '44700', 'weight': 78.0, 'height': 180.0,
        'latitude': 27.6588, 'longitude': 85.3247,
        'emergency_name': 'Maya Thapa', 'emergency_phone': '+977-9861234568',
        'medical_conditions': 'None'
    },
    {
        'username': 'gita_rai', 'password': 'Gita@12345', 'email': 'gita.rai@email.com',
        'first_name': 'Gita', 'last_name': 'Rai', 'blood_group': 'AB+',
        'dob': date(1996, 12, 5), 'gender': 'F', 'phone': '+977-9871234567',
        'address': 'Traffic Chowk, Ward 8', 'city': 'Biratnagar', 'state': 'Koshi',
        'postal_code': '56613', 'weight': 62.0, 'height': 165.0,
        'latitude': 26.4525, 'longitude': 87.2718,
        'emergency_name': 'Ramesh Rai', 'emergency_phone': '+977-9871234568',
        'medical_conditions': 'None'
    },
    {
        'username': 'krishna_shah', 'password': 'Krishna@12345', 'email': 'krishna.shah@email.com',
        'first_name': 'Krishna', 'last_name': 'Shah', 'blood_group': 'O-',
        'dob': date(1994, 7, 18), 'gender': 'M', 'phone': '+977-9881234567',
        'address': 'Adarshanagar, Ward 12', 'city': 'Birgunj', 'state': 'Madhesh',
        'postal_code': '44300', 'weight': 75.0, 'height': 172.0,
        'latitude': 27.0104, 'longitude': 84.8803,
        'emergency_name': 'Radha Shah', 'emergency_phone': '+977-9881234568',
        'medical_conditions': 'None'
    },
    {
        'username': 'maya_tamang', 'password': 'Maya@12345', 'email': 'maya.tamang@email.com',
        'first_name': 'Maya', 'last_name': 'Tamang', 'blood_group': 'A-',
        'dob': date(1997, 11, 25), 'gender': 'F', 'phone': '+977-9891234567',
        'address': 'Bhanu Chowk, Ward 5', 'city': 'Dharan', 'state': 'Koshi',
        'postal_code': '56700', 'weight': 55.0, 'height': 160.0,
        'latitude': 26.8147, 'longitude': 87.2789,
        'emergency_name': 'Laxman Tamang', 'emergency_phone': '+977-9891234568',
        'medical_conditions': 'None'
    },
    {
        'username': 'rajesh_poudel', 'password': 'Rajesh@12345', 'email': 'rajesh.poudel@email.com',
        'first_name': 'Rajesh', 'last_name': 'Poudel', 'blood_group': 'B-',
        'dob': date(1993, 4, 30), 'gender': 'M', 'phone': '+977-9801234567',
        'address': 'Makwanpur Gadhi, Ward 10', 'city': 'Hetauda', 'state': 'Bagmati',
        'postal_code': '44107', 'weight': 70.0, 'height': 168.0,
        'latitude': 27.4287, 'longitude': 85.0326,
        'emergency_name': 'Anita Poudel', 'emergency_phone': '+977-9801234568',
        'medical_conditions': 'Mild allergy to penicillin'
    },
    {
        'username': 'sunita_karki', 'password': 'Sunita@12345', 'email': 'sunita.karki@email.com',
        'first_name': 'Sunita', 'last_name': 'Karki', 'blood_group': 'AB-',
        'dob': date(1999, 9, 8), 'gender': 'F', 'phone': '+977-9811234567',
        'address': 'Janakpur Dham, Ward 15', 'city': 'Janakpur', 'state': 'Madhesh',
        'postal_code': '45600', 'weight': 60.0, 'height': 163.0,
        'latitude': 26.7288, 'longitude': 85.9266,
        'emergency_name': 'Mohan Karki', 'emergency_phone': '+977-9811234568',
        'medical_conditions': 'None'
    },
    {
        'username': 'bikash_shrestha', 'password': 'Bikash@12345', 'email': 'bikash.shrestha@email.com',
        'first_name': 'Bikash', 'last_name': 'Shrestha', 'blood_group': 'O+',
        'dob': date(1991, 2, 14), 'gender': 'M', 'phone': '+977-9821234567',
        'address': 'Traffic Chowk, Ward 20', 'city': 'Butwal', 'state': 'Lumbini',
        'postal_code': '32907', 'weight': 82.0, 'height': 178.0,
        'latitude': 27.7000, 'longitude': 83.4500,
        'emergency_name': 'Puja Shrestha', 'emergency_phone': '+977-9821234568',
        'medical_conditions': 'None'
    },
    {
        'username': 'anita_nepal', 'password': 'Anita@12345', 'email': 'anita.nepal@email.com',
        'first_name': 'Anita', 'last_name': 'Nepal', 'blood_group': 'A+',
        'dob': date(2000, 6, 20), 'gender': 'F', 'phone': '+977-9831234567',
        'address': 'Durbar Marg, Ward 5', 'city': 'Bhaktapur', 'state': 'Bagmati',
        'postal_code': '44800', 'weight': 57.0, 'height': 161.0,
        'latitude': 27.6710, 'longitude': 85.4298,
        'emergency_name': 'Bijay Nepal', 'emergency_phone': '+977-9831234568',
        'medical_conditions': 'None'
    }
]

# 10 Admin/Hospital Data with real hospital information
hospitals_data = [
    {
        'username': 'admin_tribhuvan', 'password': 'Admin@12345', 'email': 'admin@tuth.edu.np',
        'first_name': 'Tribhuvan', 'last_name': 'Hospital Admin',
        'admin_name': 'Dr. Ramesh Kumar Sharma', 'contact': '+977-01-4217766',
        'address': 'Maharajgunj, Kathmandu', 'city': 'Kathmandu', 'state': 'Bagmati',
        'postal_code': '44600', 'hospital_name': 'Tribhuvan University Teaching Hospital',
        'hospital_phone': '+977-01-4217766', 'hospital_email': 'info@tuth.edu.np',
        'hospital_address': 'Maharajgunj, Kathmandu', 'hospital_city': 'Kathmandu',
        'hospital_state': 'Bagmati', 'hospital_type': 'medical_college',
        'services': 'Blood Collection, Blood Testing, Emergency Supply, Blood Banking, Component Separation',
        'operating_hours': '24/7', 'latitude': 27.7353, 'longitude': 85.3350
    },
    {
        'username': 'admin_patan', 'password': 'Admin@12345', 'email': 'admin@pahs.edu.np',
        'first_name': 'Patan', 'last_name': 'Hospital Admin',
        'admin_name': 'Dr. Sushila Devi Thapa', 'contact': '+977-01-5522295',
        'address': 'Lagankhel, Lalitpur', 'city': 'Lalitpur', 'state': 'Bagmati',
        'postal_code': '44700', 'hospital_name': 'Patan Hospital',
        'hospital_phone': '+977-01-5522295', 'hospital_email': 'info@pahs.edu.np',
        'hospital_address': 'Lagankhel, Lalitpur', 'hospital_city': 'Lalitpur',
        'hospital_state': 'Bagmati', 'hospital_type': 'medical_college',
        'services': 'Blood Collection, Blood Testing, Emergency Supply, Blood Banking',
        'operating_hours': '24/7', 'latitude': 27.6648, 'longitude': 85.3242
    },
    {
        'username': 'admin_birgunj', 'password': 'Admin@12345', 'email': 'admin@nghbirgunj.gov.np',
        'first_name': 'Narayani', 'last_name': 'Hospital Admin',
        'admin_name': 'Dr. Krishna Prasad Yadav', 'contact': '+977-051-522866',
        'address': 'Adarshanagar, Birgunj', 'city': 'Birgunj', 'state': 'Madhesh',
        'postal_code': '44300', 'hospital_name': 'Narayani Hospital',
        'hospital_phone': '+977-051-522866', 'hospital_email': 'info@nghbirgunj.gov.np',
        'hospital_address': 'Adarshanagar, Birgunj', 'hospital_city': 'Birgunj',
        'hospital_state': 'Madhesh', 'hospital_type': 'government',
        'services': 'Blood Collection, Blood Testing, Emergency Supply',
        'operating_hours': '24/7', 'latitude': 27.0114, 'longitude': 84.8842
    },
    {
        'username': 'admin_pokhara', 'password': 'Admin@12345', 'email': 'admin@gandaki.gov.np',
        'first_name': 'Gandaki', 'last_name': 'Hospital Admin',
        'admin_name': 'Dr. Binod Kumar Gurung', 'contact': '+977-061-532323',
        'address': 'Prithvi Chowk, Pokhara', 'city': 'Pokhara', 'state': 'Gandaki',
        'postal_code': '33700', 'hospital_name': 'Gandaki Medical College',
        'hospital_phone': '+977-061-532323', 'hospital_email': 'info@gandaki.gov.np',
        'hospital_address': 'Prithvi Chowk, Pokhara', 'hospital_city': 'Pokhara',
        'hospital_state': 'Gandaki', 'hospital_type': 'medical_college',
        'services': 'Blood Collection, Blood Testing, Emergency Supply, Blood Banking',
        'operating_hours': '24/7', 'latitude': 28.2096, 'longitude': 83.9856
    },
    {
        'username': 'admin_biratnagar', 'password': 'Admin@12345', 'email': 'admin@nobel.edu.np',
        'first_name': 'Nobel', 'last_name': 'Hospital Admin',
        'admin_name': 'Dr. Prakash Kumar Rai', 'contact': '+977-021-571333',
        'address': 'Biratnagar-5, Traffic Chowk', 'city': 'Biratnagar', 'state': 'Koshi',
        'postal_code': '56613', 'hospital_name': 'Nobel Medical College',
        'hospital_phone': '+977-021-571333', 'hospital_email': 'info@nobel.edu.np',
        'hospital_address': 'Biratnagar-5, Traffic Chowk', 'hospital_city': 'Biratnagar',
        'hospital_state': 'Koshi', 'hospital_type': 'medical_college',
        'services': 'Blood Collection, Blood Testing, Emergency Supply, Component Separation',
        'operating_hours': '24/7', 'latitude': 26.4539, 'longitude': 87.2693
    },
    {
        'username': 'admin_bharatpur', 'password': 'Admin@12345', 'email': 'admin@bpkihs.edu',
        'first_name': 'Bharatpur', 'last_name': 'Hospital Admin',
        'admin_name': 'Dr. Sunita Kumari Shrestha', 'contact': '+977-056-525555',
        'address': 'Hospital Road, Bharatpur', 'city': 'Bharatpur', 'state': 'Bagmati',
        'postal_code': '44200', 'hospital_name': 'Chitwan Medical College',
        'hospital_phone': '+977-056-525555', 'hospital_email': 'info@bpkihs.edu',
        'hospital_address': 'Hospital Road, Bharatpur', 'hospital_city': 'Bharatpur',
        'hospital_state': 'Bagmati', 'hospital_type': 'medical_college',
        'services': 'Blood Collection, Blood Testing, Emergency Supply',
        'operating_hours': '24/7', 'latitude': 27.6789, 'longitude': 84.4344
    },
    {
        'username': 'admin_dharan', 'password': 'Admin@12345', 'email': 'admin@bpkihs.edu.np',
        'first_name': 'BPKIHS', 'last_name': 'Hospital Admin',
        'admin_name': 'Dr. Laxman Kumar Tamang', 'contact': '+977-025-525555',
        'address': 'BPKIHS Campus, Dharan', 'city': 'Dharan', 'state': 'Koshi',
        'postal_code': '56700', 'hospital_name': 'B.P. Koirala Institute of Health Sciences',
        'hospital_phone': '+977-025-525555', 'hospital_email': 'info@bpkihs.edu.np',
        'hospital_address': 'BPKIHS Campus, Dharan', 'hospital_city': 'Dharan',
        'hospital_state': 'Koshi', 'hospital_type': 'medical_college',
        'services': 'Blood Collection, Blood Testing, Emergency Supply, Blood Banking, Component Separation',
        'operating_hours': '24/7', 'latitude': 26.8194, 'longitude': 87.2833
    },
    {
        'username': 'admin_janakpur', 'password': 'Admin@12345', 'email': 'admin@jpmch.gov.np',
        'first_name': 'Janakpur', 'last_name': 'Hospital Admin',
        'admin_name': 'Dr. Mohan Prasad Karki', 'contact': '+977-041-521077',
        'address': 'Janakpur Dham, Hospital Road', 'city': 'Janakpur', 'state': 'Madhesh',
        'postal_code': '45600', 'hospital_name': 'Janakpur Provincial Hospital',
        'hospital_phone': '+977-041-521077', 'hospital_email': 'info@jpmch.gov.np',
        'hospital_address': 'Janakpur Dham, Hospital Road', 'hospital_city': 'Janakpur',
        'hospital_state': 'Madhesh', 'hospital_type': 'government',
        'services': 'Blood Collection, Blood Testing, Emergency Supply',
        'operating_hours': '24/7', 'latitude': 26.7271, 'longitude': 85.9248
    },
    {
        'username': 'admin_butwal', 'password': 'Admin@12345', 'email': 'admin@lumbini.gov.np',
        'first_name': 'Lumbini', 'last_name': 'Hospital Admin',
        'admin_name': 'Dr. Puja Devi Shrestha', 'contact': '+977-071-540666',
        'address': 'Milanchowk, Butwal', 'city': 'Butwal', 'state': 'Lumbini',
        'postal_code': '32907', 'hospital_name': 'Lumbini Provincial Hospital',
        'hospital_phone': '+977-071-540666', 'hospital_email': 'info@lumbini.gov.np',
        'hospital_address': 'Milanchowk, Butwal', 'hospital_city': 'Butwal',
        'hospital_state': 'Lumbini', 'hospital_type': 'government',
        'services': 'Blood Collection, Blood Testing, Emergency Supply',
        'operating_hours': '24/7', 'latitude': 27.7030, 'longitude': 83.4589
    },
    {
        'username': 'admin_bhaktapur', 'password': 'Admin@12345', 'email': 'admin@bhaktapur.gov.np',
        'first_name': 'Bhaktapur', 'last_name': 'Hospital Admin',
        'admin_name': 'Dr. Bijay Kumar Nepal', 'contact': '+977-01-6611934',
        'address': 'Dudhpati, Bhaktapur', 'city': 'Bhaktapur', 'state': 'Bagmati',
        'postal_code': '44800', 'hospital_name': 'Bhaktapur Cancer Hospital',
        'hospital_phone': '+977-01-6611934', 'hospital_email': 'info@bhaktapur.gov.np',
        'hospital_address': 'Dudhpati, Bhaktapur', 'hospital_city': 'Bhaktapur',
        'hospital_state': 'Bagmati', 'hospital_type': 'government',
        'services': 'Blood Collection, Blood Testing, Emergency Supply, Blood Banking',
        'operating_hours': '24/7', 'latitude': 27.6722, 'longitude': 85.4281
    }
]

credentials_list = []

# Create Donors
print("\n=== Creating Donors ===")
for donor_data in donors_data:
    try:
        # Create User
        user = User.objects.create_user(
            username=donor_data['username'],
            password=donor_data['password'],
            email=donor_data['email'],
            first_name=donor_data['first_name'],
            last_name=donor_data['last_name']
        )
        
        # Create Donor Profile
        donor = Donor.objects.create(
            user=user,
            blood_group=donor_data['blood_group'],
            date_of_birth=donor_data['dob'],
            gender=donor_data['gender'],
            phone_number=donor_data['phone'],
            address=donor_data['address'],
            city=donor_data['city'],
            state=donor_data['state'],
            postal_code=donor_data['postal_code'],
            country='Nepal',
            latitude=donor_data['latitude'],
            longitude=donor_data['longitude'],
            weight=donor_data['weight'],
            height=donor_data['height'],
            medical_conditions=donor_data['medical_conditions'],
            emergency_contact_name=donor_data['emergency_name'],
            emergency_contact_phone=donor_data['emergency_phone'],
            allow_emergency_contact=True,
            is_eligible=True
        )
        
        credentials_list.append(f"DONOR - Username: {donor_data['username']}, Password: {donor_data['password']}, Role: Donor")
        print(f"✓ Created donor: {donor_data['username']} ({donor_data['blood_group']})")
        
    except Exception as e:
        print(f"✗ Error creating donor {donor_data['username']}: {str(e)}")

# Create Admins and Hospitals
print("\n=== Creating Admins and Hospitals ===")
blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']

for hospital_data in hospitals_data:
    try:
        # Create User with admin privileges
        user = User.objects.create_user(
            username=hospital_data['username'],
            password=hospital_data['password'],
            email=hospital_data['email'],
            first_name=hospital_data['first_name'],
            last_name=hospital_data['last_name'],
            is_staff=True,
            is_superuser=True
        )
        
        # Create Admin Profile
        admin_profile = AdminProfile.objects.create(
            user=user,
            name=hospital_data['admin_name'],
            contact_no=hospital_data['contact'],
            address=hospital_data['address'],
            city=hospital_data['city'],
            state=hospital_data['state'],
            postal_code=hospital_data['postal_code'],
            country='Nepal',
            email=hospital_data['email']
        )
        
        # Create Hospital
        hospital = Hospital.objects.create(
            admin_user=user,
            name=hospital_data['hospital_name'],
            phone_number=hospital_data['hospital_phone'],
            email=hospital_data['hospital_email'],
            address=hospital_data['hospital_address'],
            city=hospital_data['hospital_city'],
            state=hospital_data['hospital_state'],
            hospital_type=hospital_data['hospital_type'],
            services=hospital_data['services'],
            operating_hours=hospital_data['operating_hours'],
            latitude=hospital_data['latitude'],
            longitude=hospital_data['longitude'],
            has_blood_bank=True,
            accepts_donations=True,
            is_active=True
        )
        
        # Initialize Blood Inventory for each blood group
        for blood_group in blood_groups:
            BloodInventory.objects.create(
                hospital=hospital,
                blood_group=blood_group,
                units_available=0.0,
                units_reserved=0.0,
                updated_by=user,
                notes=f'Initialized during hospital creation'
            )
        
        credentials_list.append(f"ADMIN - Username: {hospital_data['username']}, Password: {hospital_data['password']}, Role: Admin, Hospital: {hospital_data['hospital_name']}")
        print(f"✓ Created admin: {hospital_data['username']} for {hospital_data['hospital_name']}")
        
    except Exception as e:
        print(f"✗ Error creating admin {hospital_data['username']}: {str(e)}")

# Save credentials to file
print("\n=== Saving Credentials ===")
credentials_file = r'C:\Users\Acer\OneDrive\Videos\om\BDIMS_version_last\BDIMS\gen\cred.txt'
with open(credentials_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("BDIMS - User Credentials\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("DONOR ACCOUNTS (10)\n")
    f.write("-" * 80 + "\n")
    for cred in credentials_list[:10]:
        f.write(cred + "\n")
    
    f.write("\n" + "=" * 80 + "\n\n")
    f.write("ADMIN ACCOUNTS (10)\n")
    f.write("-" * 80 + "\n")
    for cred in credentials_list[10:]:
        f.write(cred + "\n")
    
    f.write("\n" + "=" * 80 + "\n")
    f.write("All passwords follow the same pattern: Capitalize first letter + @12345\n")
    f.write("=" * 80 + "\n")

print(f"✓ Credentials saved to: {credentials_file}")
print("\n=== Script Completed Successfully ===")
print(f"Created: {len(donors_data)} Donors, {len(hospitals_data)} Admins with Hospitals")
