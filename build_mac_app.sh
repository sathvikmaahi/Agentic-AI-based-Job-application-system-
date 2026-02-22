#!/bin/bash

# ApplyAI - macOS App Builder
cd "$(dirname "$0")"

echo "==========================================="
echo "       ApplyAI - Building macOS App"
echo "==========================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r docs/requirements.txt
pip install Pillow  # For icon generation

# Generate icon
echo "Generating app icon..."
python3 assets/generate_icon.py

# Create placeholder data files
touch "data/user_config.json"
touch "data/resumes_config.json"
touch "data/user_profile.json"
touch "data/schedule_config.json"

# Build the macOS app
echo "Building macOS application..."
python -m PyInstaller \
    --name="ApplyAI" \
    --windowed \
    --onedir \
    --clean \
    --noconfirm \
    --collect-all customtkinter \
    --collect-all selenium \
    --collect-all webdriver_manager \
    --hidden-import "selenium.webdriver.chrome.options" \
    --hidden-import "selenium.webdriver.chrome.service" \
    --hidden-import "selenium.webdriver.common.by" \
    --hidden-import "selenium.webdriver.support.ui" \
    --hidden-import "selenium.webdriver.support.expected_conditions" \
    --hidden-import "selenium.webdriver.common.action_chains" \
    --add-data "data/user_config.json:data" \
    --add-data "data/resumes_config.json:data" \
    --add-data "data/user_profile.json:data" \
    --add-data "data/schedule_config.json:data" \
    --add-data "assets/icon.png:assets" \
    --paths "ui" \
    --paths "core" \
    --paths "utils" \
    ui/main.py

# Clean up
rm -rf build/ApplyAI

if [ -d "dist/ApplyAI.app" ]; then
    echo ""
    echo "✅ BUILD SUCCESSFUL!"
    echo "Your app is ready: dist/ApplyAI.app"
    
    # Copy YAML configs
    cp data/*.yaml "dist/ApplyAI.app/Contents/Resources/data/" 2>/dev/null || true
    rm -f "dist/ApplyAI.app/Contents/Resources/data/"*.json 2>/dev/null || true
    
    # Copy to desktop
    rm -rf ~/Desktop/ApplyAI.app ~/Desktop/JobsPro.app
    cp -R "dist/ApplyAI.app" ~/Desktop/
    echo "📱 App copied to Desktop!"
    open dist
else
    echo "❌ Build failed"
fi
