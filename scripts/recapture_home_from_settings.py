#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

from PIL import Image

device = "ZY227PJ5BN"
ASSETS = Path(__file__).resolve().parents[1] / "assets"
TOP = 78


def adb(*args: str):
    subprocess.run(["adb", "-s", device, *args], check=True)


def cap(path: Path) -> tuple[int, int, int]:
    raw = subprocess.run(
        ["adb", "-s", device, "exec-out", "screencap", "-p"],
        check=True,
        capture_output=True,
    ).stdout
    path.write_bytes(raw)
    img = Image.open(path).convert("RGB")
    w, h = img.size
    img = img.crop((0, TOP, w, h))
    img.save(path, optimize=True, quality=92)
    return img.getpixel((img.width // 2, 400))


# Start on Settings (known good), then Home
adb("shell", "am", "start", "-n", "com.vfrbuddy.app/.MainActivity")
time.sleep(8)
adb("shell", "input", "tap", "980", "2220")  # Settings tab
time.sleep(3)
px = cap(ASSETS / "_settings_check.png")
print("settings pixel", px)
adb("shell", "input", "tap", "180", "2220")  # Home tab
time.sleep(8)
px2 = cap(ASSETS / "screenshot-home-favorites.png")
print("home pixel", px2)
Path(ASSETS / "_settings_check.png").unlink(missing_ok=True)
