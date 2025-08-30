#!/bin/bash
# Quick VM setup script for Dictionary App testing

set -e

echo "🖥️  Dictionary App VM Testing Setup"
echo "=================================="

# Create testing directory
mkdir -p vm-testing
cd vm-testing

# Option 1: Download Windows 10 development VM (Free, 90 days)
download_windows_vm() {
    echo "📥 Downloading Windows 10 Development VM..."
    echo "   - Size: ~6GB"
    echo "   - Valid for 90 days"
    echo "   - Includes Visual Studio"
    
    # Microsoft provides free Windows VMs for developers
    wget -O "Win10_dev.ova" \
        "https://aka.ms/windev_VM_virtualbox" \
        || echo "⚠️  Download from: https://developer.microsoft.com/en-us/windows/downloads/virtual-machines/"
}

# Option 2: macOS setup (requires macOS host legally)
setup_macos_info() {
    echo "🍎 macOS VM Setup Information"
    echo "   - Legal only on Apple hardware"
    echo "   - Use macOS Monterey or newer"
    echo "   - Enable virtualization in System Preferences"
    echo "   - Use UTM, Parallels, or VMware Fusion"
}

# Option 3: Create test script
create_test_script() {
    cat > test-dictionary-app.sh << 'EOF'
#!/bin/bash
# Test script to run inside VMs

echo "🧪 Testing Dictionary App"
echo "========================"

# Check Python
python --version || python3 --version || echo "❌ Python not found"

# Test requirements
pip install -r requirements.txt || echo "⚠️  Some requirements failed"
pip install pynput pystray customtkinter pyperclip pillow || echo "⚠️  UI deps failed"

# Run app
echo "🚀 Starting Dictionary App..."
echo "   Try double-tapping Ctrl to test hotkeys"
python run_app.py || python3 run_app.py

echo "✅ Test complete!"
EOF
    chmod +x test-dictionary-app.sh
}

# Main menu
echo "Choose testing option:"
echo "1) Download Windows 10 Dev VM (Recommended)"
echo "2) Show macOS VM setup info"
echo "3) Create test scripts only"
echo "4) Use Docker Windows environment"

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        download_windows_vm
        create_test_script
        echo "✅ Windows VM download started"
        echo "   Import the .ova file into VirtualBox when complete"
        ;;
    2)
        setup_macos_info
        create_test_script
        ;;
    3)
        create_test_script
        echo "✅ Test script created: test-dictionary-app.sh"
        ;;
    4)
        echo "🐳 Using Docker Windows environment..."
        cd ..
        docker-compose -f docker-compose.vm-test.yml up -d windows-test
        echo "✅ Connect to VNC at localhost:5900"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "📋 Next Steps:"
echo "   1. Import VM into VirtualBox/UTM"
echo "   2. Copy Dictionary App folder to VM"  
echo "   3. Run test-dictionary-app.sh inside VM"
echo "   4. Test hotkeys (double Ctrl)"
echo "   5. Test system tray functionality"

echo ""
echo "🎯 What to test:"
echo "   - App starts without errors"
echo "   - Double Ctrl opens search window"
echo "   - Search works with sample data"
echo "   - System tray icon appears"
echo "   - Settings window opens"