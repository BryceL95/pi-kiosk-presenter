# pi-kiosk-presenter
A Python script to load a URL in a Chrome browser to act as a presenter screen.

launcher.py auto-runs when the Pi starts. The git repository will be checked for updates. If there are updates, they will be installed. All requirements will be installed. Once installed, presenter.py will run.

## Creating an account
Your Kiosk settings are configured through your browser. Navigate to [rrdev.brycelongacre.com/tools-new](https://rrdev.brycelongacre.com/tools-new/) and register an account. It is recommended to use your Race Result customer ID when creating your rrdev customer account. You will need this ID during the hardware setup.

## Hardware Setup
Clone the repository. Make sure to clone the stable branch and not the main one
```
git clone -b stable https://github.com/BryceL95/pi-kiosk-presenter.git
```

Run the following command to install all necessary packages, enable i2C, configure real-time clock, create the virtual environment, and configure auto boot. When running the install, you will be asked for your customerID which was configured in the last step.
```
bash install.sh
```

## Hardware
Recommended hardware: Raspberry Pi 4 or Pi 5.

It is recommended to add the DS3231 Real Time Clock module so the Pi can keep accurate time. This connects directly to the Pi using pins 1, 3, 5, 7, and 9.
[Amazon Link - DS3231](https://www.amazon.com/dp/B08X4H3NBR?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)

![Image of DS3231](/assets/images/DS3231.jpg)

A button can be added between GPIO 17 (pin 11 on the Pi) and Ground. This button will reload the browser when pressed.

This [Raspberry Pi 4 Case](https://www.amazon.com/dp/B07Y7W3GFH?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_2) can be used with the [Kiosk Pi Case.STL](</assets/3D_Files/Kiosk Pi Case.STL>) to add a button to Pi4 easily.

![Pi4 Case Top](/assets/images/CaseTop.png)


## How to configure kiosk settings
Log into [rrdev.brycelongacre.com/tools-new](https://rrdev.brycelongacre.com/tools-new/) and navigate to Kiosk on the left. Here you will see a list of all Kiosk devices that have connected to your account. Selecting Settings will open a window where you can change settings for the device. Below is a list of settings and what they do.

| Setting Name      | Description                                                                  |
|-------------------|------------------------------------------------------------------------------|
| Event Name        | Name of the event. Just used as a reference. Not used for anything on the Pi |
| Presenter URL     | The URL to load on screen 1 of the Pi                                        |
| Screen Rotation   | The rotation of screen 1                                                     |
| Presenter URL 2   | The URL to load on screen 2 of the Pi                                        |
| Screen Rotation 2 | The rotation of screen 2                                                     |

![Kiosk Settings](/assets/images/KioskSettings.png)