@echo off
setlocal enabledelayedexpansion

:: Hospital Management System - Stop All Services Script for Windows
echo 🛑 Stopping Hospital Management Microservices System...
echo ====================================================

:: Function to kill processes on specific port
:kill_port
set port=%1
set service_name=%2
echo 🔄 Stopping %service_name% on port %port%...

:: Find and kill processes using the port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%port% " 2^>nul') do (
    if not "%%a"=="0" (
        taskkill /F /PID %%a >nul 2>&1
        if !errorlevel! equ 0 (
            echo ✅ Stopped process PID %%a on port %port%
        )
    )
)

:: Also kill windows started with titles
taskkill /F /FI "WINDOWTITLE eq Insurance Service" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Patient Service" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Frontend Service" >nul 2>&1

:: Also kill any python.exe that is running our scripts
for /f "tokens=2 delims==" %%p in ('wmic process where "name='python.exe'" get CommandLine /value ^| findstr /i "main.py app.py"') do (
    for /f "tokens=2" %%q in ('wmic process where "CommandLine like '%%%p%' and name='python.exe'" get ProcessId /value ^| findstr "ProcessId"') do (
        set pid=%%q
        set pid=!pid:ProcessId=!
        taskkill /F /PID !pid! >nul 2>&1
    )
)

exit /b 0

:: Stop all services
call :kill_port 8002 "Insurance Service"
call :kill_port 8001 "Patient Service" 
call :kill_port 5001 "Frontend Service"

:: Wait a moment for processes to stop
timeout /t 2 >nul

echo.
echo 🔍 Verifying services are stopped...

:: Check if ports are free
netstat -an | findstr ":8002 " >nul 2>&1
if %errorlevel% neq 0 (
    echo ✅ Insurance Service (Port 8002) - STOPPED
) else (
    echo ⚠️  Insurance Service (Port 8002) - Still running
)

netstat -an | findstr ":8001 " >nul 2>&1
if %errorlevel% neq 0 (
    echo ✅ Patient Service (Port 8001) - STOPPED
) else (
    echo ⚠️  Patient Service (Port 8001) - Still running
)

netstat -an | findstr ":5001 " >nul 2>&1
if %errorlevel% neq 0 (
    echo ✅ Frontend Service (Port 5001) - STOPPED
) else (
    echo ⚠️  Frontend Service (Port 5001) - Still running
)

echo.
echo 🎉 Hospital Management Microservices stopped.
echo =====================================
echo.
echo 💡 To start all services again, run: start-all-services.bat

pause