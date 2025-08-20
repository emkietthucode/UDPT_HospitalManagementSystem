@echo off
setlocal

echo 🚀 Starting Patient Service MongoDB on Docker (Windows)...

:: Check Docker
docker info >nul 2>&1
if %errorlevel% neq 0 (
  echo ❌ Docker is not running. Please start Docker Desktop first.
  pause
  exit /b 1
)

cd /d "%~dp0"

:: Stop existing containers
echo 🛑 Stopping existing containers...
docker compose down

:: Start MongoDB service only
echo 🐳 Starting MongoDB container...
docker compose up -d mongodb
if %errorlevel% neq 0 (
  echo ❌ Failed to start MongoDB container
  exit /b 1
)

echo ⏳ Waiting for MongoDB to be ready...
ping -n 8 127.0.0.1 >nul

echo ✅ MongoDB is (likely) ready. Connection string examples:
echo   mongodb://admin:password123@localhost:27017/hospital_management?authSource=admin

echo Done.
pause