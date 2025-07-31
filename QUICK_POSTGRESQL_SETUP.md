# 🚀 Quick PostgreSQL Setup for Your Configuration

## ✅ **Django Settings Updated!**

Your PostgreSQL configuration is now active:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '1',
        'USER': 'postgres',
        'PASSWORD': '1',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🔧 **Current Issue**
PostgreSQL server is not running on localhost:5432. Here are quick solutions:

---

## 🐳 **Option 1: Quick Docker Setup (Recommended)**

### **Step 1: Install Docker Desktop**
- Download: https://www.docker.com/products/docker-desktop/
- Install and start Docker Desktop

### **Step 2: Run PostgreSQL with Your Settings**
Open PowerShell and run:
```powershell
docker run --name postgres-blood-donation `
  -e POSTGRES_DB=1 `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=1 `
  -p 5432:5432 `
  -d postgres:15
```

### **Step 3: Test Connection**
```powershell
cd g:\org_don
python manage.py migrate
```

---

## 💻 **Option 2: Install PostgreSQL Locally**

### **Step 1: Download PostgreSQL**
- Go to: https://www.postgresql.org/download/windows/
- Download and install PostgreSQL 15 or 16

### **Step 2: During Installation**
- **Port:** 5432
- **Superuser (postgres) Password:** 1
- **Locale:** Default

### **Step 3: Create Database**
After installation, open **SQL Shell (psql)** and run:
```sql
-- Login with user: postgres, password: 1
CREATE DATABASE "1";
```

### **Step 4: Test Django Connection**
```powershell
cd g:\org_don
python manage.py migrate
```

---

## ☁️ **Option 3: Free Cloud PostgreSQL**

### **Supabase (Recommended)**
1. Go to: https://supabase.com/
2. Create free account
3. Create new project
4. Get connection details
5. Update settings.py with cloud credentials

### **Example Cloud Settings:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.your_project_ref',
        'PASSWORD': 'your_password',
        'HOST': 'db.your_project_ref.supabase.co',
        'PORT': '5432',
    }
}
```

---

## 🔄 **Option 4: Temporary SQLite Fallback**

If you want to continue development while setting up PostgreSQL:

```python
# Temporary SQLite configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Then switch back to PostgreSQL when ready.

---

## 🎯 **Recommended Quick Start**

### **For Immediate Development:**
```powershell
# Option 1: Use Docker (if you have it)
docker run --name postgres-blood-donation -e POSTGRES_DB=1 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=1 -p 5432:5432 -d postgres:15

# Option 2: Temporarily switch to SQLite
# (Edit settings.py to use SQLite, then switch back later)
```

### **After PostgreSQL is Running:**
```powershell
cd g:\org_don
python manage.py migrate
python manage.py create_test_users
python manage.py runserver
```

---

## 🔍 **Check if PostgreSQL is Running**

### **Windows Services:**
1. Press `Win + R`, type `services.msc`
2. Look for "postgresql" service
3. Start if stopped

### **Command Line Check:**
```powershell
netstat -an | findstr :5432
```

### **Docker Check:**
```powershell
docker ps
```

---

## 🚨 **Troubleshooting**

### **Connection Refused Error:**
- PostgreSQL is not running
- Wrong port (check if it's 5433 instead of 5432)
- Firewall blocking connection

### **Authentication Failed:**
- Wrong username/password
- User doesn't exist
- Database doesn't exist

### **Quick Fix Commands:**
```powershell
# Check PostgreSQL status
sc query postgresql-x64-15

# Start PostgreSQL service
net start postgresql-x64-15

# Create database (if PostgreSQL is running)
createdb -U postgres 1
```

---

## 🎉 **Once PostgreSQL is Working**

Your blood donation system will have:
✅ **Better Performance** - Faster queries
✅ **Better Concurrency** - Multiple users
✅ **Production Ready** - Scalable database
✅ **Advanced Features** - JSON fields, full-text search
✅ **Better Backup** - Professional backup tools

---

## 📞 **Need Help?**

1. **Check Docker:** `docker --version`
2. **Check PostgreSQL:** Look in Windows Services
3. **Try Cloud Option:** Supabase for instant setup
4. **Temporary SQLite:** Continue development while setting up

**The Django app is ready for PostgreSQL - just need to get the database server running! 🐘✨**
