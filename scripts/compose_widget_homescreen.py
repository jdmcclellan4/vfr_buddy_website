#!/usr/bin/env python3
"""Compose a full home-screen shot: aircraft wallpaper + widget + launcher icons."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
W, H = 1080, 2400
STATUS_CROP = 110

WALLPAPER = ASSETS / "aircraft-wallpaper.png"
EMULATOR = Path(
    r"C:\Users\jdmcc\.cursor\projects\c-Users-jdmcc-cursor-VFR-buddy\assets\c__Users_jdmcc_AppData_Roaming_Cursor_User_workspaceStorage_11552ccf61fbf25ce5a68abe20f5a517_images_image-3939f217-3d63-4e3b-a6f7-15a91c1046f4.png"
)
EMU_W, EMU_H = 394, 895

# Full icon crops from emulator — never split or trim
MIDDLE_ICONS = [
    (118, 530, 184, 648),   # Gmail + label
    (210, 530, 276, 648),   # Photos + label
    (302, 530, 368, 648),   # YouTube + label
]
DOCK_ICONS = [
    (28, 678, 94, 758),     # Phone
    (120, 678, 186, 758),   # Messages
    (212, 678, 278, 758),   # Chrome
    (304, 678, 370, 758),   # VFR Buddy
]
SEARCH_BAR = (16, 784, 378, 858)
# White pill only — excludes black wallpaper margins in the search crop
SEARCH_PILL = (30, 790, 363, 839)
# Raise icon rows above the search bar (emu pixels)
ICON_LIFT_EMU = 55


def cover_resize(img: Image.Image, width: int, height: int) -> Image.Image:
    src_w, src_h = img.size
    scale = max(width / src_w, height / src_h)
    resized = img.resize((int(src_w * scale), int(src_h * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def key_dark(img: Image.Image, threshold: int = 42) -> Image.Image:
    rgba = img.convert("RGBA")
    pixels = rgba.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if max(r, g, b) < threshold:
                pixels[x, y] = (0, 0, 0, 0)
    return rgba


def emu_scale() -> float:
    return W / EMU_W


def emu_center(box: tuple[int, int, int, int]) -> tuple[int, int]:
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def paste_full_icon(
    canvas: Image.Image,
    source: Image.Image,
    crop: tuple[int, int, int, int],
    *,
    center_x_emu: float,
    top_y_emu: float,
    target_width: int,
) -> None:
    """Paste the full emulator crop scaled uniformly; same icon width for every app."""
    piece = key_dark(source.crop(crop))
    src_w = crop[2] - crop[0]
    src_h = crop[3] - crop[1]
    scale = target_width / src_w
    new_w = max(1, int(src_w * scale))
    new_h = max(1, int(src_h * scale))
    piece = piece.resize((new_w, new_h), Image.Resampling.LANCZOS)

    s = emu_scale()
    cx = int(center_x_emu * s)
    top = int(top_y_emu * s) + STATUS_CROP
    canvas.alpha_composite(piece, (cx - new_w // 2, top))


def main() -> None:
    wallpaper = Image.open(WALLPAPER).convert("RGB")
    emulator = Image.open(EMULATOR).convert("RGBA")
    widget = Image.open(ASSETS / "screenshot-widget-card.png").convert("RGBA")

    base = cover_resize(wallpaper, W, H).convert("RGBA")

    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(scrim)
    for y in range(int(H * 0.45), H):
        alpha = int(130 * ((y - H * 0.45) / (H * 0.55)) ** 1.3)
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    base = Image.alpha_composite(base, scrim)
    canvas = base.copy()

    widget_w = int(W * 0.47)
    widget_h = int(widget.size[1] * (widget_w / widget.size[0]))
    widget_resized = widget.resize((widget_w, widget_h), Image.Resampling.LANCZOS)
    wx, wy = int(W * 0.05), STATUS_CROP + int((H - STATUS_CROP) * 0.04)
    shadow = Image.new("RGBA", (widget_w + 28, widget_h + 28), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((14, 14, widget_w + 14, widget_h + 14), radius=30, fill=(0, 0, 0, 130))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    canvas.alpha_composite(shadow, (wx - 14, wy - 10))
    canvas.alpha_composite(widget_resized, (wx, wy))

    icon_w = int(66 * emu_scale())

    # Layout mirrors the emulator reference, lifted above the search bar
    middle_y = 530 - ICON_LIFT_EMU
    dock_y = 678 - ICON_LIFT_EMU
    for crop in MIDDLE_ICONS:
        cx, _ = emu_center(crop)
        paste_full_icon(canvas, emulator, crop, center_x_emu=cx, top_y_emu=middle_y, target_width=icon_w)

    for crop in DOCK_ICONS:
        cx, _ = emu_center(crop)
        paste_full_icon(canvas, emulator, crop, center_x_emu=cx, top_y_emu=dock_y, target_width=icon_w)

    # Search bar — white pill only, scaled to full width (no black margins)
    sy = (H - STATUS_CROP) / EMU_H
    pill_h = int((SEARCH_PILL[3] - SEARCH_PILL[1]) * sy)
    dest_w = int(W * 0.9)
    dest_x = (W - dest_w) // 2
    dest_y = int(SEARCH_PILL[1] * sy) + STATUS_CROP
    search = emulator.crop(SEARCH_PILL).resize((dest_w, pill_h), Image.Resampling.LANCZOS)
    canvas.alpha_composite(search.convert("RGBA"), (dest_x, dest_y))

    nav = ImageDraw.Draw(canvas)
    pill_w, pill_h = 220, 10
    nav.rounded_rectangle(
        ((W - pill_w) // 2, H - 34, (W + pill_w) // 2, H - 34 + pill_h),
        radius=5,
        fill=(255, 255, 255, 220),
    )

    out = canvas.convert("RGB").crop((0, STATUS_CROP, W, H))
    out.save(ASSETS / "screenshot-widget-homescreen.png", optimize=True, quality=92)
    out.save(ASSETS / "screenshot-widget.png", optimize=True, quality=92)
    print(f"Saved screenshot-widget-homescreen.png {out.size}")


if __name__ == "__main__":
    main()
