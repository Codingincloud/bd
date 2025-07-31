@echo off
echo ========================================
echo Blood Donation System - PostgreSQL Setup
echo ========================================
echo.

echo Checking if Docker is available...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not installed or not in PATH.
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo Docker found! Setting up PostgreSQL...
echo.

echo Stopping any existing PostgreSQL container...
docker stop postgres-blood-donation >nul 2>&1
docker rm postgres-blood-donation >nul 2>&1

echo Starting PostgreSQL container with your settings...
docker run --name postgres-blood-donation ^
  -e POSTGRES_DB=1 ^
  -e POSTGRES_USER=postgres ^
  -e POSTGRES_PASSWORD=1 ^
  -p 5432:5432 ^
  -d postgres:15

if %errorlevel% neq 0 (
    echo Failed to start PostgreSQL container.
    echo Please check Docker Desktop is running.
    pause
    exit /b 1
)

echo.
echo Waiting for PostgreSQL to start...
timeout /t 10 /nobreak >nul

echo.
echo Testing database connection...
python manage.py check --database default

if %errorlevel% neq 0 (
    echo Database connection failed. Please check the setup.
    pause
    exit /b 1
)

echo.
echo Running database migrations...
python manage.py migrate

if %errorlevel% neq 0 (
    echo Migration failed. Please check the database setup.
    pause
    exit /b 1
)

echo.
echo Creating test users...
python manage.py create_test_users

echo.
echo ========================================
echo PostgreSQL Setup Complete!
echo ========================================
echo.
echo Database: 1
echo User: postgres
echo Password: 1
echo Host: localhost
echo Port: 5432
echo.
echo You can now run: python manage.py runserver
echo.
pause
