#!/usr/bin/env python3
"""
Setup script for Coffee Shop Backend
"""
import os
import subprocess
import sys

def run_command(command, description):
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("="*50)
    print("Coffee Shop Backend Setup")
    print("="*50)
    
    # Check if Python is available
    if not run_command("python --version", "Checking Python version"):
        return
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        if run_command("python -m venv venv", "Creating virtual environment"):
            print("\nTo activate virtual environment:")
            print("  On macOS/Linux: source venv/bin/activate")
            print("  On Windows: venv\\Scripts\\activate")
    
    # Install dependencies
    if os.path.exists("requirements.txt"):
        run_command("pip install -r requirements.txt", "Installing dependencies")
    else:
        print("❌ requirements.txt not found!")
        return
    
    # Initialize database
    if os.path.exists("init_db.py"):
        run_command("python init_db.py", "Initializing database")
    else:
        print("❌ init_db.py not found!")
        return
    
    print("\n" + "="*50)
    print("Setup complete! 🎉")
    print("="*50)
    print("\nTo start the server:")
    print("1. Activate virtual environment:")
    print("   source venv/bin/activate (macOS/Linux)")
    print("   venv\\Scripts\\activate (Windows)")
    print("2. Run: uvicorn src.main:app --reload")
    print("\nAccess the API at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()