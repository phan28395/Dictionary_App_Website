#!/bin/bash
# Start Windows-like testing environment

echo "Starting X11 display..."
Xvfb :0 -screen 0 1024x768x24 &
sleep 2

echo "Starting window manager..."
fluxbox &
sleep 1

echo "Starting VNC server..."
x11vnc -display :0 -nopw -listen localhost -xkb -ncache 10 -ncache_cr -forever &

echo "Testing Python in Wine..."
wine python --version

echo "Environment ready!"
echo "Connect with VNC viewer to localhost:5900"
echo "Dictionary app is in /app/"

# Keep container running
tail -f /dev/null