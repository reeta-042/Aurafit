"""
AuraFit Initialization Script
Sets up the project and validates dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Verify Python 3.10+"""
    if sys.version_info < (3, 10):
        print(f"❌ Python 3.10+ required (found {sys.version_info.major}.{sys.version_info.minor})")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

def create_directories():
    """Create required directories"""
    dirs = ["data", "logs", "src", "src/core", "src/utils", "src/ui"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print(f"✅ Created {len(dirs)} directories")

def check_dependencies():
    """Check if dependencies are installed"""
    required = [
        "streamlit",
        "google-genai",
        "pillow",
        "pandas",
        "plotly",
        "pyttsx3",
        "SpeechRecognition",
        "pydantic"
    ]
    
    missing = []
    for pkg in required:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print(f"   Run: pip install -r requirements.txt")
        return False
    
    print(f"✅ All {len(required)} dependencies installed")
    return True

def setup_env():
    """Setup environment file"""
    env_file = ".env"
    example_file = ".env.example"
    
    if os.path.exists(env_file):
        print(f"✅ .env file exists")
    elif os.path.exists(example_file):
        print(f"⚠️ .env not found. Copy .env.example and add your GOOGLE_API_KEY")
    else:
        print(f"⚠️ Create .env with GOOGLE_API_KEY={your_key}")

def main():
    print("=" * 50)
    print("🚀 AURAFIT SETUP")
    print("=" * 50)
    print()
    
    check_python_version()
    create_directories()
    setup_env()
    
    if not check_dependencies():
        print("\n❌ Setup incomplete. Install dependencies and try again.")
        return False
    
    print("\n" + "=" * 50)
    print("✅ SETUP COMPLETE")
    print("=" * 50)
    print("\n🎯 Next steps:")
    print("   1. Copy .env.example → .env")
    print("   2. Add your GOOGLE_API_KEY to .env")
    print("   3. Run: streamlit run victim_interface.py")
    print("   4. In another terminal: streamlit run responder_dashboard.py")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
