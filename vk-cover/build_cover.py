#!/usr/bin/env python3
"""Build the brand memo, palette board, and the 1920x768 VK community cover."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS_LIGHTHOUSE = Path("/opt/cursor/artifacts/assets/vk-cover-sea-lighthouse.png")
FALLBACK_LIGHTHOUSE = Path("/tmp/lighthouse-extract.png")
FONTS = ROOT / "fonts"
FONT_TITLE = str(FONTS / "SofiaSansCondensed.ttf")
FONT_BODY = str(FONTS / "OpenSans.ttf")

W, H = 1920, 768
TITLE_TEXT = "Английский маяк:"
SUBTITLE_TEXT = "подготовка к ОГЭ и ЕГЭ по английскому языку"


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)


PALETTE = json.loads((ROOT / "palette.json").read_text(encoding="utf-8"))
C = {key: hex_to_rgb(item["hex"]) for key, item in PALETTE["colors"].items()}


def lerp(a, b, t):
    t = np.clip(t, 0.0, 1.0)
    return (1.0 - t) * np.asarray(a, dtype=np.float32) + t * np.asarray(b, dtype=np.float32)


def load_font(path: str, size: int, variation: str) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(path, size)
    font.set_variation_by_name(variation)
    return font


def ink_width(font: ImageFont.FreeTypeFont, text: str) -> int:
    b = font.getbbox(text)
    return b[2] - b[0]


def centered_x(cx: float, font: ImageFont.FreeTypeFont, text: str) -> int:
    """X so the visual ink of `text` is centered on cx."""
    b = font.getbbox(text)
    return int(round(cx - (b[0] + b[2]) / 2))


def build_palette_board() -> Image.Image:
    cols, rows = 5, 2
    sw, sh = 280, 200
    pad, gap = 36, 20
    board_w = pad * 2 + cols * sw + (cols - 1) * gap
    board_h = pad * 2 + rows * sh + gap + 72
    img = Image.new("RGB", (board_w, board_h), C["teal_deep"])
    draw = ImageDraw.Draw(img)
    label_font = load_font(FONT_BODY, 20, "Regular")
    title_font = load_font(FONT_TITLE, 32, "Bold")

    draw.text((pad, 16), "Английский маяк — палитра логотипа", font=title_font, fill=C["white"])

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
                arr[yy] = lerp(top, bot, yy / (sh - 1))
            tile = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
        img.paste(tile, (x, y))

        sample = np.array(tile)[sh // 2, sw // 2]
        luminance = 0.2126 * sample[0] + 0.7152 * sample[1] + 0.0722 * sample[2]
        fill = C["teal_deep"] if luminance > 160 else C["white"]
        bbox = draw.textbbox((0, 0), label, font=label_font)
        tw = bbox[2] - bbox[0]
        draw.text((x + (sw - tw) // 2, y + sh - 38), label, font=label_font, fill=fill)

    return img


def rounded_rect(draw: ImageDraw.ImageDraw, box, fill, radius=18):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def build_memo() -> Image.Image:
    """Brand memo: fonts + palette + cover rules."""
    mw, mh = 1600, 2100
    img = Image.new("RGB", (mw, mh), C["teal_deep"])
    draw = ImageDraw.Draw(img)

    title_xl = load_font(FONT_TITLE, 72, "ExtraBold")
    title_md = load_font(FONT_TITLE, 36, "Bold")
    title_sm = load_font(FONT_TITLE, 28, "Bold")
    body = load_font(FONT_BODY, 22, "Regular")
    body_lg = load_font(FONT_BODY, 28, "Regular")
    caption = load_font(FONT_BODY, 18, "Regular")
    sample_title = load_font(FONT_TITLE, 64, "ExtraBold")
    sample_body = load_font(FONT_BODY, 32, "Regular")

    pad = 56
    y = 48
    draw.text((pad, y), "Английский маяк", font=title_xl, fill=C["white"])
    y += 86
    draw.text((pad, y), "Памятка: шрифты и палитра", font=body_lg, fill=C["light_pastel_blue"])
    y += 56
    draw.rectangle((pad, y, mw - pad, y + 3), fill=C["muted_gold"])
    y += 36

    # --- Fonts ---
    draw.text((pad, y), "ШРИФТЫ", font=title_sm, fill=C["gold_light"])
    y += 48

    cards = [
        {
            "kicker": "Большой — для названия",
            "name": "Sofia Sans Condensed",
            "meta": "Начертание ExtraBold · заголовок обложки, логотип",
            "sample": "Английский маяк",
            "sample_font": sample_title,
        },
        {
            "kicker": "Маленький — для пояснения",
            "name": "Open Sans",
            "meta": "Начертание Regular · подзаголовок, описания",
            "sample": "подготовка к ОГЭ и ЕГЭ по английскому языку",
            "sample_font": sample_body,
        },
    ]
    card_h = 210
    for card in cards:
        rounded_rect(draw, (pad, y, mw - pad, y + card_h), C["dark_teal"], 20)
        draw.text((pad + 36, y + 22), card["kicker"], font=caption, fill=C["gold_light"])
        draw.text((pad + 36, y + 52), card["name"], font=title_md, fill=C["white"])
        draw.text((pad + 36, y + 98), card["meta"], font=caption, fill=C["steel"])
        draw.text((pad + 36, y + 136), card["sample"], font=card["sample_font"], fill=C["white"])
        y += card_h + 20

    y += 16
    draw.text((pad, y), "ПАЛИТРА ЛОГОТИПА", font=title_sm, fill=C["gold_light"])
    y += 48

    swatches = [
        ("#214149", "Тёмный бирюзовый", "логотип, середина моря", C["dark_teal"], None),
        ("#A5D2DF", "Светло-голубой", "блик, светлый акцент", C["light_pastel_blue"], None),
        ("#468A9D", "Средний бирюзовый", "вода, второй цвет", C["medium_teal"], None),
        ("#494F55", "Угольно-серый", "текст на светлом", C["charcoal"], None),
        ("#A8B2BB", "Стальной", "второстепенный текст", C["steel"], None),
        ("#C19B4F", "Золото", "лучи маяка", C["muted_gold"], None),
        ("#FFFFFF", "Белый", "текст и башня маяка", C["white"], None),
        ("#C19B4F → #F3D593", "Градиент золота", "свечение фонаря", None, (C["muted_gold"], C["gold_light"])),
        ("#488DA0 → #1A333A", "Градиент моря", "фон обложки ВК", None, (C["teal_horizon"], C["teal_deep"])),
    ]
    cols = 3
    sw, sh, gap = 480, 118, 18
    for i, (hex_label, name, usage, solid, gradient) in enumerate(swatches):
        r, c = divmod(i, cols)
        x = pad + c * (sw + gap)
        yy = y + r * (sh + gap)
        box = (x, yy, x + sw, yy + sh)
        if gradient:
            tile = Image.new("RGB", (sw, sh), C["teal_deep"])
            arr = np.zeros((sh, sw, 3), dtype=np.float32)
            for row in range(sh):
                arr[row] = lerp(gradient[0], gradient[1], row / (sh - 1))
            tile = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
            img.paste(tile, (x, yy))
        else:
            draw.rectangle(box, fill=solid)
        sample_rgb = gradient[0] if gradient else solid
        lum = 0.2126 * sample_rgb[0] + 0.7152 * sample_rgb[1] + 0.0722 * sample_rgb[2]
        fill = C["teal_deep"] if lum > 165 else C["white"]
        subfill = C["charcoal"] if lum > 165 else C["steel"]
        draw.text((x + 18, yy + 16), name, font=load_font(FONT_TITLE, 24, "Bold"), fill=fill)
        draw.text((x + 18, yy + 48), hex_label, font=caption, fill=fill)
        draw.text((x + 18, yy + 76), usage, font=caption, fill=subfill)

    y += 3 * (sh + gap) + 12
    draw.text((pad, y), "ОБЛОЖКА ВК", font=title_sm, fill=C["gold_light"])
    y += 44
    rounded_rect(draw, (pad, y, mw - pad, y + 220), C["dark_teal"], 20)
    rules = [
        "Размер: 1920 × 768 px · формат PNG или JPG",
        "Название: Sofia Sans Condensed ExtraBold, белый #FFFFFF",
        "Подзаголовок: Open Sans Regular, белый #FFFFFF",
        "Выравнивание: «Английский маяк» ровно по центру над «подготовка…»",
        "Фон: море #488DA0 → #214149 → #1A333A · маяк справа снизу, лучи #C19B4F",
    ]
    ry = y + 24
    for line in rules:
        draw.text((pad + 36, ry), "·  " + line, font=body, fill=C["white"])
        ry += 36

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

    cx, cy = 0.46, 0.36
    r = np.sqrt(((xx - cx) * 1.2) ** 2 + ((yy - cy) * 1.55) ** 2)
    lift = np.clip(1.0 - r / 0.95, 0.0, 1.0) ** 1.4
    medium = np.array(C["medium_teal"], dtype=np.float32)
    lift3 = lift[:, :, None]
    col = col * (1.0 - 0.12 * lift3) + medium * (0.12 * lift3)

    vign_t = np.clip((r - 0.18) / 1.05, 0.0, 1.0) ** 1.15
    deep = np.array(C["teal_deep"], dtype=np.float32)
    col = col * (1.0 - 0.28 * vign_t[:, :, None]) + deep * (0.28 * vign_t[:, :, None])

    horizon = np.exp(-((yy - 0.58) ** 2) / (2 * 0.018 ** 2))
    pastel = np.array(C["light_pastel_blue"], dtype=np.float32)
    col = col * (1.0 - 0.07 * horizon[:, :, None]) + pastel * (0.07 * horizon[:, :, None])

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
    title_font = load_font(FONT_TITLE, 96, "ExtraBold")
    sub_font = load_font(FONT_BODY, 42, "Regular")
    white = (*C["white"], 255)
    shadow = (*C["teal_deep"], 160)

    title_core = "Английский маяк"  # center these letters; colon hangs to the right
    title_w = ink_width(title_font, title_core)
    sub_w = ink_width(sub_font, SUBTITLE_TEXT)
    block_w = max(title_w, sub_w)

    # Shared horizontal center: the words «Английский маяк» sit exactly
    # above the midpoint of «подготовка…».
    cx = W / 2
    half = block_w / 2
    if cx + half > lighthouse_left - 40:
        cx = lighthouse_left - 40 - half

    title_x = centered_x(cx, title_font, title_core)
    sub_x = centered_x(cx, sub_font, SUBTITLE_TEXT)

    title_b = title_font.getbbox(TITLE_TEXT)
    core_b = title_font.getbbox(title_core)
    sub_b = sub_font.getbbox(SUBTITLE_TEXT)
    title_h = title_b[3] - title_b[1]
    gap = 56

    # Vertically: keep the pair in the upper-middle of the 1920x768 cover
    block_h = title_h + gap + (sub_b[3] - sub_b[1])
    y0 = int(round(H * 0.30 - block_h / 2))
    title_y = y0 - title_b[1]
    sub_y = title_y + title_b[3] + gap - sub_b[1]

    for dx, dy in ((0, 3), (3, 3)):
        draw.text((title_x + dx, title_y + dy), TITLE_TEXT, font=title_font, fill=shadow)
        draw.text((sub_x + dx, sub_y + dy), SUBTITLE_TEXT, font=sub_font, fill=shadow)
    draw.text((title_x, title_y), TITLE_TEXT, font=title_font, fill=white)
    draw.text((sub_x, sub_y), SUBTITLE_TEXT, font=sub_font, fill=white)

    title_center = title_x + (core_b[0] + core_b[2]) / 2
    sub_center = sub_x + (sub_b[0] + sub_b[2]) / 2
    print(
        f"align cx={cx:.1f} title_core_center={title_center:.1f} sub_center={sub_center:.1f} "
        f"delta={abs(title_center - sub_center):.2f}px"
    )
    print(f"title x={title_x} core_w={title_w}  sub x={sub_x} w={sub_w}")


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

    memo = build_memo()
    # Trim empty bottom so the sheet is compact
    arr = np.array(memo)
    bg = np.array(C["teal_deep"], dtype=np.int16)
    diff = np.abs(arr.astype(np.int16) - bg).sum(axis=2)
    rows = np.where(diff > 12)[0]
    if len(rows):
        bottom = min(memo.height, int(rows.max()) + 56)
        memo = memo.crop((0, 0, memo.width, bottom))
    memo.save(ROOT / "pamyatka.png", "PNG", optimize=True)
    memo.save(ROOT / "pamyatka.jpg", "JPEG", quality=95, optimize=True)

    cover = build_cover()
    cover.save(ROOT / "angliyskiy-mayak-1920x768.png", "PNG")
    cover.save(ROOT / "angliyskiy-mayak-1920x768.jpg", "JPEG", quality=98, subsampling=0)

    artifacts = Path("/opt/cursor/artifacts")
    artifacts.mkdir(parents=True, exist_ok=True)
    cover.save(artifacts / "oblozhka-vk-1920x768.png", "PNG")
    cover.save(artifacts / "oblozhka-vk-1920x768.jpg", "JPEG", quality=98, subsampling=0)
    cover.save(artifacts / "angliyskiy-mayak-1920x768.png", "PNG")
    memo.save(artifacts / "pamyatka.png", "PNG")
    board.save(artifacts / "palette.png", "PNG")

    import shutil
    import zipfile

    zip_path = ROOT / "oblozhka-vk-angliyskiy-mayak.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(ROOT / "angliyskiy-mayak-1920x768.png", "oblozhka-vk-1920x768.png")
        zf.write(ROOT / "angliyskiy-mayak-1920x768.jpg", "oblozhka-vk-1920x768.jpg")
        zf.write(ROOT / "pamyatka.png", "pamyatka.png")
        zf.write(ROOT / "palette.png", "palette.png")
    shutil.copy(zip_path, artifacts / "oblozhka-vk-angliyskiy-mayak.zip")
    print("wrote memo, palette and cover", cover.size, memo.size)


if __name__ == "__main__":
    main()
