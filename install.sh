#!/bin/bash

sudo apt update
sudo apt upgrade
sudo apt install python3 python3-venv ffmpeg nano -y

python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade discord.py
python3 -m pip install yt-dlp ffmpeg ffprobe PyNaCl
python3 -m pip install pillow
echo "All required packages have been installed."
clear
read -s -p "Enter your token: " TOKEN
echo
echo "TOKEN = \"$TOKEN\"" > bot_token.py
echo "Token saved to bot_token.py."

# --- AUTOSTART SETUP ---
SERVICE_NAME="kumpanbot"
BOT_PATH="$(pwd)/main.py"

echo "Do you want to set up autostart for the bot as a systemd service? (y/n)"
read answer

if [[ "$answer" != "y" ]]; then
    echo "Autostart service was not set up."
    exit 0
fi

cat <<EOF | sudo tee /etc/systemd/system/$SERVICE_NAME.service
[Unit]
Description=Kumpanbot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python $BOT_PATH
Restart=always
RestartSec=20

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME.service       # Activates the service at boot
sudo systemctl start $SERVICE_NAME.service        # Starts the service immediately

clear

echo "Systemd service has been enabled (will start at boot) and started as root."
echo "To stop the service: sudo systemctl stop $SERVICE_NAME"
echo "To remove the service: sudo systemctl disable $SERVICE_NAME && sudo rm /etc/systemd/system/$SERVICE_NAME.service"
echo "Service status:"
sudo systemctl status $SERVICE_NAME.service --no-pager
