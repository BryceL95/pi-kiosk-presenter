import os
import subprocess
import time
import sys
import shutil

BASE_DIR = "/home/brycel/pi-kiosk-presenter"

VENV_PYTHON = os.path.join(BASE_DIR, "venv/bin/python")
PRESENTER = os.path.join(BASE_DIR, "presenter.py")
REQUIREMENTS = os.path.join(BASE_DIR, "requirements.txt")


def update_repo():
    print("Checking for updates...")

    result = subprocess.run(
        ["git", "pull"],
        cwd=BASE_DIR,
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print("Git pull failed:")
        print(result.stderr)


def install_requirements():
    if os.path.exists(REQUIREMENTS):
        print("Installing requirements...")

        subprocess.run(
            [VENV_PYTHON, "-m", "pip", "install", "-r", REQUIREMENTS],
            cwd=BASE_DIR
        )


def start_presenter():
    print("Starting presenter...")

    # IMPORTANT FIX:
    # Replace launcher process entirely with presenter using venv Python
    os.execv(
        VENV_PYTHON,
        [VENV_PYTHON, PRESENTER]
    )


def ensure_chromium_installed():
    chromium_exists = (
        shutil.which("chromium") or
        shutil.which("chromium-browser")
    )

    chromedriver_exists = shutil.which("chromedriver")

    if chromium_exists and chromedriver_exists:
        print("Chromium already installed")
        return

    print("Chromium not found. Installing...")

    subprocess.run(
        ["sudo", "apt", "update"],
        check=True
    )

    subprocess.run(
        [
            "sudo",
            "apt",
            "install",
            "-y",
            "chromium",
            "chromium-driver"
        ],
        check=True
    )

    print("Chromium installation complete")

def main():
    update_repo()

    # Optional but recommended if you're actively developing
    install_requirements()

    ensure_chromium_installed()

    time.sleep(1)

    start_presenter()


if __name__ == "__main__":
    main()
