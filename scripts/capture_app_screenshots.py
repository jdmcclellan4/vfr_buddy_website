#!/usr/bin/env python3
"""Capture VFR Buddy app screenshots via adb and crop system status bar."""
from __future__ import annotations

import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise SystemExit("Install Pillow: pip install pillow")

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DEVICE = None  # auto-pick vfrbuddy package device
PACKAGE = "com.vfrbuddy.app"
# Motorola / 1080-wide phones: crop system status bar (battery, wifi, clock)
STATUS_BAR_CROP_PX = 78


def adb(*args: str, device: str | None = None) -> subprocess.CompletedProcess[str]:
    serial = device or pick_device()
    cmd = ["adb", "-s", serial, *args]
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def pick_device() -> str:
    out = subprocess.run(["adb", "devices"], check=True, capture_output=True, text=True)
    lines = [ln.split()[0] for ln in out.stdout.strip().splitlines()[1:] if "\tdevice" in ln]
    if not lines:
        raise SystemExit("No adb device found")
    for serial in lines:
        pkg = subprocess.run(
            ["adb", "-s", serial, "shell", "pm", "list", "packages", PACKAGE],
            capture_output=True,
            text=True,
        )
        if PACKAGE in pkg.stdout:
            return serial
    return lines[0]


def tap(device: str, x: int, y: int) -> None:
    adb("shell", "input", "tap", str(x), str(y), device=device)


def launch(device: str) -> None:
    adb("shell", "am", "force-stop", PACKAGE, device=device)
    adb("shell", "am", "start", "-n", f"{PACKAGE}/.MainActivity", device=device)


def dump_ui(device: str) -> ET.Element:
    adb("shell", "uiautomator", "dump", "/sdcard/vfr_ui.xml", device=device)
    xml = adb("shell", "cat", "/sdcard/vfr_ui.xml", device=device).stdout
    return ET.fromstring(xml)


def find_center(root: ET.Element, *, text: str | None = None, desc: str | None = None) -> tuple[int, int] | None:
    for node in root.iter("node"):
        if text is not None and node.attrib.get("text") != text:
            continue
        if desc is not None and node.attrib.get("content-desc") != desc:
            continue
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.attrib.get("bounds", ""))
        if not m:
            continue
        x1, y1, x2, y2 = map(int, m.groups())
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    return None


def find_contains(root: ET.Element, needle: str) -> tuple[int, int] | None:
    for node in root.iter("node"):
        t = node.attrib.get("text", "")
        d = node.attrib.get("content-desc", "")
        if needle not in t and needle not in d:
            continue
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.attrib.get("bounds", ""))
        if not m:
            continue
        x1, y1, x2, y2 = map(int, m.groups())
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    return None


def screencap(device: str, out: Path) -> None:
    raw = subprocess.run(
        ["adb", "-s", device, "exec-out", "screencap", "-p"],
        check=True,
        capture_output=True,
    )
    out.write_bytes(raw.stdout)
    crop_status_bar(out)


def crop_status_bar(path: Path) -> None:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    top = STATUS_BAR_CROP_PX
    if h <= top + 200:
        return
    cropped = img.crop((0, top, w, h))
    cropped.save(path, optimize=True, quality=92)


def wake_and_unlock(device: str) -> None:
    import time

    adb("shell", "input", "keyevent", "224", device=device)
    time.sleep(0.5)
    adb("shell", "wm", "dismiss-keyguard", device=device)
    time.sleep(0.3)
    adb("shell", "input", "swipe", "540", "1800", "540", "800", "300", device=device)
    time.sleep(1)


def capture_launcher_widget(device: str) -> None:
    import time

    adb("shell", "input", "keyevent", "3", device=device)
    time.sleep(2)
    raw = subprocess.run(
        ["adb", "-s", device, "exec-out", "screencap", "-p"],
        check=True,
        capture_output=True,
    ).stdout
    tmp = ASSETS / "_launcher.png"
    tmp.write_bytes(raw)
    img = Image.open(tmp).convert("RGB")
    w, h = img.size
    widget = img.crop((56, 830, 822, 1787))
    widget.save(ASSETS / "screenshot-widget.png", optimize=True, quality=92)
    tmp.unlink(missing_ok=True)
    print(f"Saved screenshot-widget.png {widget.size}")


def wait(seconds: float, device: str) -> None:
    import time

    time.sleep(seconds)
    # dismiss transient overlays
    _ = dump_ui(device)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    device = pick_device()
    print(f"Using device {device}")
    wake_and_unlock(device)
    adb("reverse", "tcp:8081", "tcp:8081", device=device)
    launch(device)
    wait(12, device)

    root = dump_ui(device)

    # Bottom tabs — Search ~ center, Settings ~ right (1080x2300 typical)
    home_tab = find_contains(root, "Home") or (180, 2220)
    search_tab = find_contains(root, "Search") or (540, 2220)
    settings_tab = find_contains(root, "Settings") or (900, 2220)

    shots: list[tuple[str, callable]] = []

    # 1. Home / Favorites
    tap(device, *home_tab)
    wait(3, device)
    shots.append(("screenshot-home-favorites.png", lambda: None))

    screencap(device, ASSETS / shots[-1][0])
    print(f"Saved {shots[-1][0]}")

    # 2. Settings (personal minimums)
    tap(device, *settings_tab)
    wait(2, device)
    path = ASSETS / "screenshot-settings-minimums.png"
    screencap(device, path)
    print("Saved screenshot-settings-minimums.png")

    # 3. Widget preview (Settings → Widget; scroll to link first)
    tap(device, *settings_tab)
    wait(2, device)
    for _ in range(3):
        adb("shell", "input", "swipe", "540", "1700", "540", "700", "500", device=device)
        import time

        time.sleep(0.8)
    root = dump_ui(device)
    widget_link = find_contains(root, "Widget")
    if widget_link:
        tap(device, *widget_link)
        wait(4, device)
        root = dump_ui(device)
        raw = subprocess.run(
            ["adb", "-s", device, "exec-out", "screencap", "-p"],
            check=True,
            capture_output=True,
        ).stdout
        from io import BytesIO

        img = Image.open(BytesIO(raw)).convert("RGB")
        icao_bounds = []
        title_bounds = None
        for node in root.iter("node"):
            t = node.attrib.get("text", "")
            m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.attrib.get("bounds", ""))
            if not m:
                continue
            x1, y1, x2, y2 = map(int, m.groups())
            if re.fullmatch(r"K[A-Z0-9]{3}", t):
                icao_bounds.append((x1, y1, x2, y2))
            if t == "VFR Buddy":
                title_bounds = (x1, y1, x2, y2)
        if len(icao_bounds) >= 2:
            x1 = min(b[0] for b in icao_bounds) - 20
            y1 = (title_bounds[1] - 8 if title_bounds else min(b[1] for b in icao_bounds) - 80)
            x2 = max(b[2] for b in icao_bounds) + 120
            y2 = max(b[3] for b in icao_bounds) + 20
            widget = img.crop((max(0, x1), max(0, y1), min(img.width, x2), min(img.height, y2)))
            widget.save(ASSETS / "screenshot-widget.png", optimize=True, quality=92)
            print(f"Saved screenshot-widget.png {widget.size}")
        adb("shell", "input", "keyevent", "4", device=device)
        wait(1, device)

    tap(device, *home_tab)
    wait(2, device)

    # 4. Airport detail — tap first ICAO row
    tap(device, *home_tab)
    wait(2, device)
    root = dump_ui(device)
    icao_center = None
    for node in root.iter("node"):
        t = node.attrib.get("text", "")
        if re.fullmatch(r"K[A-Z0-9]{3}", t):
            m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.attrib.get("bounds", ""))
            if m:
                x1, y1, x2, y2 = map(int, m.groups())
                icao_center = ((x1 + x2) // 2, (y1 + y2) // 2)
                break
    if icao_center:
        tap(device, *icao_center)
        wait(3, device)
        screencap(device, ASSETS / "screenshot-airport-detail.png")
        print("Saved screenshot-airport-detail.png")
    else:
        print("Warning: no favorite ICAO found for detail screenshot", file=sys.stderr)

    print("Done.")


if __name__ == "__main__":
    main()
