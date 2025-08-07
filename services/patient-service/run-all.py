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
    
    # Set MongoDB environment variable
    os.environ["MONGODB_URL"] = "mongodb+srv://khoinguyen:UZXmjbTrfApU7gs5@khoinnguyen.zyjxbda.mongodb.net/hospital_management"
    
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