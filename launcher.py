import subprocess
import os
import time

BASE_DIR = "/home/BryceL/pi-kiosk-presenter"

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
    subprocess.run(
        [
            f"{BASE_DIR}/venv/bin/pip",
            "install",
            "-r",
            "requirements.txt"
        ],
        cwd=BASE_DIR
    )


def start_app():
    subprocess.Popen(
        [f"{BASE_DIR}/venv/bin/python", "presenter.py"],
        cwd=BASE_DIR
    )


def main():
    update_repo()

    # Optional:
    install_requirements()

    time.sleep(2)

    start_app()


if __name__ == "__main__":
    main()
