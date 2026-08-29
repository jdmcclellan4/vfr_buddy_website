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

# Measured from the 394x895 emulator reference image
MIDDLE_ICONS = [
    (118, 530, 184, 648),   # Gmail
    (210, 530, 276, 648),   # Photos
    (302, 530, 368, 648),   # YouTube
]
DOCK_ICONS = [
    (28, 678, 94, 758),     # Phone
    (120, 678, 186, 758),   # Messages
    (212, 678, 278, 758),   # Chrome
    (304, 678, 370, 758),   # VFR Buddy
]
SEARCH_BAR = (16, 784, 378, 858)


def cover_resize(img: Image.Image, width: int, height: int) -> Image.Image:
    src_w, src_h = img.size
    scale = max(width / src_w, height / src_h)
    resized = img.resize((int(src_w * scale), int(src_h * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def key_dark(img: Image.Image, threshold: int = 34) -> Image.Image:
    rgba = img.convert("RGBA")
    pixels = rgba.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if r < threshold and g < threshold and b < threshold:
                pixels[x, y] = (0, 0, 0, 0)
    return rgba


def paste_crop(
    canvas: Image.Image,
    source: Image.Image,
    crop: tuple[int, int, int, int],
    dest: tuple[int, int, int, int],
    *,
    keyed: bool = True,
) -> None:
    piece = source.crop(crop)
    if keyed:
        piece = key_dark(piece)
    piece = piece.resize((dest[2] - dest[0], dest[3] - dest[1]), Image.Resampling.LANCZOS)
    canvas.alpha_composite(piece, (dest[0], dest[1]))


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

    row_y = int(H * 0.57)
    icon_w = int(W * 0.19)
    icon_h = int(icon_w * 1.28)
    gap = int(W * 0.075)
    start_x = (W - (3 * icon_w + 2 * gap)) // 2
    for i, crop in enumerate(MIDDLE_ICONS):
        dest = (start_x + i * (icon_w + gap), row_y, start_x + i * (icon_w + gap) + icon_w, row_y + icon_h)
        paste_crop(canvas, emulator, crop, dest)

    dock_y = int(H * 0.775)
    dock_icon = int(W * 0.145)
    dock_gap = int(W * 0.04)
    dock_start = (W - (4 * dock_icon + 3 * dock_gap)) // 2
    for i, crop in enumerate(DOCK_ICONS):
        dest = (
            dock_start + i * (dock_icon + dock_gap),
            dock_y,
            dock_start + i * (dock_icon + dock_gap) + dock_icon,
            dock_y + dock_icon,
        )
        paste_crop(canvas, emulator, crop, dest, keyed=False)

    search_h = int(W * 0.135)
    search_y = int(H * 0.885)
    search_w = int(W * 0.9)
    search_x = (W - search_w) // 2
    paste_crop(
        canvas,
        emulator,
        SEARCH_BAR,
        (search_x, search_y, search_x + search_w, search_y + search_h),
        keyed=False,
    )

    pill = ImageDraw.Draw(canvas)
    pill_w, pill_h = 220, 10
    pill.rounded_rectangle(
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
