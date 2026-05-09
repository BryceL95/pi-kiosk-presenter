#!/bin/bash

set -e

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

cd /home/pi/kiosk

python3 -m venv venv

source venv/bin/activate

pip install --upgrade pip

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

echo "=============================="
echo "RTC setup complete."
echo "Reboot required."
echo "=============================="

sudo reboot