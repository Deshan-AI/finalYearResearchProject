# run.py
import subprocess
import sys
import os

def run_week2():
    """Start the web application"""
    print("=" * 60)
    print("Starting Student Burnout Detection System - Week 2")
    print("=" * 60)
    
    # Check if requirements are installed
    try:
        import fastapi
        print("✅ FastAPI installed")
    except ImportError:
        print("Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements2.txt"])
    
    # Run the application
    print("\n🚀 Starting web server...")
    print("📱 Access the application at: http://localhost:8000")
    print("📊 API documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop\n")
    
    subprocess.run([sys.executable, "-m", "uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])

if __name__ == "__main__":
    run_week2()