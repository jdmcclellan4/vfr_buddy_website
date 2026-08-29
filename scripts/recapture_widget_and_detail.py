#!/usr/bin/env python3
"""Wake device and recapture widget + airport detail screenshots."""
from __future__ import annotations

import re
import subprocess
import time
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path

from PIL import Image

DEVICE = "ZY227PJ5BN"
PACKAGE = "com.vfrbuddy.app"
ASSETS = Path(__file__).resolve().parents[1] / "assets"
STATUS_BAR_CROP_PX = 78


def adb(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["adb", "-s", DEVICE, *args], check=True, capture_output=True, text=True)


def wake_and_unlock() -> None:
    adb("shell", "input", "keyevent", "224")  # WAKEUP
    time.sleep(0.5)
    adb("shell", "input", "keyevent", "82")  # MENU/unlock helper
    time.sleep(0.3)
    adb("shell", "wm", "dismiss-keyguard")
    time.sleep(0.5)
    adb("shell", "input", "swipe", "540", "1800", "540", "800", "300")
    time.sleep(1)


def dump_ui() -> ET.Element:
    adb("shell", "uiautomator", "dump", "/sdcard/vfr_ui.xml")
    xml = adb("shell", "cat", "/sdcard/vfr_ui.xml").stdout
    return ET.fromstring(xml)


def bounds(node: ET.Element) -> tuple[int, int, int, int] | None:
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.attrib.get("bounds", ""))
    if not m:
        return None
    return tuple(map(int, m.groups()))  # type: ignore[return-value]


def tap(x: int, y: int) -> None:
    adb("shell", "input", "tap", str(x), str(y))


def screencap_raw() -> Image.Image:
    raw = subprocess.run(
        ["adb", "-s", DEVICE, "exec-out", "screencap", "-p"],
        check=True,
        capture_output=True,
    ).stdout
    return Image.open(BytesIO(raw)).convert("RGB")


def save_app_screenshot(img: Image.Image, path: Path) -> None:
    w, h = img.size
    cropped = img.crop((0, STATUS_BAR_CROP_PX, w, h))
    cropped.save(path, optimize=True, quality=92)
    print(f"Saved {path.name} {cropped.size}")


def find_tab(root: ET.Element, label: str) -> tuple[int, int]:
    for node in root.iter("node"):
        t = node.attrib.get("text", "")
        d = node.attrib.get("content-desc", "")
        if label in t or label in d:
            b = bounds(node)
            if b:
                return ((b[0] + b[2]) // 2, (b[1] + b[3]) // 2)
    defaults = {"Home": (180, 2220), "Settings": (900, 2220)}
    return defaults.get(label, (540, 2220))


def find_first_icao(root: ET.Element) -> tuple[int, int] | None:
    for node in root.iter("node"):
        t = node.attrib.get("text", "")
        if re.fullmatch(r"K[A-Z0-9]{3}", t):
            b = bounds(node)
            if b:
                return ((b[0] + b[2]) // 2, (b[1] + b[3]) // 2)
    return None


def find_widget_bounds(root: ET.Element) -> tuple[int, int, int, int] | None:
    """Find launcher widget containing ICAO codes."""
    icao_nodes = []
    for node in root.iter("node"):
        t = node.attrib.get("text", "")
        if re.fullmatch(r"K[A-Z0-9]{3}", t):
            b = bounds(node)
            if b:
                icao_nodes.append(b)
    if len(icao_nodes) < 2:
        return None
    x1 = min(b[0] for b in icao_nodes) - 24
    y1 = min(b[1] for b in icao_nodes) - 80
    x2 = max(b[2] for b in icao_nodes) + 24
    y2 = max(b[3] for b in icao_nodes) + 24
    return (max(0, x1), max(0, y1), min(1080, x2), min(2300, y2))


def capture_widget_from_launcher() -> None:
    adb("shell", "input", "keyevent", "3")
    time.sleep(2)
    root = dump_ui()
    widget_bounds = find_widget_bounds(root)
    if not widget_bounds:
        # swipe left/right to find widget page
        for swipe in [("900", "540"), ("180", "540")]:
            adb("shell", "input", "swipe", swipe[0], "1200", swipe[1], "1200", "400")
            time.sleep(1.5)
            root = dump_ui()
            widget_bounds = find_widget_bounds(root)
            if widget_bounds:
                break
    img = screencap_raw()
    if widget_bounds:
        widget = img.crop(widget_bounds)
    else:
        print("Widget bounds not found; using fallback crop")
        widget = img.crop((56, 830, 822, 1787))
    widget.save(ASSETS / "screenshot-widget.png", optimize=True, quality=92)
    print(f"Saved screenshot-widget.png {widget.size}")


def capture_airport_detail() -> None:
    adb("reverse", "tcp:8081", "tcp:8081")
    adb("shell", "am", "force-stop", PACKAGE)
    adb("shell", "am", "start", "-n", f"{PACKAGE}/.MainActivity")
    time.sleep(12)
    root = dump_ui()
    tap(*find_tab(root, "Home"))
    time.sleep(4)
    root = dump_ui()
    texts = [n.attrib.get("text", "") for n in root.iter("node") if n.attrib.get("text")]
    print("Sample UI texts:", [t for t in texts if t][:15])
    icao = find_first_icao(root)
    if not icao:
        print("No ICAO on home; waiting longer")
        time.sleep(8)
        root = dump_ui()
        icao = find_first_icao(root)
    if icao:
        tap(*icao)
        time.sleep(4)
        save_app_screenshot(screencap_raw(), ASSETS / "screenshot-airport-detail.png")
    else:
        raise SystemExit("Could not find favorite ICAO for detail screenshot")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    wake_and_unlock()
    capture_airport_detail()
    wake_and_unlock()
    capture_widget_from_launcher()


if __name__ == "__main__":
    main()
