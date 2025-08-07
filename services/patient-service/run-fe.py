import subprocess
import sys
import os

def run_frontend():
    print("📱 Starting Frontend Service...")
    print("🌐 Frontend will run at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    # Set environment variable
    os.environ['PATIENT_SERVICE_URL'] = 'http://localhost:8001'
    
    os.chdir("frontend")
    subprocess.run([sys.executable, "app.py"])

if __name__ == "__main__":
    run_frontend()