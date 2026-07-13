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
from gpiozero import Button

os.environ['GPIOZERO_PIN_FACTORY'] = 'lgpio'
os.environ["DISPLAY"] = ":0"
subprocess.run(["xset", "s", "off"])
subprocess.run(["xset", "-dpms"])
subprocess.run(["xset", "s", "noblank"])

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

def get_customer_id():
    if os.path.exists(CUSTOMER_ID_FILE):
        with open(CUSTOMER_ID_FILE, "r") as f:
            return f.read().strip()
    else:
        customerID = "0"
        with open(CUSTOMER_ID_FILE, "w") as f:
            f.write(customerID)
        return customerID   

def get_version():
    if os.path.exists("version.txt"):
        with open("version.txt", "r") as f:
            return f.read().strip()
    else:
        return "0.0.0"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

def set_resolution_x11(width, height, display_name):
    """
    Changes screen resolution on X11-based Raspberry Pi OS.
    """
    # command = f"xrandr --size {width}x{height}"
    command = f"xrandr --output {display_name} --mode {width}x{height}"
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Resolution shifted to {width}x{height}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to change resolution: {e}")

def switch_display_mode(mode):
    # Replace these with your actual monitor names from 'xrandr -q'
    primary_display = "HDMI-1"
    secondary_display = "HDMI-2"
    
    if mode == "Extend":
        # Extend: Place HDMI-2 to the right of HDMI-1
        command = [
            "xrandr", 
            "--output", primary_display, "--auto",
            "--output", secondary_display, "--auto", "--right-of", primary_display
        ]
        
    elif mode == "Duplicate":
        # Duplicate/Mirror: Make HDMI-2 clone HDMI-1
        command = [
            "xrandr", 
            "--output", primary_display, "--auto",
            "--output", secondary_display, "--auto", "--same-as", primary_display
        ]
        
    else:
        print("Invalid mode. Use 'Extend' or 'Duplicate'")
        return

    # Execute the command
    try:
        subprocess.run(command, check=True)
        print(f"Successfully switched to {mode} mode.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to change screen mode: {e}")


DEVICE_ID_FILE = "deviceID.txt"
CUSTOMER_ID_FILE = "customerID.txt"
DEVICE_FW = get_version()
TYPE = "presenter"
DEVICE_HW = get_device_model()
DEVICE_ID = get_or_create_device_id()
USER_ID = get_customer_id()
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
CurrentURL2 = ""
LastRotation = ""
LastRotation2 = ""
LastResolution = ""
LastResolution2 = ""
LastDisplayMode = ""

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

def get_connected_outputs():
    result = subprocess.check_output("xrandr", shell=True).decode()
    
    connected = []
    for line in result.splitlines():
        if " connected" in line:
            name = line.split()[0]
            connected.append(name)
    
    return connected

screens = get_connected_outputs()
print("Connected screens:", screens)

def reloadPage():
    print("Manual Browser Reload")
    driver1.get(PresenterUrl)
    driver1.execute_script("document.body.style.cursor = 'none';")

    if len(screens) >= 2:
        driver2.get(PresenterUrl2)
        driver2.execute_script("document.body.style.cursor = 'none';")

def CheckSettings(setting, default):
    if SettingsParsed and setting in SettingsParsed and SettingsParsed[setting] != "":
        print(f"{setting}: ", SettingsParsed[setting])
        return SettingsParsed[setting]
    else:
        print(f"{setting}: ", default)
        return default
    
def rotate_screen(orientation, screen):
    print("orientation", orientation)
    print("screen", screen)
    try:
        # Determine the display name (usually HDMI-1 or DSI-1)
        # You can find yours by running 'xrandr' in the terminal
        display_name = "HDMI-1"
        if screen == 1:
            display_name = "HDMI-1"
        elif screen == 2:
            display_name = "HDMI-2"
        
        command = ["xrandr", "--output", display_name, "--rotate", orientation]
        subprocess.run(command, check=True)
        print(f"Screen rotated to: {orientation}")
    except subprocess.CalledProcessError as e:
        print(f"Error rotating screen: {e}")

def CheckScreenRotation():
    global LastRotation
    global LastRotation2
    rotation = CheckSettings("ScreenRotation", "normal")
    rotation2 = CheckSettings("ScreenRotation2", "normal")

    if rotation != LastRotation:
        rotate_screen(rotation, 1)
        LastRotation = rotation

    if rotation2 != LastRotation2:
        rotate_screen(rotation2, 2)
        LastRotation2 = rotation2

def CheckResolution():
    global LastResolution
    global LastResolution2
    resolution = CheckSettings("Resolution", "1920x1080")
    resXY = resolution.split("x")

    resolution2 = CheckSettings("Resolution2", "1920x1080")
    resXY2 = resolution2.split("x")

    if resolution != LastResolution:
        set_resolution_x11(resXY[0], resXY[1], "HDMI-1")
        LastResolution = resolution

    if resolution2 != LastResolution2:
        set_resolution_x11(resXY2[0], resXY2[1], "HDMI-2")
        LastResolution2 = resolution2

def CheckDisplayMode():
    global LastDisplayMode
    DisplayMode = CheckSettings("DisplayMode", "Duplicate")

    if DisplayMode != LastDisplayMode:
        switch_display_mode(DisplayMode)
        LastDisplayMode = DisplayMode

# First boot, push status then get settings
PushStatus()
CheckScreenRotation()
CheckResolution()
CheckDisplayMode()
time.sleep(0.5)

while True:
    print("SettingsCount", SettingsCount)

    if SettingsCount == 10:
        SettingsCount = 0
        PushStatus()
        CheckScreenRotation()
        CheckResolution()
        CheckDisplayMode()
        time.sleep(0.5)

    # screen 1 options
    options1 = webdriver.ChromeOptions()
    options1.add_argument("--kiosk")
    options1.add_argument("--window-position=0,0")
    options1.add_argument("--window-size=1920,1080")
    options1.add_argument("start-maximized")
    options1.add_argument("--deny-permission-prompts")
    options1.add_argument("disable-infobars")
    options1.add_argument("--disable-blink-features=AutomationControlled")
    options1.add_experimental_option("excludeSwitches", ["enable-automation"])
    options1.add_experimental_option("useAutomationExtension", False)

    # screen 2 options
    options2 = webdriver.ChromeOptions()
    options2.add_argument("--kiosk")
    options2.add_argument("--window-position=1920,0")
    options2.add_argument("--window-size=1920,1080")
    options2.add_argument("start-maximized")
    options2.add_argument("--deny-permission-prompts")
    options2.add_argument("disable-infobars")
    options2.add_argument("--disable-blink-features=AutomationControlled")
    options2.add_experimental_option("excludeSwitches", ["enable-automation"])
    options2.add_experimental_option("useAutomationExtension", False)

    PresenterUrl = CheckSettings("PresenterUrl", "https://rrdev.brycelongacre.com/kiosk/")
    PresenterUrl2 = CheckSettings("PresenterUrl2", "https://rrdev.brycelongacre.com/kiosk/")

    if PresenterStatus == False:
        print("Open browser...")
        CurrentURL = PresenterUrl
        CurrentURL2 = PresenterUrl2
        PresenterStatus = True

        driver1 = webdriver.Chrome(options=options1)
        driver1.get(PresenterUrl)
        driver1.execute_script("document.body.style.cursor = 'none';")

        if len(screens) >= 2:
            print("Dual screens")
            
            driver2 = webdriver.Chrome(options=options2)
            driver2.get(PresenterUrl2)
            driver2.execute_script("document.body.style.cursor = 'none';")

    elif PresenterUrl != CurrentURL:
        print("New url - Browser Reload")
        CurrentURL = PresenterUrl

        driver1 = webdriver.Chrome(options=options1)
        driver1.get(PresenterUrl)
        driver1.execute_script("document.body.style.cursor = 'none';")
    elif PresenterUrl2 != CurrentURL2 and len(screens) >= 2:
        print("New url - Browser Reload Screen 2")
        CurrentURL2 = PresenterUrl2

        driver2 = webdriver.Chrome(options=options2)
        driver2.get(PresenterUrl2)
        driver2.execute_script("document.body.style.cursor = 'none';")
    else:
        print("Browser running")
        time.sleep(1)

    button.when_pressed = reloadPage

    # count each cycle
    SettingsCount += 1
