# Requires -Version 5.1
param(
	[switch]$Force
)

Write-Host "🏥 Starting Hospital Management Microservices System (Windows)" -ForegroundColor Cyan

function Ensure-Docker {
	try {
		$null = docker info 2>$null
		return $true
	} catch {
		Write-Host "❌ Docker Desktop chưa chạy. Vui lòng mở Docker Desktop rồi thử lại." -ForegroundColor Red
		return $false
	}
}

function Stop-PortProcess {
	param([int]$Port)
	try {
		$connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
		if ($connections) {
			$connections | ForEach-Object {
				try { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } catch {}
			}
			Write-Host "Stopped processes on port $Port" -ForegroundColor Yellow
		} else {
			Write-Host "Port $Port is free" -ForegroundColor Green
		}
	} catch {}
}

function Ensure-MongoDB {
	# Khởi động MongoDB bằng Docker Compose nếu chưa chạy
	$composeDir = Join-Path $root "services\patient-service"

	# Nếu dùng MongoDB Atlas (mongodb+srv) hoặc không trỏ localhost thì bỏ qua
	$mongoUrl = $env:MONGODB_URL
	if ($mongoUrl -and ($mongoUrl -like "mongodb+srv*" -or $mongoUrl -notlike "*localhost*" -and $mongoUrl -notlike "*127.0.0.1*")) {
		Write-Host "⏭️  Bỏ qua khởi động MongoDB local (đang dùng remote: $mongoUrl)." -ForegroundColor Yellow
		return
	}

	if (-not (Ensure-Docker)) { return }
	Write-Host "\n🐳 Kiểm tra và khởi động MongoDB (Docker) ..." -ForegroundColor Cyan
	try {
		Push-Location $composeDir
		# Dừng các container cũ (mongodb) nếu cần
		& docker compose up -d mongodb | Out-Null
		Pop-Location
		Write-Host "  ↳ MongoDB container đã được khởi động (nếu chưa chạy)." -ForegroundColor DarkGray
	} catch {
		Write-Host "⚠️ Không thể khởi động MongoDB bằng Docker Compose: $($_.Exception.Message)" -ForegroundColor Yellow
	}

	# Đợi cổng 27017 sẵn sàng
	for ($i=1; $i -le 15; $i++) {
		try {
			$tcp = Test-NetConnection -ComputerName "localhost" -Port 27017 -WarningAction SilentlyContinue
			if ($tcp.TcpTestSucceeded) {
				Write-Host "✅ MongoDB (27017) sẵn sàng." -ForegroundColor Green
				return
			}
		} catch {}
		Start-Sleep -Seconds 1
	}
	Write-Host "⚠️ MongoDB có thể chưa sẵn sàng, tiếp tục khởi động services (các service sẽ retry)." -ForegroundColor Yellow
}

function Ensure-Requirements {
	param([string]$ServiceDir)
	$req = Join-Path $ServiceDir "requirements.txt"
	if (Test-Path $req) {
		$python = Get-PythonPath -ServiceDir $ServiceDir
		Write-Host "Installing requirements for $ServiceDir ..." -ForegroundColor DarkCyan
		Start-Process -FilePath $python -ArgumentList @("-m","pip","install","-r","$req") -Wait -NoNewWindow
	}
}

function Get-PythonPath {
	param([string]$ServiceDir)
	$venvWin = Join-Path $ServiceDir "venv\Scripts\python.exe"
	$venvPy = Join-Path $ServiceDir "backend\venv\Scripts\python.exe"
	if (Test-Path $venvWin) { return $venvWin }
	if (Test-Path $venvPy) { return $venvPy }
	if (Get-Command py -ErrorAction SilentlyContinue) { return "py" }
	return "python"
}

function Start-UvicornService {
	param(
		[string]$Name,
		[string]$WorkingDir,
		[int]$Port
	)
	Write-Host "`n🚀 Starting $Name on port $Port..." -ForegroundColor Magenta
	$python = Get-PythonPath -ServiceDir $WorkingDir
	$logDir = Join-Path $WorkingDir "logs"
	if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
	$outLog = Join-Path $logDir "${Name.Replace(' ','-').ToLower()}-out.log"
	$errLog = Join-Path $logDir "${Name.Replace(' ','-').ToLower()}-err.log"
	$args = @("-m","uvicorn","main:app","--host","0.0.0.0","--port","$Port")
	Start-Process -FilePath $python -ArgumentList $args -WorkingDirectory $WorkingDir -WindowStyle Normal -RedirectStandardOutput $outLog -RedirectStandardError $errLog | Out-Null
	Write-Host "  ↳ Logs: $outLog | $errLog" -ForegroundColor DarkGray
}

function Start-Frontend {
	param([string]$WorkingDir,[int]$Port)
	Write-Host "`n🚀 Starting Frontend on port $Port..." -ForegroundColor Magenta
	$python = Get-PythonPath -ServiceDir $WorkingDir
	$logDir = Join-Path $WorkingDir "logs"
	if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
	$outLog = Join-Path $logDir "frontend-out.log"
	$errLog = Join-Path $logDir "frontend-err.log"
	$args = @("app.py")
	Start-Process -FilePath $python -ArgumentList $args -WorkingDirectory $WorkingDir -WindowStyle Normal -RedirectStandardOutput $outLog -RedirectStandardError $errLog | Out-Null
	Write-Host "  ↳ Logs: $outLog | $errLog" -ForegroundColor DarkGray
}

function Wait-Health {
	param([string]$Url,[int]$Retries=20)
	for ($i=1; $i -le $Retries; $i++) {
		try {
			$resp = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 3
			if ($resp.StatusCode -eq 200) { return $true }
		} catch {}
		Start-Sleep -Seconds 1
	}
	return $false
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Environment defaults (ưu tiên .env của từng service, KHÔNG ghi đè nếu đã có)
$insEnv = Join-Path $root "services\insurance-service\.env"
$patEnv = Join-Path $root "services\patient-service\backend\.env"

if (-not $env:MONGODB_URL) {
	if (-not (Test-Path $insEnv) -and -not (Test-Path $patEnv)) {
		$env:MONGODB_URL = "mongodb://admin:password123@localhost:27017/hospital_management?authSource=admin"
	}
}
if (-not $env:INSURANCE_SERVICE_URL) { $env:INSURANCE_SERVICE_URL = "http://127.0.0.1:8002" }
if (-not $env:PATIENT_SERVICE_URL) { $env:PATIENT_SERVICE_URL = "http://127.0.0.1:8001" }

Write-Host "MONGODB_URL=$($env:MONGODB_URL)" -ForegroundColor DarkGray
Write-Host "INSURANCE_SERVICE_URL=$($env:INSURANCE_SERVICE_URL)" -ForegroundColor DarkGray
Write-Host "PATIENT_SERVICE_URL=$($env:PATIENT_SERVICE_URL)" -ForegroundColor DarkGray

# Stop existing (only when -Force)
if ($Force) {
	Stop-PortProcess -Port 8001
	Stop-PortProcess -Port 8002
	Stop-PortProcess -Port 5001
} else {
	Write-Host "ℹ️  Not stopping existing processes automatically (use -Force to kill)." -ForegroundColor Yellow
}

# Start services
Ensure-MongoDB
Ensure-Requirements -ServiceDir (Join-Path $root "services\insurance-service")
if (-not (Get-NetTCPConnection -LocalPort 8002 -State Listen -ErrorAction SilentlyContinue)) {
	Start-UvicornService -Name "Insurance Service" -WorkingDir (Join-Path $root "services\insurance-service") -Port 8002
} else {
	Write-Host "❌ Skipping Insurance Service start because port 8002 is in use." -ForegroundColor Red
}
Start-Sleep -Seconds 2
Ensure-Requirements -ServiceDir (Join-Path $root "services\patient-service\backend")
if (-not (Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue)) {
	Start-UvicornService -Name "Patient Service" -WorkingDir (Join-Path $root "services\patient-service\backend") -Port 8001
} else {
	Write-Host "❌ Skipping Patient Service start because port 8001 is in use." -ForegroundColor Red
}
Start-Sleep -Seconds 2
if (-not (Get-NetTCPConnection -LocalPort 5001 -State Listen -ErrorAction SilentlyContinue)) {
	Start-Frontend -WorkingDir (Join-Path $root "services\patient-service\frontend") -Port 5001
} else {
	Write-Host "❌ Skipping Frontend start because port 5001 is in use." -ForegroundColor Red
}

Write-Host "`n🔍 Verifying services..." -ForegroundColor Yellow

if (Wait-Health -Url "http://localhost:8002/health") {
	Write-Host "✅ Insurance Service (8002) - RUNNING" -ForegroundColor Green
} else {
	Write-Host "❌ Insurance Service (8002) - NOT RESPONDING" -ForegroundColor Red
}

if (Wait-Health -Url "http://localhost:8001/health") {
	Write-Host "✅ Patient Service (8001) - RUNNING" -ForegroundColor Green
} else {
	Write-Host "❌ Patient Service (8001) - NOT RESPONDING" -ForegroundColor Red
}

try {
	$resp = Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:5001" -TimeoutSec 3
	if ($resp.StatusCode -eq 200) {
		Write-Host "✅ Frontend (5001) - RUNNING" -ForegroundColor Green
	} else {
		Write-Host "❌ Frontend (5001) - NOT RESPONDING" -ForegroundColor Red
	}
} catch {
	Write-Host "❌ Frontend (5001) - NOT RESPONDING" -ForegroundColor Red
}

Write-Host "`n🎉 Services started. Docs: http://localhost:8001/docs | http://localhost:8002/docs" -ForegroundColor Cyan

