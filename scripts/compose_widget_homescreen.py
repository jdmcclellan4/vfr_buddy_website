#!/usr/bin/env python3
"""Compose a full home-screen shot: aircraft wallpaper + widget + launcher icons."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
W, H = 1080, 2400
STATUS_CROP = 110

WALLPAPER = ASSETS / "aircraft-wallpaper.png"
EMULATOR = Path(
    r"C:\Users\jdmcc\.cursor\projects\c-Users-jdmcc-cursor-VFR-buddy\assets\c__Users_jdmcc_AppData_Roaming_Cursor_User_workspaceStorage_11552ccf61fbf25ce5a68abe20f5a517_images_image-3939f217-3d63-4e3b-a6f7-15a91c1046f4.png"
)
EMU_W, EMU_H = 394, 895

NAVY = (11, 31, 58)
CYAN = (43, 184, 200)
TEXT = (255, 255, 255)
SOFT = (207, 216, 220)
VFR_GREEN = (46, 125, 50)

MIDDLE_ICONS = [
    (118, 530, 184, 648),
    (210, 530, 276, 648),
    (302, 530, 368, 648),
]
DOCK_ICONS = [
    (28, 678, 94, 758),
    (120, 678, 186, 758),
    (212, 678, 278, 758),
    (304, 678, 370, 758),
]
SEARCH_PILL = (30, 790, 363, 839)
ICON_LIFT_EMU = 55

WIDGET_ROWS = [
    ("KRAL", "10SM CLR 25012"),
    ("KOSH", "10SM CLR 21003"),
    ("KVER", "10SM OVC110 10004"),
    ("KSTL", "10SM SCT065 07003"),
    ("KBAD", "10SM CLR 11008"),
]


def cover_resize(img: Image.Image, width: int, height: int) -> Image.Image:
    src_w, src_h = img.size
    scale = max(width / src_w, height / src_h)
    resized = img.resize((int(src_w * scale), int(src_h * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


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


def render_home_widget(width: int) -> Image.Image:
    """Render the compact Android home-screen widget (matches FavoritesWidget)."""
    pad = max(14, int(width * 0.038))
    row_h = max(54, int(width * 0.155))
    title_size = max(16, int(width * 0.042))
    icao_size = max(18, int(width * 0.048))
    summary_size = max(13, int(width * 0.034))
    badge_size = max(12, int(width * 0.032))
    radius = max(14, int(width * 0.042))

    title_font = load_font(title_size, bold=True)
    icao_font = load_font(icao_size, bold=True)
    summary_font = load_font(summary_size)
    badge_font = load_font(badge_size, bold=True)

    height = pad * 2 + title_size + 10 + len(WIDGET_ROWS) * row_h
    widget = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(widget)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=NAVY + (255,))

    draw.text((pad, pad), "VFR Buddy", fill=CYAN, font=title_font)

    y = pad + title_size + 10
    for icao, summary in WIDGET_ROWS:
        draw.text((pad, y), icao, fill=TEXT, font=icao_font)
        draw.text((pad, y + icao_size + 2), summary, fill=SOFT, font=summary_font)

        badge_text = "VFR"
        badge_w = int(width * 0.17)
        badge_h = int(width * 0.085)
        bx = width - pad - badge_w
        by = y + 4
        draw.rounded_rectangle(
            (bx, by, bx + badge_w, by + badge_h),
            radius=8,
            fill=VFR_GREEN + (255,),
        )
        bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            (bx + (badge_w - tw) // 2, by + (badge_h - th) // 2 - 1),
            badge_text,
            fill=TEXT,
            font=badge_font,
        )
        y += row_h

    return widget


def paste_full_icon(
    canvas: Image.Image,
    source: Image.Image,
    crop: tuple[int, int, int, int],
    *,
    center_x_emu: float,
    top_y_emu: float,
    target_width: int,
) -> None:
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


def paste_search_bar(canvas: Image.Image, emulator: Image.Image) -> None:
    sy = (H - STATUS_CROP) / EMU_H
    dest_w = int(W * 0.9)
    dest_h = max(56, int((SEARCH_PILL[3] - SEARCH_PILL[1]) * sy))
    dest_x = (W - dest_w) // 2
    dest_y = int(SEARCH_PILL[1] * sy) + STATUS_CROP

    pill = Image.new("RGBA", (dest_w, dest_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(pill)
    draw.rounded_rectangle((0, 0, dest_w - 1, dest_h - 1), radius=dest_h // 2, fill=(255, 255, 255, 255))
    canvas.alpha_composite(pill, (dest_x, dest_y))

    content = key_dark(emulator.crop(SEARCH_PILL), threshold=55)
    content = content.resize((dest_w, dest_h), Image.Resampling.LANCZOS)
    canvas.alpha_composite(content, (dest_x, dest_y))


def main() -> None:
    wallpaper = Image.open(WALLPAPER).convert("RGB")
    emulator = Image.open(EMULATOR).convert("RGBA")

    base = cover_resize(wallpaper, W, H).convert("RGBA")

    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(scrim)
    for y in range(int(H * 0.45), H):
        alpha = int(130 * ((y - H * 0.45) / (H * 0.55)) ** 1.3)
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    base = Image.alpha_composite(base, scrim)
    canvas = base.copy()

    widget_w = int(W * 0.42)
    widget = render_home_widget(widget_w)
    wx, wy = int(W * 0.06), STATUS_CROP + int((H - STATUS_CROP) * 0.035)
    shadow = Image.new("RGBA", (widget_w + 24, widget.height + 24), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((12, 12, widget_w + 12, widget.height + 12), radius=24, fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    canvas.alpha_composite(shadow, (wx - 12, wy - 8))
    canvas.alpha_composite(widget, (wx, wy))

    icon_w = int(66 * emu_scale())
    middle_y = 530 - ICON_LIFT_EMU
    dock_y = 678 - ICON_LIFT_EMU
    for crop in MIDDLE_ICONS:
        cx, _ = emu_center(crop)
        paste_full_icon(canvas, emulator, crop, center_x_emu=cx, top_y_emu=middle_y, target_width=icon_w)
    for crop in DOCK_ICONS:
        cx, _ = emu_center(crop)
        paste_full_icon(canvas, emulator, crop, center_x_emu=cx, top_y_emu=dock_y, target_width=icon_w)

    paste_search_bar(canvas, emulator)

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
    widget.save(ASSETS / "screenshot-widget-card.png", optimize=True, quality=92)
    print(f"Saved screenshot-widget-homescreen.png {out.size}")


if __name__ == "__main__":
    main()
