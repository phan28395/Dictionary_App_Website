#!/bin/bash
# Quick VM setup for Dictionary App testing
# Works on any Linux system

set -e

echo "🚀 Quick VM Setup for Dictionary App Testing"
echo "============================================"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ Don't run as root. Run as regular user."
   exit 1
fi

# Create testing directory
mkdir -p ~/vm-testing-dictionary-app
cd ~/vm-testing-dictionary-app

echo "📋 Choose your testing method:"
echo ""
echo "1) 🐳 Docker Windows Environment (Recommended - Works now)"
echo "2) 📦 Download VirtualBox + Windows VM" 
echo "3) 🌐 Online Testing Services"
echo "4) 📝 Manual Setup Instructions"
echo ""

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "🐳 Setting up Docker Windows environment..."
        
        # Check if Docker is running
        if ! docker info >/dev/null 2>&1; then
            echo "❌ Docker is not running. Please start Docker first."
            exit 1
        fi
        
        echo "✅ Docker is running"
        echo "📥 This will download Ubuntu + Wine + Python (~2GB)"
        read -p "Continue? (y/n): " confirm
        
        if [[ $confirm != "y" ]]; then
            echo "❌ Cancelled"
            exit 0
        fi
        
        # Create simple Dockerfile
        cat > Dockerfile << 'EOF'
FROM ubuntu:22.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    wget gnupg2 xvfb x11vnc fluxbox python3 python3-pip python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Install Wine
RUN dpkg --add-architecture i386 && \
    mkdir -pm755 /etc/apt/keyrings && \
    wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key && \
    echo "deb [arch=amd64,i386 signed-by=/etc/apt/keyrings/winehq-archive.key] https://dl.winehq.org/wine-builds/ubuntu jammy main" > /etc/apt/sources.list.d/winehq.list && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y winehq-stable && \
    rm -rf /var/lib/apt/lists/*

ENV DISPLAY=:0
ENV WINEPREFIX=/root/.wine

# Install Python in Wine
RUN wine wineboot --init && \
    wget -q https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe && \
    xvfb-run -a wine python-3.11.9-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 && \
    rm python-3.11.9-amd64.exe

WORKDIR /app
EXPOSE 5900

CMD ["bash", "-c", "Xvfb :0 -screen 0 1280x1024x24 & sleep 2 && fluxbox & sleep 1 && x11vnc -display :0 -nopw -forever -shared -bg && echo 'VNC ready on port 5900' && bash"]
EOF
        
        echo "🔨 Building Docker image (this may take 10-15 minutes)..."
        docker build -t dict-app-test .
        
        echo "🚀 Starting container..."
        docker run -d -p 5900:5900 --name dict-app-test-container dict-app-test
        
        echo "✅ Windows-like test environment ready!"
        echo ""
        echo "📱 To connect:"
        echo "   1. Install VNC viewer: sudo pacman -S tigervnc"
        echo "   2. Connect to: localhost:5900"
        echo "   3. Copy your app files to container:"
        echo "      docker cp /path/to/DictionaryApp dict-app-test-container:/app/"
        echo "   4. Test with: wine python run_app.py"
        
        ;;
        
    2)
        echo "📦 VirtualBox + Windows VM Setup"
        echo ""
        echo "Step 1: Install VirtualBox"
        echo "   - Download from: https://www.virtualbox.org/wiki/Downloads"
        echo "   - Or try: yay -S virtualbox"
        echo ""
        echo "Step 2: Download Windows VM"
        echo "   - Go to: https://developer.microsoft.com/en-us/windows/downloads/virtual-machines/"
        echo "   - Download 'Windows 10 development environment'"
        echo "   - Choose VirtualBox format"
        echo "   - File size: ~6GB"
        echo ""
        echo "Step 3: Import and Test"
        echo "   - Open VirtualBox"
        echo "   - File → Import Appliance → Select .ova file"
        echo "   - Start VM and copy your app folder"
        echo "   - Install Python 3.11 in Windows"
        echo "   - Run: python run_app.py"
        
        ;;
        
    3)
        echo "🌐 Online Testing Services"
        echo ""
        echo "Option A: GitHub Codespaces (Free tier available)"
        echo "   1. Push your code to GitHub"
        echo "   2. Open in Codespaces"
        echo "   3. Select Windows environment"
        echo "   4. Test your app"
        echo ""
        echo "Option B: BrowserStack (Paid)"
        echo "   - Real Windows/Mac devices"
        echo "   - Perfect for final testing"
        echo "   - https://www.browserstack.com"
        echo ""
        echo "Option C: Replit (Free)"
        echo "   - Upload your code"
        echo "   - Test Python functionality"
        echo "   - Limited GUI support"
        
        ;;
        
    4)
        echo "📝 Manual Setup Instructions"
        echo ""
        echo "For Windows Testing:"
        echo "   1. Get a Windows machine (friend's laptop, work computer, etc.)"
        echo "   2. Install Python 3.11+"
        echo "   3. Copy your DictionaryApp folder"
        echo "   4. Run: python -m pip install -r requirements.txt"
        echo "   5. Run: python -m pip install pynput pystray customtkinter pyperclip pillow"
        echo "   6. Test: python run_app.py"
        echo "   7. Try double-Ctrl hotkey"
        echo ""
        echo "For macOS Testing:"
        echo "   1. Get a Mac (legally required for macOS VMs)"
        echo "   2. Install Python 3.11+ (brew install python@3.11)"
        echo "   3. Same steps as Windows"
        echo "   4. Test Cmd+Cmd or Ctrl+Ctrl hotkeys"
        
        ;;
        
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎯 Testing Checklist:"
echo "   □ App starts without errors"
echo "   □ Double-Ctrl opens search window"
echo "   □ Search finds words in database"
echo "   □ System tray icon appears"  
echo "   □ Settings window opens"
echo "   □ Can search and get results"
echo ""
echo "📊 Report back with:"
echo "   - Which OS you tested on"
echo "   - What worked / didn't work"
echo "   - Any error messages"