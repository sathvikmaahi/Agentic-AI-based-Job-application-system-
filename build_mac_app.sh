#!/bin/bash
set -euo pipefail

# ApplyAI - macOS App Builder
#
# After ANY code or dependency change, run this script so Desktop stays in sync:
#   ./build_mac_app.sh
# It rebuilds dist/ApplyAI.app and copies it to ~/Desktop/ApplyAI.app

cd "$(dirname "$0")"
shopt -s nullglob

echo "==========================================="
echo "       ApplyAI - Building macOS App"
echo "==========================================="

VENV_DIR="jobspro_env"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment: $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install -q -r docs/requirements.txt
pip install -q Pillow

# Generate icon
echo "Generating app icon..."
python3 assets/generate_icon.py

# PyInstaller --add-data entries (macOS uses : as separator)
PYI_DATA=(--add-data "assets/icon.png:assets")
for f in data/*.yaml; do
    if [[ -f "$f" ]]; then
        # Never bundle local OTP recipient list into the .app
        base="$(basename "$f")"
        [[ "$base" == "authorized_users.yaml" || "$base" == "smtp_config.yaml" ]] && continue
        PYI_DATA+=(--add-data "$f:data")
    fi
done

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
    --collect-all undetected_chromedriver \
    --hidden-import "yaml" \
    --hidden-import "_yaml" \
    --hidden-import "undetected_chromedriver" \
    --hidden-import "selenium.webdriver.chrome.options" \
    --hidden-import "selenium.webdriver.chrome.service" \
    --hidden-import "selenium.webdriver.common.by" \
    --hidden-import "selenium.webdriver.support.ui" \
    --hidden-import "selenium.webdriver.support.expected_conditions" \
    --hidden-import "selenium.webdriver.common.action_chains" \
    "${PYI_DATA[@]}" \
    --paths "ui" \
    --paths "core" \
    ui/main.py

if [ -d "dist/ApplyAI.app" ]; then
    echo ""
    echo "✅ BUILD SUCCESSFUL!"
    echo "Your app is ready: dist/ApplyAI.app"

    mkdir -p "dist/ApplyAI.app/Contents/Resources/data"
    for f in data/*.yaml; do
        [[ -f "$f" ]] || continue
        base="$(basename "$f")"
        [[ "$base" == "authorized_users.yaml" || "$base" == "smtp_config.yaml" ]] && continue
        cp "$f" "dist/ApplyAI.app/Contents/Resources/data/"
    done
    # Local secrets (gitignored) — copy into Desktop .app only, never into git
    for secret in authorized_users.yaml smtp_config.yaml; do
        if [[ -f "data/$secret" ]]; then
            cp "data/$secret" "dist/ApplyAI.app/Contents/Resources/data/"
            echo "📋 Included local data/$secret in the app bundle."
        fi
    done

    rm -rf "${HOME}/Desktop/ApplyAI.app" "${HOME}/Desktop/JobsPro.app"
    cp -R "dist/ApplyAI.app" "${HOME}/Desktop/"
    echo "📱 Replaced Desktop/ApplyAI.app with the new build."
    open dist
else
    echo "❌ Build failed (dist/ApplyAI.app missing)"
    exit 1
fi
