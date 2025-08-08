import subprocess
import sys
import os

def run_backend():
    print("🔧 Starting Backend Service with MongoDB Atlas...")
    print("📡 Backend will run at: http://localhost:8001")
    print("📚 API Docs at: http://localhost:8001/docs")
    print("☁️ Using MongoDB Atlas: mongodb+srv://...@khoinnguyen.zyjxbda.mongodb.net/")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    # Set MongoDB URL environment variable
    import subprocess
import os
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
    exit(1)
    
    os.chdir("backend")
    subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8001"])

if __name__ == "__main__":
    run_backend()