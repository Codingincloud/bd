# 🩸 Blood Donation System - Login Credentials

## 🔐 Test User Accounts

### 👨‍💼 Admin Account
- **Username:** `admin`
- **Password:** `admin123`
- **Email:** `admin@bloodbank.com`
- **Role:** System Administrator
- **Access:** Full admin panel access

### 🩸 Donor Account 1
- **Username:** `donor`
- **Password:** `donor123`
- **Email:** `donor@bloodbank.com`
- **Name:** John Doe
- **Blood Group:** O+
- **Location:** Kathmandu, Nepal

### 🩸 Donor Account 2
- **Username:** `donor2`
- **Password:** `donor123`
- **Email:** `donor2@bloodbank.com`
- **Name:** Sarah Smith
- **Blood Group:** A+
- **Location:** Lalitpur, Nepal (with GPS coordinates)

## 🌐 Access URLs

### 🔗 Main Pages
- **Home:** http://127.0.0.1:8000/
- **Login:** http://127.0.0.1:8000/accounts/login/
- **Register:** http://127.0.0.1:8000/accounts/register/

### 👨‍💼 Admin Panel (login as admin)
- **Dashboard:** http://127.0.0.1:8000/admin-panel/dashboard/
- **Manage Donors:** http://127.0.0.1:8000/admin-panel/donors/
- **Location Search:** http://127.0.0.1:8000/admin-panel/donors/location-search/
- **Manage Requests:** http://127.0.0.1:8000/admin-panel/requests/
- **Manage Inventory:** http://127.0.0.1:8000/admin-panel/inventory/
- **Emergency Requests:** http://127.0.0.1:8000/admin-panel/emergencies/
- **Reports:** http://127.0.0.1:8000/admin-panel/reports/

### 🩸 Donor Panel (login as donor/donor2)
- **Dashboard:** http://127.0.0.1:8000/donor/dashboard/
- **Edit Profile:** http://127.0.0.1:8000/donor/edit-profile/
- **Schedule Donation:** http://127.0.0.1:8000/donor/schedule-donation/
- **Donation History:** http://127.0.0.1:8000/donor/donation-history/
- **Emergency Requests:** http://127.0.0.1:8000/donor/emergency-requests/

## 🚀 How to Test

### 1. Admin Features
1. Login with admin credentials
2. View dashboard with location statistics
3. Go to "Manage Donors" to see location filters
4. Try "Location Search" for GPS-based donor search
5. Test filtering by city, state, blood group

### 2. Donor Features
1. Login with donor credentials
2. Go to "Edit Profile" to update location information
3. Try the "Get My Current Location" button
4. Update city, state, postal code, and coordinates
5. View how location appears in admin panel

### 3. Registration
1. Go to registration page
2. Test both donor and admin registration
3. Fill in all location fields
4. Verify no duplicate email fields appear

## 🔧 Location Features

### ✅ What's Working
- ✅ Enhanced registration with location fields
- ✅ Location-based donor search with GPS coordinates
- ✅ Distance calculations using Haversine formula
- ✅ Location filtering in admin panel
- ✅ Profile management with location updates
- ✅ Geolocation API integration
- ✅ Location statistics in dashboard
- ✅ City/State/Country filtering

### 🎯 Key Features to Test
1. **Registration:** Complete location data collection
2. **Profile Updates:** Edit location information
3. **GPS Search:** Find donors within radius
4. **Location Filters:** Filter by city/state in admin
5. **Dashboard Stats:** View location distribution
6. **Distance Calc:** Accurate distance measurements

## 🐛 Fixed Issues
- ✅ Removed duplicate email fields in registration
- ✅ Fixed admin profile creation
- ✅ Updated password for existing admin user
- ✅ Created proper test users with location data

## 📱 Mobile Support
- Responsive design for all location features
- Geolocation works on mobile browsers
- Touch-friendly interface for location input

## 🔒 Security Notes
- All location data is optional except basic address
- GPS coordinates are only stored with user consent
- Location search requires admin privileges
- Input validation for all location fields
