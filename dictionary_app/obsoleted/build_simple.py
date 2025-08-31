#!/usr/bin/env python3
"""
Simple build script for Dictionary App
Creates a standalone directory with all files needed to run
"""

import os
import shutil
import subprocess
from pathlib import Path

def build_standalone():
    """Create a standalone directory with all necessary files."""
    
    print("Building Dictionary App standalone package...")
    
    # Create dist directory
    dist_dir = Path("dist/DictionaryApp")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True)
    
    # Files and directories to copy
    items_to_copy = [
        "run_app.py",
        "core",
        "plugins", 
        "data",
        "config",
        "requirements.txt",
        ".env.example"
    ]
    
    # Copy all necessary files
    for item in items_to_copy:
        src = Path(item)
        if src.exists():
            dst = dist_dir / item
            if src.is_dir():
                shutil.copytree(src, dst)
                print(f"  ✓ Copied directory: {item}")
            else:
                shutil.copy2(src, dst)
                print(f"  ✓ Copied file: {item}")
    
    # Create a launcher script
    launcher_script = dist_dir / "DictionaryApp.sh"
    with open(launcher_script, "w") as f:
        f.write("""#!/bin/bash
# Dictionary App Launcher

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$DIR/venv"
    
    echo "Installing dependencies..."
    "$DIR/venv/bin/pip" install -q -r "$DIR/requirements.txt"
fi

# Activate virtual environment and run app
echo "Starting Dictionary App..."
"$DIR/venv/bin/python" "$DIR/run_app.py"
""")
    
    launcher_script.chmod(0o755)
    print(f"  ✓ Created launcher: DictionaryApp.sh")
    
    # Create Windows batch launcher
    launcher_bat = dist_dir / "DictionaryApp.bat"
    with open(launcher_bat, "w") as f:
        f.write("""@echo off
REM Dictionary App Launcher for Windows

REM Get the directory where this script is located
set DIR=%~dp0

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 3 is required but not installed.
    echo Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "%DIR%venv" (
    echo Creating virtual environment...
    python -m venv "%DIR%venv"
    
    echo Installing dependencies...
    "%DIR%venv\\Scripts\\pip" install -q -r "%DIR%requirements.txt"
)

REM Run the app
echo Starting Dictionary App...
"%DIR%venv\\Scripts\\python" "%DIR%run_app.py"
pause
""")
    
    print(f"  ✓ Created launcher: DictionaryApp.bat")
    
    # Create README
    readme = dist_dir / "README.txt"
    with open(readme, "w") as f:
        f.write("""Dictionary App v1.0.0
=====================

Installation:
-------------
1. Make sure Python 3.8+ is installed on your system
2. Run the launcher for your platform:
   - Linux/Mac: ./DictionaryApp.sh
   - Windows: DictionaryApp.bat

The launcher will:
- Create a virtual environment (first run only)
- Install all dependencies (first run only)
- Start the Dictionary App

Features:
---------
- 50 free searches
- Premium upgrade for unlimited searches
- Plugin system for extensions
- Complete offline functionality
- Privacy-focused (all data stays local)

Troubleshooting:
----------------
If the app doesn't start:
1. Make sure Python 3.8+ is installed
2. Try running: python3 run_app.py
3. Check the console for error messages

Support:
--------
GitHub: https://github.com/yourusername/dictionary-app
""")
    
    print(f"  ✓ Created README.txt")
    
    # Create a ZIP archive
    print("\nCreating ZIP archive...")
    shutil.make_archive("dist/DictionaryApp-standalone", 'zip', "dist", "DictionaryApp")
    print(f"  ✓ Created: dist/DictionaryApp-standalone.zip")
    
    print("\n✅ Build complete!")
    print(f"   Standalone directory: {dist_dir}")
    print(f"   ZIP archive: dist/DictionaryApp-standalone.zip")
    print("\nTo run the app:")
    print(f"   cd {dist_dir}")
    print("   ./DictionaryApp.sh  (Linux/Mac)")
    print("   DictionaryApp.bat   (Windows)")

if __name__ == "__main__":
    build_standalone()