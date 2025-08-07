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
    os.environ["MONGODB_URL"] = "mongodb+srv://khoinguyen:UZXmjbTrfApU7gs5@khoinnguyen.zyjxbda.mongodb.net/hospital_management"
    
    os.chdir("backend")
    subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8001"])

if __name__ == "__main__":
    run_backend()