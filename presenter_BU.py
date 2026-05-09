#!/home/BryceL/kiosk-venv/bin/python3
import requests
import time
import json
import hashlib
import os
import subprocess
import socket
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timezone

import os
os.environ['GPIOZERO_PIN_FACTORY'] = 'lgpio'
from gpiozero import Button

button = Button(17)

def get_device_model():
    try:
        with open("/proc/device-tree/model", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def generate_short_id(prefix="K"):
    serial = None
    with open("/proc/cpuinfo", "r") as f:
        for line in f:
            if line.startswith("Serial"):
                serial = line.strip().split(":")[1].strip()
                break

    if not serial:
        raise RuntimeError("Could not read Pi serial number")

    # Hash and shorten to 4 digits
    h = hashlib.sha1(serial.encode()).hexdigest()
    short_num = int(h, 16) % 10000
    return f"{prefix}-{short_num:04d}"


def get_or_create_device_id():
    if os.path.exists(DEVICE_ID_FILE):
        with open(DEVICE_ID_FILE, "r") as f:
            return f.read().strip()
    else:
        deviceID = generate_short_id()
        with open(DEVICE_ID_FILE, "w") as f:
            f.write(deviceID)
        return deviceID

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

DEVICE_ID_FILE = "/home/BryceL/deviceID.txt"
DEVICE_FW = 1.3
TYPE = "presenter"
DEVICE_HW = get_device_model()
DEVICE_ID = get_or_create_device_id()
USER_ID = 32178
LOCAL_IP = get_local_ip()

print("DEVICE_FW:", DEVICE_FW)
print("TYPE:", TYPE)
print("DEVICE_HW:", DEVICE_HW)
print("DEVICE_ID:", DEVICE_ID)
print("USER_ID:", USER_ID)
print("LOCAL_IP:", LOCAL_IP)

SettingsParsed = []
PresenterStatus = False
SettingsCount = 0
CurrentURL = ""
LastRotation = "normal"


def PushStatus():
    global SettingsParsed
    utc_now = datetime.now(timezone.utc)
    utc_timestamp = utc_now.timestamp()
    print(utc_timestamp)

    url = f"https://rrdev.brycelongacre.com/kioskstatus/?type={TYPE}&fw={DEVICE_FW}&hw={DEVICE_HW}&deviceID={DEVICE_ID}&userID={USER_ID}&ip={LOCAL_IP}&timestamp={utc_timestamp}"

    payload = {}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        print(f"PushStatus: {response.status_code}")
        SettingsParsed = json.loads(response.text)
    except:
        print("GET Status error")

def reloadPage():
    print("Browser Reload")
    CurrentURL = PresenterUrl
    driver.get(PresenterUrl)
    driver.execute_script("document.body.style.cursor = 'none';")

def CheckSettings(setting, default):
    if SettingsParsed and setting in SettingsParsed:
        return SettingsParsed[setting]
    else:
        return default
    
def rotate_screen(orientation):
    print("orientation", orientation)
    try:
        # Determine the display name (usually HDMI-1 or DSI-1)
        # You can find yours by running 'xrandr' in the terminal
        display_name = "HDMI-1" 
        
        command = ["xrandr", "--output", display_name, "--rotate", orientation]
        subprocess.run(command, check=True)
        print(f"Screen rotated to: {orientation}")
    except subprocess.CalledProcessError as e:
        print(f"Error rotating screen: {e}")

def CheckScreenRotation():
    global LastRotation
    rotation = CheckSettings("ScreenRotation", "normal")
    print("rotation", rotation)
    print("LastRotation", LastRotation)

    if rotation != LastRotation:
        rotate_screen(rotation)
        LastRotation = rotation

# First boot, push status then get settings
PushStatus()
CheckScreenRotation()
time.sleep(0.5)

while True:
    print("SettingsCount", SettingsCount)

    if SettingsCount == 10:
        SettingsCount = 0
        PushStatus()
        CheckScreenRotation()
        time.sleep(0.5)

    # PresenterUrl = CheckSettings(
    #     "PresenterUrl", "https://rrdev.brycelongacre.com/kiosk/default.html"
    # )

    PresenterUrl = CheckSettings(
        "PresenterUrl", "http://192.168.2.188/ui/presenter/e2da064e-b0e7-443c-9441-5ff56aea3d69"
    )

    print(PresenterUrl)

    if PresenterStatus == False:
        print("Open browser...")
        CurrentURL = PresenterUrl
        PresenterStatus = True

        chrome_options = Options()
        # chrome_options.add_argument("--ozone-platform=x11")
        chrome_options.add_argument("--kiosk")
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("--deny-permission-prompts")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(PresenterUrl)
        driver.execute_script("document.body.style.cursor = 'none';")

    elif PresenterUrl != CurrentURL:
        print("Browser Reload")
        CurrentURL = PresenterUrl
        driver.get(PresenterUrl)
        driver.execute_script("document.body.style.cursor = 'none';")
    else:
        print("Browser running")
        time.sleep(1)

    button.when_pressed = reloadPage

    # count each cycle
    SettingsCount += 1
