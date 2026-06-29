# pi-kiosk-presenter
A Python script to load a URL in a Chrome browser to act as a presenter screen.

launcher.py auto-runs when the Pi starts. The git repository will be checked for updates. If there are updates, they will be installed. All requirements will be installed. Once installed, presenter.py will run.

## Setup
Clone the repository:
```
git clone https://github.com/BryceL95/pi-kiosk-presenter.git
```

install.sh will run a few configurations to get the real-time clock set up and the virtual environment created.


## Hardware
Recommended hardware: Raspberry Pi 4 or Pi 5.

It is recommended to add the DS3231 Real Time Clock module so the Pi can keep accurate time. This connects directly to the Pi using pins 1, 3, 5, 7, and 9.
[Amazon Link - DS3231](https://www.amazon.com/dp/B08X4H3NBR?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)

![Image of DS3231](/images/DS3231.jpg)

A button can be added between GPIO 17 (pin 11 on the Pi) and Ground. This button will reload the browser when pressed.
