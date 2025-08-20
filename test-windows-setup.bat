@echo off
setlocal enabledelayedexpansion

:: Test script for Windows Hospital Management System setup
echo 🧪 Testing Windows Hospital Management System Setup
echo ==================================================

:: Test 1: Check Python installation
echo.
echo 1️⃣  Testing Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python is available
    python --version
) else (
    echo ❌ Python not found - please install Python 3.9+
    goto :end
)

:: Test 2: Check directory structure
echo.
echo 2️⃣  Testing directory structure...
if exist "services\insurance-service" (
    echo ✅ Insurance service directory exists
) else (
    echo ❌ Insurance service directory missing
)

if exist "services\patient-service\backend" (
    echo ✅ Patient service backend directory exists
) else (
    echo ❌ Patient service backend directory missing
)

if exist "services\patient-service\frontend" (
    echo ✅ Patient service frontend directory exists
) else (
    echo ❌ Patient service frontend directory missing
)

:: Test 3: Check batch files
echo.
echo 3️⃣  Testing batch files existence...
if exist "quick-setup.bat" (
    echo ✅ quick-setup.bat exists
) else (
    echo ❌ quick-setup.bat missing
)

if exist "start-all-services.bat" (
    echo ✅ start-all-services.bat exists
) else (
    echo ❌ start-all-services.bat missing
)

if exist "stop-all-services.bat" (
    echo ✅ stop-all-services.bat exists
) else (
    echo ❌ stop-all-services.bat missing
)

:: Test 4: Check network connectivity (curl)
echo.
echo 4️⃣  Testing network tools...
curl --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ curl is available for service testing
) else (
    echo ⚠️  curl not found - service verification might not work
    echo    You can install curl or use browser to test services
)

:: Test 5: Check port availability
echo.
echo 5️⃣  Testing port availability...
netstat -an | findstr ":8001 " >nul 2>&1
if %errorlevel% neq 0 (
    echo ✅ Port 8001 is available
) else (
    echo ⚠️  Port 8001 is in use
)

netstat -an | findstr ":8002 " >nul 2>&1
if %errorlevel% neq 0 (
    echo ✅ Port 8002 is available
) else (
    echo ⚠️  Port 8002 is in use
)

netstat -an | findstr ":5001 " >nul 2>&1
if %errorlevel% neq 0 (
    echo ✅ Port 5001 is available
) else (
    echo ⚠️  Port 5001 is in use
)

:end
echo.
echo 🎯 Test completed!
echo.
echo 📋 Next steps:
echo    1. Run quick-setup.bat to install dependencies
echo    2. Update MongoDB connection strings in .env files
echo    3. Run start-all-services.bat to start the system
echo    4. Run stop-all-services.bat to stop the system

pause