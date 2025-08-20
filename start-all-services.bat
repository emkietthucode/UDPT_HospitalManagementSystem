@echo off
setlocal enabledelayedexpansion

:: Hospital Management System - Microservices Startup Script for Windows
echo 🏥 Starting Hospital Management Microservices System...
echo ==================================================

:: Skip function definitions and go to main logic
goto :main

:: Function to check if port is available
:check_port
set port=%1
netstat -an | findstr ":%port% " >nul 2>&1
if %errorlevel% equ 0 (
    echo ❌ Port %port% is already in use
    exit /b 1
) else (
    echo ✅ Port %port% is available  
    exit /b 0
)

:: Function to kill processes on specific port
:kill_port
set port=%1
echo 🔄 Stopping processes on port %port%...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%port% "') do (
    taskkill /F /PID %%a >nul 2>&1
)
exit /b 0

:main
:: Stop existing processes on target ports
echo 🔄 Stopping existing services...
call :kill_port 8001
call :kill_port 8002  
call :kill_port 5001
timeout /t 2 >nul

:: Check port availability
echo.
echo 🔍 Checking port availability...
call :check_port 8001
call :check_port 8002
call :check_port 5001

:: Set base directory (current directory)
set BASE_DIR=%CD%

:: Start Insurance Service (Port 8002)
echo.
echo 🚀 Starting Insurance Service on port 8002...
cd "%BASE_DIR%\services\insurance-service"

if exist "venv\Scripts\python.exe" (
    start "Insurance Service" /min cmd /c "venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8002"
    echo Started Insurance Service
) else (
    echo ❌ Virtual environment not found for Insurance Service
    echo Please run quick-setup.bat first
    pause
    exit /b 1
)

:: Wait a bit before starting next service
timeout /t 5 >nul

:: Start Patient Service (Port 8001)
echo.
echo 🚀 Starting Patient Service on port 8001...
cd "%BASE_DIR%\services\patient-service\backend"

if exist "venv\Scripts\python.exe" (
    start "Patient Service" /min cmd /c "venv\Scripts\python.exe main.py"
    echo Started Patient Service
) else (
    echo ❌ Virtual environment not found for Patient Service
    echo Please run quick-setup.bat first
    pause
    exit /b 1
)

:: Wait a bit before starting frontend
timeout /t 5 >nul

:: Start Frontend Service (Port 5001)
echo.
echo 🚀 Starting Frontend Service on port 5001...
cd "%BASE_DIR%\services\patient-service\frontend"

if exist "venv\Scripts\python.exe" (
    start "Frontend Service" /min cmd /c "venv\Scripts\python.exe app.py"
    echo Started Frontend Service
) else (
    echo ❌ Virtual environment not found for Frontend Service
    echo Please run quick-setup.bat first
    pause
    exit /b 1
)

:: Wait for services to start
echo.
echo ⏳ Waiting for services to start...
timeout /t 30 >nul

:: Verify all services
echo.
echo 🔍 Verifying services...

:: Check Insurance Service
curl -s http://127.0.0.1:8002/health >nul 2>&1 && echo Insurance Service - Port 8002 - RUNNING || echo Insurance Service - Port 8002 - NOT RESPONDING

:: Check Patient Service  
curl -s http://localhost:8001/health >nul 2>&1 && echo Patient Service - Port 8001 - RUNNING || echo Patient Service - Port 8001 - NOT RESPONDING

:: Check Frontend Service
curl -s http://localhost:5001 >nul 2>&1 && echo Frontend Service - Port 5001 - RUNNING || echo Frontend Service - Port 5001 - NOT RESPONDING

echo.
echo 🎉 Hospital Management System Started!
echo ==================================================
echo 📊 Service URLs:
echo • Insurance Service API: http://localhost:8002/docs
echo • Patient Service API:   http://localhost:8001/docs
echo • Web Application:       http://localhost:5001
echo.
echo 💾 Databases:
echo • Insurance Service:     insurance_service_db (MongoDB)
echo • Patient Service:       hospital_management (MongoDB)
echo.
echo 💡 To stop all services, run: stop-all-services.bat
echo Or close the service windows manually

echo.
echo ℹ️ Nếu Insurance/Patient NOT RESPONDING, hãy đảm bảo MongoDB đang chạy và .env dùng URL local:
echo    MONGODB_URL=mongodb://admin:password123@localhost:27017/<db>?authSource=admin

:: Return to original directory
cd "%BASE_DIR%"

pause