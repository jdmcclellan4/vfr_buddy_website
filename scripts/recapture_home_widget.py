#!/usr/bin/env python3
import re
import subprocess
import time
from pathlib import Path

from PIL import Image

device = "ZY227PJ5BN"
ASSETS = Path(__file__).resolve().parents[1] / "assets"
TOP = 78


def adb(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["adb", "-s", device, *args], check=True, capture_output=True, text=True)


def screencap(path: Path, crop_top: int = TOP) -> Image.Image:
    raw = subprocess.run(
        ["adb", "-s", device, "exec-out", "screencap", "-p"],
        check=True,
        capture_output=True,
    ).stdout
    path.write_bytes(raw)
    img = Image.open(path).convert("RGB")
    w, h = img.size
    cropped = img.crop((0, crop_top, w, h))
    cropped.save(path, optimize=True, quality=92)
    return cropped


adb("shell", "am", "force-stop", "com.vfrbuddy.app")
adb("reverse", "tcp:8081", "tcp:8081")
adb("shell", "am", "start", "-n", "com.vfrbuddy.app/.MainActivity")
time.sleep(14)

xml = adb("shell", "cat", "/sdcard/vfr_ui.xml").stdout if False else ""
adb("shell", "uiautomator", "dump", "/sdcard/vfr_ui.xml")
xml = adb("shell", "cat", "/sdcard/vfr_ui.xml").stdout
texts = [t for t in re.findall(r'text="([^"]+)"', xml) if len(t) > 1]
print("UI texts:", texts[:20])
print("Has Favorites:", "Favorites" in xml)

home = ASSETS / "screenshot-home-favorites.png"
img = screencap(home)
print("Home saved", home, img.size, "mid pixel", img.getpixel((img.width // 2, 300)))

# Widget: swipe launcher to page with widget if needed, then crop
adb("shell", "input", "keyevent", "3")
time.sleep(2)
launcher = ASSETS / "_launcher.png"
full = screencap(launcher, crop_top=0)
# find non-black region - widget is navy; scan for content
w, h = full.size
best_y = TOP + 750
widget = full.crop((20, best_y, w - 20, min(h, best_y + 1000)))
widget.save(ASSETS / "screenshot-widget.png", optimize=True, quality=92)
print("Widget saved", widget.size)
launcher.unlink(missing_ok=True)
