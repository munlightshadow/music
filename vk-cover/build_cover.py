#!/usr/bin/env python3
"""Build the brand palette board and the 1920x768 VK community cover."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS_LIGHTHOUSE = Path("/opt/cursor/artifacts/assets/vk-cover-sea-lighthouse.png")
FALLBACK_LIGHTHOUSE = Path("/tmp/lighthouse-extract.png")
FONTS = ROOT / "fonts"
FONT_EXTRABOLD = str(FONTS / "Montserrat-ExtraBold.ttf")
FONT_BOLD = str(FONTS / "Montserrat-Bold.ttf")
FONT_MEDIUM = str(FONTS / "Montserrat-Medium.ttf")

W, H = 1920, 768


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)


PALETTE = json.loads((ROOT / "palette.json").read_text(encoding="utf-8"))
C = {key: hex_to_rgb(item["hex"]) for key, item in PALETTE["colors"].items()}


def lerp(a, b, t):
    t = np.clip(t, 0.0, 1.0)
    return (1.0 - t) * np.asarray(a, dtype=np.float32) + t * np.asarray(b, dtype=np.float32)


def build_palette_board() -> Image.Image:
    cols, rows = 5, 2
    sw, sh = 280, 200
    pad, gap = 36, 20
    board_w = pad * 2 + cols * sw + (cols - 1) * gap
    board_h = pad * 2 + rows * sh + gap + 72
    img = Image.new("RGB", (board_w, board_h), C["teal_deep"])
    draw = ImageDraw.Draw(img)
    try:
        label_font = ImageFont.truetype(FONT_MEDIUM, 22)
        title_font = ImageFont.truetype(FONT_BOLD, 28)
    except OSError:
        label_font = ImageFont.load_default()
        title_font = label_font

    draw.text((pad, 18), "Английский маяк — палитра логотипа", font=title_font, fill=C["white"])

    swatches = [
        ("#214149", C["dark_teal"], None),
        ("#A5D2DF", C["light_pastel_blue"], None),
        ("#468A9D", C["medium_teal"], None),
        ("#494F55", C["charcoal"], None),
        ("#A8B2BB", C["steel"], None),
        ("#C19B4F", C["muted_gold"], None),
        ("#FFFFFF", C["white"], None),
        ("#C19B4F  →  #F3D593", None, (C["muted_gold"], C["gold_light"])),
        ("#488DA0  →  #1A333A", None, (C["teal_horizon"], C["teal_deep"])),
    ]

    for i, (label, solid, gradient) in enumerate(swatches):
        r, c = divmod(i, cols)
        x = pad + c * (sw + gap)
        y = pad + 52 + r * (sh + gap)
        tile = Image.new("RGB", (sw, sh), solid or C["teal_deep"])
        if gradient:
            top, bot = gradient
            arr = np.zeros((sh, sw, 3), dtype=np.float32)
            for yy in range(sh):
                t = yy / (sh - 1)
                arr[yy] = lerp(top, bot, t)
            tile = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
        img.paste(tile, (x, y))

        sample = np.array(tile)[sh // 2, sw // 2]
        luminance = 0.2126 * sample[0] + 0.7152 * sample[1] + 0.0722 * sample[2]
        fill = C["teal_deep"] if luminance > 160 else C["white"]
        bbox = draw.textbbox((0, 0), label, font=label_font)
        tw = bbox[2] - bbox[0]
        draw.text((x + (sw - tw) // 2, y + sh - 40), label, font=label_font, fill=fill)

    return img


def extract_lighthouse() -> Image.Image:
    if ASSETS_LIGHTHOUSE.exists():
        src = Image.open(ASSETS_LIGHTHOUSE).convert("RGB")
        src_arr = np.array(src)
        rgb = src_arr.astype(np.int16)
        brightness = rgb.mean(axis=2)
        keep = (brightness > 70) | (
            (rgb[:, :, 0] > 140) & (rgb[:, :, 1] > 90) & (rgb[:, :, 0] > rgb[:, :, 2] + 20)
        )
        x0, y0, x1, y1 = 1040, 520, 1520, 1008
        crop_rgb = src_arr[y0:y1, x0:x1]
        crop_keep = keep[y0:y1, x0:x1]
        alpha_img = Image.fromarray((crop_keep.astype(np.uint8) * 255), "L")
        alpha_img = alpha_img.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(5))
        alpha_arr = np.array(alpha_img).astype(np.float32)
        crop = crop_rgb.astype(np.int16)
        is_sea = (crop.mean(axis=2) < 58) & ~(
            (crop[:, :, 0] > 115) & (crop[:, :, 0] > crop[:, :, 2] + 12)
        )
        alpha_arr[is_sea] *= 0.05
        lh = Image.fromarray(crop_rgb, "RGB").convert("RGBA")
        lh.putalpha(Image.fromarray(np.clip(alpha_arr, 0, 255).astype(np.uint8), "L"))
        bbox = lh.getbbox()
        lh = lh.crop(bbox)
    else:
        lh = Image.open(FALLBACK_LIGHTHOUSE).convert("RGBA")

    # Recolor: body → white, beams → gold gradient from the logo palette
    arr = np.array(lh).astype(np.float32)
    rgb, alpha = arr[:, :, :3], arr[:, :, 3]
    brightness = rgb.mean(axis=2)
    gold_mask = (
        (rgb[:, :, 0] > 140)
        & (rgb[:, :, 1] > 90)
        & (rgb[:, :, 0] > rgb[:, :, 2] + 15)
        & (alpha > 40)
    )
    white_mask = (brightness > 170) & (alpha > 80) & ~gold_mask

    gold_t = np.clip((brightness - 140) / 90.0, 0.0, 1.0)
    gold_color = lerp(C["muted_gold"], C["gold_light"], gold_t[:, :, None])
    rgb[gold_mask] = gold_color[gold_mask]
    rgb[white_mask] = np.array(C["white"], dtype=np.float32)

    # Dark window cutouts → dark teal from the palette
    window = (brightness < 90) & (alpha > 160) & ~gold_mask
    rgb[window] = np.array(C["dark_teal"], dtype=np.float32)

    out = np.dstack([np.clip(rgb, 0, 255), np.clip(alpha, 0, 255)]).astype(np.uint8)
    lh = Image.fromarray(out, "RGBA")
    target_h = 290
    scale = target_h / lh.height
    return lh.resize((max(1, int(lh.width * scale)), target_h), Image.Resampling.LANCZOS)


def build_sea() -> Image.Image:
    yy = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
    xx = np.linspace(0.0, 1.0, W, dtype=np.float32)[None, :]

    # Logo sea gradient: #488DA0 (top) → #214149 (mid) → #1A333A (bottom)
    col = np.zeros((H, W, 3), dtype=np.float32)
    mid_stop = 0.48
    t = yy[:, 0]
    top = np.array(C["teal_horizon"], dtype=np.float32)
    mid = np.array(C["dark_teal"], dtype=np.float32)
    bot = np.array(C["teal_deep"], dtype=np.float32)
    for i, ti in enumerate(t):
        if ti < mid_stop:
            col[i] = lerp(top, mid, ti / mid_stop)
        else:
            col[i] = lerp(mid, bot, (ti - mid_stop) / (1.0 - mid_stop))

    # Soft center lift using medium teal, vignette handled below
    cx, cy = 0.46, 0.36
    r = np.sqrt(((xx - cx) * 1.2) ** 2 + ((yy - cy) * 1.55) ** 2)
    lift = np.clip(1.0 - r / 0.95, 0.0, 1.0) ** 1.4
    medium = np.array(C["medium_teal"], dtype=np.float32)
    lift3 = lift[:, :, None]
    col = col * (1.0 - 0.12 * lift3) + medium * (0.12 * lift3)

    # Vignette stays on-palette: lerp toward deep teal instead of multiplying toward black
    vign_t = np.clip((r - 0.18) / 1.05, 0.0, 1.0) ** 1.15
    deep = np.array(C["teal_deep"], dtype=np.float32)
    col = col * (1.0 - 0.28 * vign_t[:, :, None]) + deep * (0.28 * vign_t[:, :, None])

    # Faint horizon using light pastel blue — very subtle, still on-palette
    horizon = np.exp(-((yy - 0.58) ** 2) / (2 * 0.018 ** 2))
    pastel = np.array(C["light_pastel_blue"], dtype=np.float32)
    col = col * (1.0 - 0.07 * horizon[:, :, None]) + pastel * (0.07 * horizon[:, :, None])

    # Calm water bands
    for amp, freq, phase, yband in (
        (1.0, 1.7, 0.0, 0.80),
        (0.7, 2.6, 1.1, 0.87),
        (0.5, 3.3, 2.0, 0.93),
    ):
        wave = (np.sin((xx * freq + phase) * np.pi * 2) * 0.5 + 0.5) * amp
        band = np.exp(-((yy - yband) ** 2) / 0.005)
        mix = np.clip(wave * band * 0.045, 0, 1)
        col = col * (1.0 - mix[:, :, None]) + medium * mix[:, :, None]

    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB")


def draw_cover_text(canvas: Image.Image, lighthouse_left: int) -> None:
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype(FONT_EXTRABOLD, 88)
    sub_font = ImageFont.truetype(FONT_BOLD, 50)
    white = (*C["white"], 255)
    shadow = (*C["teal_deep"], 160)

    def draw_line(text: str, y: int, font) -> int:
        b = font.getbbox(text)
        tw, th = b[2] - b[0], b[3] - b[1]
        x = (W - tw) // 2
        if x + tw > lighthouse_left - 36:
            x = lighthouse_left - 36 - tw
        for dx, dy in ((0, 3), (3, 3)):
            draw.text((x + dx, y + dy), text, font=font, fill=shadow)
        draw.text((x, y), text, font=font, fill=white)
        return th

    y = 200
    y += draw_line("Английский маяк:", y, title_font)
    y += 56  # a bit more space between the title and the second line
    draw_line("подготовка к ОГЭ и ЕГЭ по английскому языку", y, sub_font)


def build_cover() -> Image.Image:
    sea = build_sea().convert("RGBA")
    lh = extract_lighthouse()
    pad_r, pad_b = 56, 22
    lx = W - lh.width - pad_r
    ly = H - lh.height - pad_b
    sea.alpha_composite(lh, (lx, ly))
    draw_cover_text(sea, lx)
    out = sea.convert("RGB")
    assert out.size == (W, H)
    return out


def main() -> None:
    board = build_palette_board()
    board.save(ROOT / "palette.png", "PNG", optimize=True)

    cover = build_cover()
    cover.save(ROOT / "angliyskiy-mayak-1920x768.png", "PNG", optimize=True)
    cover.save(ROOT / "angliyskiy-mayak-1920x768.jpg", "JPEG", quality=95, optimize=True, subsampling=1)

    artifacts = Path("/opt/cursor/artifacts")
    artifacts.mkdir(parents=True, exist_ok=True)
    cover.save(artifacts / "angliyskiy-mayak-1920x768.png", "PNG")
    cover.save(artifacts / "angliyskiy-mayak-1920x768.jpg", "JPEG", quality=95)
    board.save(artifacts / "palette.png", "PNG")
    print("wrote palette and cover", cover.size)


if __name__ == "__main__":
    main()
