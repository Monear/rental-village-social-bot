#!/bin/bash

echo "🔧 Installing Dependencies and Fixing Sanity Data"
echo "================================================"

# Check if running as root/sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script needs sudo access to install system dependencies"
    echo "Please run: sudo ./install-deps-and-fix.sh"
    exit 1
fi

# Get the original user (the one who ran sudo)
ORIGINAL_USER=${SUDO_USER:-$USER}
ORIGINAL_HOME=$(getent passwd "$ORIGINAL_USER" | cut -d: -f6)

echo "👤 Running as: $ORIGINAL_USER"
echo "🏠 Home directory: $ORIGINAL_HOME"

# Install required system packages
echo "📦 Installing system dependencies..."
apt-get update -qq
apt-get install -y python3-venv python3-pip git

if [ $? -ne 0 ]; then
    echo "❌ Failed to install system dependencies"
    exit 1
fi

echo "✅ System dependencies installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found in current directory"
    echo "Please ensure your .env file with Sanity credentials is present"
    exit 1
fi

echo "✅ Found .env file"

# Create virtual environment in user's home directory
VENV_PATH="$ORIGINAL_HOME/.sanity-fix-venv"

echo "📦 Creating virtual environment at $VENV_PATH..."
sudo -u "$ORIGINAL_USER" python3 -m venv "$VENV_PATH"

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"

# Install Python dependencies as the original user
echo "📦 Installing Python dependencies..."
sudo -u "$ORIGINAL_USER" "$VENV_PATH/bin/pip" install --quiet python-dotenv git+https://github.com/OmniPro-Group/sanity-python.git

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    sudo -u "$ORIGINAL_USER" rm -rf "$VENV_PATH"
    exit 1
fi

echo "✅ Python dependencies installed"

# Run the fix script as the original user
echo "🚀 Running Sanity data fix..."
sudo -u "$ORIGINAL_USER" "$VENV_PATH/bin/python" fix-sanity-data.py

exit_code=$?

# Clean up
echo "🧹 Cleaning up..."
sudo -u "$ORIGINAL_USER" rm -rf "$VENV_PATH"

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "🎉 Sanity data fix completed successfully!"
    echo ""
    echo "What was fixed:"
    echo "✅ Added missing _key properties to all array items"
    echo "✅ Cleaned up unnecessary fields"
    echo "✅ Organized data for new schema structure"
    echo "✅ Updated timestamps"
    echo ""
    echo "Next steps:"
    echo "1. Restart your Sanity Studio: sudo podman-compose restart sanity-studio"
    echo "2. Open Studio and verify the equipment data displays correctly"
    echo "3. Check that arrays can be edited without 'missing keys' errors"
else
    echo "❌ Sanity data fix failed. Check the output above for details."
    exit 1
fi