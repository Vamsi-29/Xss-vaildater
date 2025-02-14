#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status
set -o pipefail  # Catch errors in piped commands

handle_error() {
    echo "[✘] Error on line $1. Exiting..."
    exit 1
}
trap 'handle_error $LINENO' ERR

echo "[+] Updating package lists..."
sudo apt update

echo "[+] Installing Python3 and pip..."
sudo apt install -y python3 python3-pip || { echo "[✘] Failed to install Python3 and pip"; exit 1; }

echo "[+] Installing Google Chrome..."
wget -q -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb || { echo "[✘] Failed to download Google Chrome"; exit 1; }
sudo apt install -y ./google-chrome.deb || { echo "[✘] Failed to install Google Chrome"; exit 1; }
rm google-chrome.deb

echo "[+] Installing required Python packages..."
pip3 install --upgrade requests selenium webdriver-manager || { echo "[✘] Failed to install Python packages"; exit 1; }

echo "[+] Verifying installation..."
python3 -c "import requests, selenium, webdriver_manager; print('[✔] All dependencies installed successfully.')" || { echo "[✘] Python dependency verification failed"; exit 1; }

echo "[✔] Setup complete. You can now run your XSS scanner."
