#!/bin/bash

set -e

# ==============================
# Resolve user and paths dynamically
# ==============================
# Works whether the script is run as the normal user (with sudo used
# per-command, as in the rest of this script) or invoked with sudo.
TARGET_USER="${SUDO_USER:-$(whoami)}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
PROJECT_DIR="$TARGET_HOME/pi-kiosk-presenter"

echo "Target user:    $TARGET_USER"
echo "Home directory: $TARGET_HOME"
echo "Project dir:    $PROJECT_DIR"

echo "=============================="
echo "Customer ID Setup"
echo "=============================="

read -rp "Enter Customer ID: " CUSTOMER_ID

if [ -z "$CUSTOMER_ID" ]; then
    echo "Customer ID cannot be empty."
    exit 1
fi

echo "$CUSTOMER_ID" > "$PROJECT_DIR/customerID.txt"
echo "Customer ID saved to $PROJECT_DIR/customerID.txt"

echo "=============================="
echo "Updating packages..."
echo "=============================="

sudo apt update

echo "=============================="
echo "Installing packages..."
echo "=============================="

sudo apt install -y i2c-tools python3-venv git

echo "=============================="
echo "Enabling I2C..."
echo "=============================="

sudo raspi-config nonint do_i2c 0

CONFIG_FILE=""

if [ -f /boot/firmware/config.txt ]; then
    CONFIG_FILE="/boot/firmware/config.txt"
elif [ -f /boot/config.txt ]; then
    CONFIG_FILE="/boot/config.txt"
else
    echo "Could not find config.txt"
    exit 1
fi

echo "Using config file: $CONFIG_FILE"

if ! grep -q "dtoverlay=i2c-rtc,ds3231" "$CONFIG_FILE"; then
    echo "" | sudo tee -a "$CONFIG_FILE"
    echo "dtoverlay=i2c-rtc,ds3231" | sudo tee -a "$CONFIG_FILE"
fi

echo "=============================="
echo "Removing fake-hwclock..."
echo "=============================="

sudo apt-get -y remove fake-hwclock || true
sudo update-rc.d -f fake-hwclock remove || true
sudo systemctl disable fake-hwclock || true

echo "=============================="
echo "Patching hwclock-set..."
echo "=============================="

HWCLOCK_FILE="/lib/udev/hwclock-set"

if [ -f "$HWCLOCK_FILE" ]; then

    sudo sed -i 's/^if \[ -e \/run\/systemd\/system \] ; then/#if [ -e \/run\/systemd\/system ] ; then/' "$HWCLOCK_FILE"

    sudo sed -i 's/^    exit 0/#    exit 0/' "$HWCLOCK_FILE"

    sudo sed -i 's/^fi/#fi/' "$HWCLOCK_FILE"

    sudo sed -i 's/^\/sbin\/hwclock --rtc=\$dev --systz/#\/sbin\/hwclock --rtc=\$dev --systz/' "$HWCLOCK_FILE"

fi

echo "=============================="
echo "Creating Python virtual environment..."
echo "=============================="

cd "$PROJECT_DIR"

python3 -m venv venv

source venv/bin/activate

pip install --upgrade pip

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

deactivate

echo "=============================="
echo "RTC setup complete."
echo "=============================="

echo "=============================="
echo "Configuring display power settings..."
echo "=============================="

AUTOSTART_FILE="$TARGET_HOME/.config/lxsession/LXDE-pi/autostart"

mkdir -p "$TARGET_HOME/.config/lxsession/LXDE-pi"

# Ensure file exists
touch "$AUTOSTART_FILE"

# Add xset settings if not already present (keeps the screen from blanking)
grep -qxF "@xset s off" "$AUTOSTART_FILE" || echo "@xset s off" >> "$AUTOSTART_FILE"
grep -qxF "@xset -dpms" "$AUTOSTART_FILE" || echo "@xset -dpms" >> "$AUTOSTART_FILE"
grep -qxF "@xset s noblank" "$AUTOSTART_FILE" || echo "@xset s noblank" >> "$AUTOSTART_FILE"

echo "=============================="
echo "Creating systemd service..."
echo "=============================="

SERVICE_FILE="/etc/systemd/system/kiosk.service"

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Kiosk
After=network.target

[Service]
User=$TARGET_USER
WorkingDirectory=$PROJECT_DIR
Environment=HOME=$TARGET_HOME
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/launcher.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Wrote service file: $SERVICE_FILE"

sudo systemctl daemon-reload
sudo systemctl enable kiosk.service

echo "=============================="
echo "Setup complete. Reboot required."
echo "=============================="

sudo reboot