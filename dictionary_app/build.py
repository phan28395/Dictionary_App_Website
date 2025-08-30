#!/usr/bin/env python3
"""
Build script for Dictionary App
Creates platform-specific executables and installers
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
import zipfile
import json

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKCYAN}→ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

class DictionaryAppBuilder:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.build_dir = self.root_dir / 'build'
        self.dist_dir = self.root_dir / 'dist'
        self.release_dir = self.root_dir / 'releases'
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.version = self.get_version()
        
    def get_version(self):
        """Get app version from config."""
        config_path = self.root_dir / 'config' / 'default_config.json'
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                return config.get('app', {}).get('version', '1.0.0')
        return '1.0.0'
        
    def clean_build_dirs(self):
        """Clean previous build artifacts."""
        print_info("Cleaning previous build artifacts...")
        
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print_success(f"Removed {dir_path}")
                
        # Create release directory if it doesn't exist
        self.release_dir.mkdir(exist_ok=True)
        
    def install_dependencies(self):
        """Install build dependencies."""
        print_info("Installing build dependencies...")
        
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements-build.txt'
            ], check=True)
            print_success("Build dependencies installed")
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install dependencies: {e}")
            return False
            
        return True
        
    def build_executable(self):
        """Build the executable using PyInstaller."""
        print_info(f"Building executable for {self.system} ({self.arch})...")
        
        try:
            # Run PyInstaller
            subprocess.run([
                sys.executable, '-m', 'PyInstaller',
                'dictionary_app.spec',
                '--clean',
                '--noconfirm'
            ], check=True)
            
            print_success("Executable built successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print_error(f"Build failed: {e}")
            return False
            
    def create_portable_zip(self):
        """Create a portable ZIP archive."""
        print_info("Creating portable ZIP archive...")
        
        # Determine executable name based on platform
        if self.system == 'windows':
            exe_name = 'DictionaryApp.exe'
        elif self.system == 'darwin':
            exe_name = 'DictionaryApp.app'
        else:
            exe_name = 'DictionaryApp'
            
        exe_path = self.dist_dir / exe_name
        
        if not exe_path.exists():
            print_error(f"Executable not found: {exe_path}")
            return False
            
        # Create ZIP filename
        zip_name = f"DictionaryApp-{self.version}-{self.system}-{self.arch}-portable.zip"
        zip_path = self.release_dir / zip_name
        
        # Create ZIP archive
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if exe_path.is_file():
                zipf.write(exe_path, exe_name)
            else:
                # For app bundles (macOS)
                for root, dirs, files in os.walk(exe_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.dist_dir)
                        zipf.write(file_path, arcname)
                        
            # Add README
            readme_content = f"""Dictionary App v{self.version}
=========================

A powerful dictionary application with plugin support.

How to Run:
-----------
1. Extract this ZIP file to any location
2. Run {exe_name}
3. The app will start with a system tray icon

First Time Setup:
-----------------
- The app includes 50 free searches
- Upgrade to premium for unlimited searches
- All data is stored locally for privacy

Support:
--------
GitHub: https://github.com/yourusername/dictionary-app
Email: support@dictionaryapp.com
"""
            zipf.writestr('README.txt', readme_content)
            
        print_success(f"Created portable archive: {zip_path}")
        return True
        
    def create_installer(self):
        """Create platform-specific installer."""
        print_info(f"Creating installer for {self.system}...")
        
        if self.system == 'windows':
            return self.create_windows_installer()
        elif self.system == 'darwin':
            return self.create_macos_dmg()
        else:
            return self.create_linux_package()
            
    def create_windows_installer(self):
        """Create Windows installer using NSIS (if available)."""
        print_warning("Windows installer creation requires NSIS")
        print_info("Please install NSIS from: https://nsis.sourceforge.io/")
        
        # Create a basic NSIS script
        nsis_script = self.root_dir / 'installer.nsi'
        with open(nsis_script, 'w') as f:
            f.write(f"""
; Dictionary App NSIS Installer Script
!define PRODUCT_NAME "Dictionary App"
!define PRODUCT_VERSION "{self.version}"
!define PRODUCT_PUBLISHER "Dictionary App Team"

Name "${{PRODUCT_NAME}} ${{PRODUCT_VERSION}}"
OutFile "releases/DictionaryApp-${{PRODUCT_VERSION}}-setup.exe"
InstallDir "$PROGRAMFILES64\\DictionaryApp"
RequestExecutionLevel admin

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  File "dist\\DictionaryApp.exe"
  CreateShortcut "$DESKTOP\\Dictionary App.lnk" "$INSTDIR\\DictionaryApp.exe"
  CreateShortcut "$SMPROGRAMS\\Dictionary App.lnk" "$INSTDIR\\DictionaryApp.exe"
SectionEnd
""")
        
        print_success(f"Created NSIS script: {nsis_script}")
        print_info("Run 'makensis installer.nsi' to build installer")
        return True
        
    def create_macos_dmg(self):
        """Create macOS DMG installer."""
        print_warning("DMG creation requires macOS developer tools")
        
        # Basic DMG creation would go here
        print_info("Use 'hdiutil' or 'create-dmg' to create DMG")
        return True
        
    def create_linux_package(self):
        """Create Linux AppImage."""
        print_info("Creating Linux AppImage...")
        
        # Create AppImage directory structure
        appimage_dir = self.build_dir / 'AppDir'
        appimage_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy executable
        exe_src = self.dist_dir / 'DictionaryApp'
        exe_dst = appimage_dir / 'usr' / 'bin' / 'DictionaryApp'
        exe_dst.parent.mkdir(parents=True, exist_ok=True)
        
        if exe_src.exists():
            shutil.copy2(exe_src, exe_dst)
            exe_dst.chmod(0o755)
            
        # Create desktop entry
        desktop_entry = appimage_dir / 'DictionaryApp.desktop'
        with open(desktop_entry, 'w') as f:
            f.write(f"""[Desktop Entry]
Name=Dictionary App
Exec=DictionaryApp
Icon=dictionary-app
Type=Application
Categories=Education;Office;
Comment=Powerful dictionary with plugin support
Version={self.version}
""")
        
        # Create AppRun script
        apprun = appimage_dir / 'AppRun'
        with open(apprun, 'w') as f:
            f.write("""#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/usr/bin/DictionaryApp" "$@"
""")
        apprun.chmod(0o755)
        
        print_success("AppImage structure created")
        print_info("Use 'appimagetool' to build the AppImage")
        return True
        
    def run_tests(self):
        """Run basic smoke tests on the built executable."""
        print_info("Running smoke tests...")
        
        # Check if executable exists
        if self.system == 'windows':
            exe_path = self.dist_dir / 'DictionaryApp.exe'
        else:
            exe_path = self.dist_dir / 'DictionaryApp'
            
        if not exe_path.exists():
            print_error("Executable not found")
            return False
            
        print_success("Executable found")
        
        # Could add more tests here
        # For example, running with --version flag
        
        return True
        
    def build(self):
        """Main build process."""
        print_header(f"Building Dictionary App v{self.version}")
        
        # Step 1: Clean
        self.clean_build_dirs()
        
        # Step 2: Install dependencies
        if not self.install_dependencies():
            print_error("Build failed: Could not install dependencies")
            return False
            
        # Step 3: Build executable
        if not self.build_executable():
            print_error("Build failed: Could not create executable")
            return False
            
        # Step 4: Run tests
        if not self.run_tests():
            print_warning("Tests failed, but build completed")
            
        # Step 5: Create portable ZIP
        self.create_portable_zip()
        
        # Step 6: Create installer (platform-specific)
        self.create_installer()
        
        print_header("Build Complete!")
        print_success(f"Executable location: {self.dist_dir}")
        print_success(f"Release packages: {self.release_dir}")
        
        return True

def main():
    """Main entry point."""
    builder = DictionaryAppBuilder()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'clean':
            builder.clean_build_dirs()
        elif command == 'test':
            builder.run_tests()
        elif command == 'portable':
            builder.create_portable_zip()
        elif command == 'installer':
            builder.create_installer()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python build.py [clean|test|portable|installer]")
            sys.exit(1)
    else:
        # Run full build
        success = builder.build()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()