import subprocess
import sys
import os
import time
import signal
from threading import Thread

backend_process = None
frontend_process = None

def run_backend():
    global backend_process
    print("🔧 Starting Backend Service with MongoDB Atlas...")
    
    import subprocess
import os
import time
import signal
import sys
from pathlib import Path

# Load environment variables from .env file
def load_env():
    env_file = Path(__file__).parent / "backend" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Set up environment
load_env()

# Check if MongoDB URL is configured
if not os.environ.get("MONGODB_URL") or "YOUR_USERNAME" in os.environ.get("MONGODB_URL", ""):
    print("❌ MongoDB connection chưa được cấu hình!")
    print("Vui lòng cập nhật MONGODB_URL trong file services/patient-service/backend/.env")
    sys.exit(1)
    
    os.chdir("backend")
    
    # Use Python from virtual environment if it exists
    python_path = "venv/bin/python3" if os.path.exists("venv/bin/python3") else sys.executable
    
    backend_process = subprocess.Popen([
        python_path, "-m", "uvicorn", "main:app", "--reload", "--port", "8001"
    ])
    os.chdir("..")

def run_frontend():
    global frontend_process
    print("📱 Starting Frontend Service...")
    
    # Wait for backend to start
    time.sleep(3)
    
    # Set environment variable
    os.environ['PATIENT_SERVICE_URL'] = 'http://127.0.0.1:8001'
    
    os.chdir("frontend")
    frontend_process = subprocess.Popen([sys.executable, "app.py"])
    os.chdir("..")

def signal_handler(sig, frame):
    print("\n🛑 Stopping services...")
    if backend_process:
        backend_process.terminate()
    if frontend_process:
        frontend_process.terminate()
    sys.exit(0)

def main():
    print("🏥 Starting Hospital Patient Management System...")
    print("📡 Backend: http://127.0.0.1:8001")
    print("🌐 Frontend: http://127.0.0.1:5000")
    print("📚 API Docs: http://127.0.0.1:8001/docs")
    print("⏹️  Press Ctrl+C to stop all services")
    print("=" * 60)
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start backend in thread
    backend_thread = Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Start frontend in thread
    frontend_thread = Thread(target=run_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()




# python3 -m venv .venv
# source .venv/bin/activate

# cd backend
# pip install --upgrade pip setuptools wheel
# pip install -r requirements.txt