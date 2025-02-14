#!/bin/bash


echo "[+] Installing Python3 and pip..."
sudo apt install -y python3 python3-pip

echo "[+] Installing Google Chrome..."
wget -q -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome.deb
rm google-chrome.deb

echo "[+] Installing required Python packages..."
pip3 install --upgrade requests selenium webdriver-manager

echo "[+] Verifying installation..."
python3 -c "import requests, selenium, webdriver_manager; print('[✔] All dependencies installed successfully.')"

echo "[✔] Setup complete. You can now run your XSS scanner."
