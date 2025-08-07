import subprocess
import sys
import os

def run_backend():
    print("🔧 Starting Backend Service...")
    print("📡 Backend will run at: http://localhost:8001")
    print("📚 API Docs at: http://localhost:8001/docs")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    os.chdir("backend")
    subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8001"])

if __name__ == "__main__":
    run_backend()