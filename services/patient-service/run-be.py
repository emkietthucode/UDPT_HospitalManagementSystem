import os
import sys
import subprocess
from pathlib import Path


def load_env_from_file():
    env_file = Path(__file__).parent / "backend" / ".env"
    if env_file.exists():
        with open(env_file, encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value


def ensure_mongodb_url_default():
    # Đồng bộ với mặc định trong backend/main.py
    if not os.environ.get("MONGODB_URL"):
        os.environ["MONGODB_URL"] = "mongodb://localhost:27017/hospital_management"


def run_backend():
    print("🔧 Starting Patient Backend Service...")
    print("📡 http://localhost:8001 | 📚 Docs: http://localhost:8001/docs")
    print("⏹️  Ctrl+C để dừng")
    print("-" * 50)

    # Load env and ensure defaults
    load_env_from_file()
    ensure_mongodb_url_default()

    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)

    # Chạy uvicorn
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--reload",
        "--port",
        "8001",
        "--host",
        "0.0.0.0",
    ]
    subprocess.run(cmd)


if __name__ == "__main__":
    run_backend()