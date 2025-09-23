#!/usr/bin/env python3
"""
Installation script for Social Media Poster package.

This script helps users install and set up the Social Media Poster package.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_package():
    """Install the package."""
    print("🚀 Installing Social Media Poster...")
    
    if not check_python_version():
        return False
    
    # Install the package
    if not run_command("pip install -e .", "Installing package"):
        return False
    
    # Check if .env exists, if not copy from .env.example
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("📝 Created .env file from .env.example")
            print("⚠️  Please edit .env file with your API credentials")
        else:
            print("⚠️  No .env.example found. You'll need to create a .env file manually")
    else:
        print("✅ .env file already exists")
    
    # Create uploads directory
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    print("📁 Created uploads directory")
    
    print("\n🎉 Installation complete!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file with your social media API credentials")
    print("2. Run: python -m socmed_poster")
    print("3. Open http://localhost:5000 in your browser")
    
    return True

if __name__ == "__main__":
    success = install_package()
    sys.exit(0 if success else 1)