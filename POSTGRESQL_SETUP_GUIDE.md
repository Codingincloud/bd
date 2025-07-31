# 🐘 PostgreSQL Setup Guide for Blood Donation System

## ✅ **Django Settings Already Updated!**

The Django settings have been updated to use PostgreSQL:
- **Database:** `blood_donation_db`
- **User:** `blood_donation_user`
- **Password:** `blood_donation_pass`
- **Host:** `localhost`
- **Port:** `5432`

---

## 🚀 **Option 1: Install PostgreSQL on Windows (Recommended)**

### **Step 1: Download PostgreSQL**
1. Go to: https://www.postgresql.org/download/windows/
2. Download the PostgreSQL installer for Windows
3. Run the installer as Administrator

### **Step 2: Installation Settings**
- **Port:** 5432 (default)
- **Superuser Password:** Choose a strong password (remember this!)
- **Locale:** Default
- **Components:** Install all components

### **Step 3: Create Database and User**
After installation, open **pgAdmin** or **SQL Shell (psql)** and run:

```sql
-- Create database
CREATE DATABASE blood_donation_db;

-- Create user
CREATE USER blood_donation_user WITH PASSWORD 'blood_donation_pass';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE blood_donation_db TO blood_donation_user;

-- Grant schema privileges
\c blood_donation_db
GRANT ALL ON SCHEMA public TO blood_donation_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO blood_donation_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO blood_donation_user;
```

---

## 🐳 **Option 2: Docker PostgreSQL (Easiest)**

### **Step 1: Install Docker Desktop**
1. Download from: https://www.docker.com/products/docker-desktop/
2. Install and start Docker Desktop

### **Step 2: Run PostgreSQL Container**
Open PowerShell and run:

```powershell
docker run --name blood-donation-postgres `
  -e POSTGRES_DB=blood_donation_db `
  -e POSTGRES_USER=blood_donation_user `
  -e POSTGRES_PASSWORD=blood_donation_pass `
  -p 5432:5432 `
  -d postgres:15
```

### **Step 3: Verify Container is Running**
```powershell
docker ps
```

---

## ☁️ **Option 3: Cloud PostgreSQL (Production Ready)**

### **Free Cloud Options:**
1. **Supabase** (https://supabase.com/) - Free tier with 500MB
2. **ElephantSQL** (https://www.elephantsql.com/) - Free tier with 20MB
3. **Aiven** (https://aiven.io/) - Free trial
4. **Railway** (https://railway.app/) - Free tier

### **Update Settings for Cloud:**
Replace the database settings in `blood_donation/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_cloud_db_name',
        'USER': 'your_cloud_username',
        'PASSWORD': 'your_cloud_password',
        'HOST': 'your_cloud_host',
        'PORT': '5432',
    }
}
```

---

## 🔧 **After PostgreSQL is Set Up**

### **Step 1: Test Connection**
```powershell
cd g:\org_don
python manage.py dbshell
```

### **Step 2: Run Migrations**
```powershell
python manage.py makemigrations
python manage.py migrate
```

### **Step 3: Create Superuser**
```powershell
python manage.py createsuperuser
```

### **Step 4: Create Test Users**
```powershell
python manage.py create_test_users
```

---

## 🔄 **Migration from SQLite to PostgreSQL**

### **Option A: Fresh Start (Recommended)**
1. Set up PostgreSQL
2. Run migrations to create fresh tables
3. Use the `create_test_users` command to recreate users

### **Option B: Data Migration (Advanced)**
```powershell
# Export data from SQLite
python manage.py dumpdata --natural-foreign --natural-primary > data.json

# Switch to PostgreSQL settings
# Run migrations
python manage.py migrate

# Import data
python manage.py loaddata data.json
```

---

## 🛠️ **Troubleshooting**

### **Connection Error:**
```
django.db.utils.OperationalError: could not connect to server
```
**Solution:** Make sure PostgreSQL is running and credentials are correct.

### **Permission Error:**
```
django.db.utils.ProgrammingError: permission denied
```
**Solution:** Grant proper privileges to the user (see SQL commands above).

### **Port Already in Use:**
```
Error: port 5432 already in use
```
**Solution:** Stop existing PostgreSQL service or use different port.

---

## 📋 **Quick Setup Commands**

### **For Docker Users:**
```powershell
# Start PostgreSQL
docker run --name blood-donation-postgres -e POSTGRES_DB=blood_donation_db -e POSTGRES_USER=blood_donation_user -e POSTGRES_PASSWORD=blood_donation_pass -p 5432:5432 -d postgres:15

# Run migrations
cd g:\org_don
python manage.py migrate

# Create test users
python manage.py create_test_users

# Start Django server
python manage.py runserver
```

### **For Local PostgreSQL:**
```powershell
# After installing PostgreSQL and creating database
cd g:\org_don
python manage.py migrate
python manage.py create_test_users
python manage.py runserver
```

---

## 🎯 **Benefits of PostgreSQL**

✅ **Better Performance** - Faster queries and better optimization
✅ **Scalability** - Handle more users and data
✅ **Advanced Features** - JSON fields, full-text search, etc.
✅ **Production Ready** - Used by major applications
✅ **Better Concurrency** - Multiple users can access simultaneously
✅ **Data Integrity** - Better ACID compliance
✅ **Backup & Recovery** - Professional backup solutions

---

## 🚨 **Important Notes**

1. **Backup SQLite Data** before switching (if you have important data)
2. **Test Connection** before running migrations
3. **Update Environment Variables** for production deployment
4. **Use Strong Passwords** for production databases
5. **Enable SSL** for production connections

---

## 🔗 **Next Steps**

1. Choose your preferred PostgreSQL setup method
2. Follow the setup instructions
3. Run the migration commands
4. Test the application with PostgreSQL
5. Enjoy better database performance!

**The Django settings are already configured for PostgreSQL - just set up the database and run migrations! 🐘✨**
