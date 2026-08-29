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

# Icon circle + label regions on the 394x895 emulator reference
MIDDLE_ICON_CIRCLES = [
    (118, 530, 184, 596),
    (210, 530, 276, 596),
    (302, 530, 368, 596),
]
MIDDLE_LABELS = [
    (118, 596, 184, 648),
    (210, 596, 276, 648),
    (302, 596, 368, 648),
]
DOCK_ICON_CIRCLES = [
    (28, 678, 94, 744),
    (120, 678, 186, 744),
    (212, 678, 278, 744),
    (304, 678, 370, 744),
]
SEARCH_BAR = (16, 784, 378, 858)


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


def paste_square_icon(
    canvas: Image.Image,
    source: Image.Image,
    crop: tuple[int, int, int, int],
    center_x: int,
    top_y: int,
    size: int,
) -> None:
    piece = key_dark(source.crop(crop))
    piece = piece.resize((size, size), Image.Resampling.LANCZOS)
    x = center_x - size // 2
    canvas.alpha_composite(piece, (x, top_y))


def paste_label(
    canvas: Image.Image,
    source: Image.Image,
    crop: tuple[int, int, int, int],
    center_x: int,
    top_y: int,
    width: int,
    height: int,
) -> None:
    piece = key_dark(source.crop(crop))
    piece = piece.resize((width, height), Image.Resampling.LANCZOS)
    x = center_x - width // 2
    canvas.alpha_composite(piece, (x, top_y))


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

    icon_size = int(W * 0.118)
    label_h = int(icon_size * 0.34)
    label_w = int(icon_size * 1.15)
    icon_gap = int(W * 0.095)

    # Middle row — 3 icons, same circle size as dock
    middle_count = 3
    middle_span = middle_count * icon_size + (middle_count - 1) * icon_gap
    middle_start = (W - middle_span) // 2 + icon_size // 2
    middle_y = int(H * 0.555)
    label_y = middle_y + icon_size + int(icon_size * 0.08)

    for i, (icon_crop, label_crop) in enumerate(zip(MIDDLE_ICON_CIRCLES, MIDDLE_LABELS, strict=True)):
        cx = middle_start + i * (icon_size + icon_gap)
        paste_square_icon(canvas, emulator, icon_crop, cx, middle_y, icon_size)
        paste_label(canvas, emulator, label_crop, cx, label_y, label_w, label_h)

    # Dock — 4 icons, identical circle size
    dock_count = 4
    dock_span = dock_count * icon_size + (dock_count - 1) * icon_gap
    dock_start = (W - dock_span) // 2 + icon_size // 2
    dock_y = int(H * 0.745)

    for i, icon_crop in enumerate(DOCK_ICON_CIRCLES):
        cx = dock_start + i * (icon_size + icon_gap)
        paste_square_icon(canvas, emulator, icon_crop, cx, dock_y, icon_size)

    # Search bar — white pill background + keyed contents
    search_w = int(W * 0.9)
    search_h = int(W * 0.128)
    search_x = (W - search_w) // 2
    search_y = int(H * 0.868)
    pill_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pill_draw = ImageDraw.Draw(pill_layer)
    pill_draw.rounded_rectangle(
        (search_x, search_y, search_x + search_w, search_y + search_h),
        radius=search_h // 2,
        fill=(255, 255, 255, 248),
    )
    canvas = Image.alpha_composite(canvas, pill_layer)

    search_inner = key_dark(emulator.crop(SEARCH_BAR))
    inner_scale = min((search_w - 24) / search_inner.width, (search_h - 12) / search_inner.height)
    inner_w = max(1, int(search_inner.width * inner_scale))
    inner_h = max(1, int(search_inner.height * inner_scale))
    search_inner = search_inner.resize((inner_w, inner_h), Image.Resampling.LANCZOS)
    canvas.alpha_composite(
        search_inner,
        (search_x + (search_w - inner_w) // 2, search_y + (search_h - inner_h) // 2),
    )

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
