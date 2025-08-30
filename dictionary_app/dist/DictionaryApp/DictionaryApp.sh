#!/bin/bash
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
    
    echo "Installing core dependencies..."
    "$DIR/venv/bin/pip" install -q -r "$DIR/requirements.txt"
    
    echo "Installing plugin dependencies..."
    # Install dependencies for each plugin that has requirements.txt
    for plugin_dir in "$DIR"/plugins/*/; do
        if [ -f "$plugin_dir/requirements.txt" ]; then
            plugin_name=$(basename "$plugin_dir")
            echo "Installing dependencies for $plugin_name plugin..."
            "$DIR/venv/bin/pip" install -q -r "$plugin_dir/requirements.txt"
        fi
    done
    
    echo "All dependencies installed!"
fi

# Activate virtual environment and run app
echo "Starting Dictionary App..."
"$DIR/venv/bin/python" "$DIR/run_app.py"
