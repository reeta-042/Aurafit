#!/usr/bin/env python3
"""
AuraFit Interactive Setup Wizard
Guides users through initial configuration
"""

import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    """Print welcome banner"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           🚨 AURAFIT - Emergency Response AI 🚨          ║
    ║                                                           ║
    ║              Interactive Setup Wizard                    ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

def check_python():
    """Verify Python version"""
    print("✓ Checking Python version...")
    if sys.version_info < (3, 10):
        print(f"✗ Python 3.10+ required (found {sys.version_info.major}.{sys.version_info.minor})")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} found")
    return True

def create_venv():
    """Create virtual environment"""
    print("\n✓ Setting up virtual environment...")
    
    venv_path = "venv"
    if os.path.exists(venv_path):
        response = input("  Virtual environment exists. Use existing? (y/n): ").lower()
        if response != 'y':
            print("  Removing old venv...")
            import shutil
            shutil.rmtree(venv_path)
    
    if not os.path.exists(venv_path):
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        print(f"✓ Created {venv_path}/")
    return True

def install_deps():
    """Install dependencies"""
    print("\n✓ Installing dependencies...")
    
    # Get pip path based on OS
    if sys.platform == "win32":
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
    
    # Install requirements
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
    print("✓ Dependencies installed")
    return True

def setup_env():
    """Setup environment file"""
    print("\n✓ Configuring environment...")
    
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"  Found existing {env_file}")
        response = input("  Reconfigure? (y/n): ").lower()
        if response != 'y':
            return True
    
    print("\n  Get your API key from: https://ai.google.dev")
    print("  1. Click 'Get API Key'")
    print("  2. Create new project (or select existing)")
    print("  3. Copy the API key\n")
    
    api_key = input("  Enter your GOOGLE_API_KEY (or press Enter to skip): ").strip()
    
    if api_key:
        with open(env_file, 'w') as f:
            f.write(f"GOOGLE_API_KEY={api_key}\n")
            f.write("GEMMA_MODEL=gemma-4-26b-a4b-it\n")
            f.write("LOG_LEVEL=INFO\n")
        print(f"✓ Configuration saved to {env_file}")
        return True
    else:
        print("⚠ Skipped API key setup. Update .env file later.")
        return True

def test_setup():
    """Run basic tests"""
    print("\n✓ Testing setup...")
    
    try:
        result = subprocess.run(
            [sys.executable, "test_suite.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if "FAIL" in result.stdout:
            print("⚠ Some tests failed (expected if no API key)")
        elif "PASS" in result.stdout:
            print("✓ Tests passed!")
        
        return True
    except Exception as e:
        print(f"⚠ Test failed: {e}")
        return True  # Don't block setup

def main():
    """Main setup flow"""
    print_banner()
    
    # Checks
    if not check_python():
        print("\n✗ Setup failed")
        return False
    
    # Setup steps
    if not create_venv():
        return False
    
    if not install_deps():
        return False
    
    if not setup_env():
        return False
    
    if not test_setup():
        return False
    
    # Success message
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                   ✓ SETUP COMPLETE                        ║
    ╚═══════════════════════════════════════════════════════════╝
    
    🎯 Next Steps:
    
    1. Activate virtual environment:
    """)
    
    if sys.platform == "win32":
        print("       venv\\Scripts\\activate")
    else:
        print("       source venv/bin/activate")
    
    print("""
    2. Start Victim Interface (Terminal 1):
       streamlit run victim_interface.py
    
    3. Start Responder Dashboard (Terminal 2):
       streamlit run responder_dashboard.py
    
    4. Open in browser:
       Victim Interface:   http://localhost:8501
       Responder Dashboard: http://localhost:8502
    
    📚 Documentation:
       - Quick Start:  QUICKSTART.md
       - Full Docs:    README.md
       - Deployment:   DEPLOYMENT.md
    
    🚨 Emergency? Submit a report through the Victim Interface!
    """)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
