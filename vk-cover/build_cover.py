#!/usr/bin/env python3
"""Build the brand memo, palette board, and the 1920x768 VK community cover."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
LOGO_EMBLEM = ROOT / "assets" / "logo-emblem.png"
ASSETS_LIGHTHOUSE = Path("/opt/cursor/artifacts/assets/vk-cover-sea-lighthouse.png")
FALLBACK_LIGHTHOUSE = Path("/tmp/lighthouse-extract.png")
FONTS = ROOT / "fonts"
FONT_TITLE = str(FONTS / "SofiaSansCondensed.ttf")
FONT_BODY = str(FONTS / "OpenSans.ttf")

W, H = 1920, 768
TITLE_TEXT = "АНГЛИЙСКИЙ МАЯК"
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
    sample_body = load_font(FONT_BODY, 32, "Bold")

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
            "sample": "АНГЛИЙСКИЙ МАЯК",
            "sample_font": sample_title,
        },
        {
            "kicker": "Маленький — для пояснения",
            "name": "Open Sans",
            "meta": "Начертание Bold · подзаголовок, описания",
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
        "Название: Sofia Sans Condensed ExtraBold, белый #FFFFFF · АНГЛИЙСКИЙ МАЯК",
        "Подзаголовок: Open Sans Bold, белый #FFFFFF",
        "Выравнивание: «АНГЛИЙСКИЙ МАЯК» ровно по центру над «подготовка…»",
        "Фон: море #488DA0 → #214149 → #1A333A · маяк справа снизу, лучи #C19B4F",
    ]
    ry = y + 24
    for line in rules:
        draw.text((pad + 36, ry), "·  " + line, font=body, fill=C["white"])
        ry += 36

    return img


def _logo_inside_mask(arr: np.ndarray) -> np.ndarray:
    """Circle of the emblem, from the teal sky/sea (ignores the white page)."""
    rgb = arr.astype(np.int16)
    teal = (rgb[:, :, 2] > rgb[:, :, 0] + 16) & (rgb[:, :, 1] > rgb[:, :, 0] + 6)
    ys, xs = np.where(teal)
    cy, cx = float(np.median(ys)), float(np.median(xs))
    r = float(np.percentile(np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2), 99.2))
    yy, xx = np.ogrid[: arr.shape[0], : arr.shape[1]]
    return (yy - cy) ** 2 + (xx - cx) ** 2 <= (r * 0.995) ** 2


def logo_sky_sea() -> tuple[np.ndarray, np.ndarray]:
    src = Image.open(LOGO_EMBLEM).convert("RGB")
    arr = np.array(src)
    inside = _logo_inside_mask(arr)
    rgb = arr.astype(np.int16)
    brightness = rgb.mean(axis=2)
    teal = (rgb[:, :, 2] > rgb[:, :, 0] + 18) & (rgb[:, :, 1] > rgb[:, :, 0] + 8)
    ys, xs = np.where(inside)
    y0, y1 = int(ys.min()), int(ys.max())
    split = y0 + int((y1 - y0) * 0.62)
    sky_px = arr[inside & teal & (np.arange(arr.shape[0])[:, None] < split)]
    sea_px = arr[inside & teal & (np.arange(arr.shape[0])[:, None] >= split)]
    if len(sky_px) == 0:
        sky = np.array(C["teal_horizon"], dtype=np.float32)
    else:
        sky = np.median(sky_px, axis=0).astype(np.float32)
    if len(sea_px) == 0:
        sea = np.array(C["dark_teal"], dtype=np.float32)
    else:
        sea = np.median(sea_px, axis=0).astype(np.float32)
    return sky, sea


def extract_lighthouse() -> Image.Image:
    src_path = LOGO_EMBLEM if LOGO_EMBLEM.exists() else ASSETS_LIGHTHOUSE
    src = Image.open(src_path).convert("RGB")
    arr = np.array(src)
    inside = _logo_inside_mask(arr) if src_path == LOGO_EMBLEM else np.ones(arr.shape[:2], bool)
    rgb = arr.astype(np.int16)
    brightness = rgb.mean(axis=2)
    gold = (rgb[:, :, 0] > 155) & (rgb[:, :, 1] > 95) & (rgb[:, :, 0] > rgb[:, :, 2] + 22)
    white_struct = (brightness > 205) & inside
    dark_detail = (brightness < 55) & inside
    white_d = Image.fromarray((white_struct.astype(np.uint8) * 255), "L").filter(ImageFilter.MaxFilter(9))
    near_white = np.array(white_d) > 0
    keep = gold | white_struct | (dark_detail & near_white)

    # Drop the circular rim so we keep the lighthouse, not the emblem frame
    yy, xx = np.ogrid[: arr.shape[0], : arr.shape[1]]
    ys, xs = np.where(inside)
    cy, cx = float(np.median(ys)), float(np.median(xs))
    r = float(np.sqrt(((xs - cx) ** 2 + (ys - cy) ** 2).max()))
    keep = keep & (((yy - cy) ** 2 + (xx - cx) ** 2) < (r * 0.90) ** 2)

    alpha = Image.fromarray((keep.astype(np.uint8) * 255), "L")
    alpha = alpha.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.1))
    aa = np.array(alpha).astype(np.float32)
    aa[~inside] = 0
    # Drop leftover sky/sea teal from the alpha fringe
    teal = (rgb[:, :, 2] > rgb[:, :, 0] + 18) & (rgb[:, :, 1] > rgb[:, :, 0] + 8) & (brightness < 190)
    aa[teal] *= 0.04

    lh = Image.fromarray(arr, "RGB").convert("RGBA")
    lh.putalpha(Image.fromarray(np.clip(aa, 0, 255).astype(np.uint8), "L"))
    bbox = lh.getbbox()
    lh = lh.crop(bbox)

    pixels = np.array(lh).astype(np.float32)
    rgb, alpha = pixels[:, :, :3], pixels[:, :, 3]
    brightness = rgb.mean(axis=2)
    gold_mask = (
        (rgb[:, :, 0] > 150)
        & (rgb[:, :, 1] > 95)
        & (rgb[:, :, 0] > rgb[:, :, 2] + 18)
        & (alpha > 40)
    )
    white_mask = (brightness > 200) & (alpha > 80) & ~gold_mask
    gold_t = np.clip((brightness - 140) / 90.0, 0.0, 1.0)
    rgb[gold_mask] = lerp(C["muted_gold"], C["gold_light"], gold_t[:, :, None])[gold_mask]
    rgb[white_mask] = np.array(C["white"], dtype=np.float32)
    out = np.dstack([np.clip(rgb, 0, 255), np.clip(alpha, 0, 255)]).astype(np.uint8)
    lh = Image.fromarray(out, "RGBA")
    bbox = lh.getbbox()
    lh = lh.crop(bbox)
    target_h = 280
    scale = target_h / lh.height
    return lh.resize((max(1, int(lh.width * scale)), target_h), Image.Resampling.LANCZOS)


def build_sea() -> Image.Image:
    """Expand the logo circle's sky/sea blues across the 1920x768 banner."""
    sky, sea = logo_sky_sea()
    col = np.zeros((H, W, 3), dtype=np.float32)
    # Same split as the emblem: sky occupies the upper ~62%, water the rest
    split = 0.62
    t = np.linspace(0.0, 1.0, H, dtype=np.float32)
    for i, ti in enumerate(t):
        if ti < split:
            # keep sky almost flat, like the solid fill in the logo
            col[i] = sky
        else:
            u = (ti - split) / (1.0 - split)
            col[i] = lerp(sky, sea, u ** 0.7)

    # Soft side vignette using the sea color so the wide banner doesn't feel empty
    xx = np.linspace(0.0, 1.0, W, dtype=np.float32)[None, :]
    edge = np.clip(np.maximum(0.08 - xx, xx - 0.92) / 0.08, 0, 1)
    col = col * (1.0 - 0.12 * edge[:, :, None]) + sea * (0.12 * edge[:, :, None])
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB")


def draw_cover_text(canvas: Image.Image, lighthouse_left: int) -> None:
    draw = ImageDraw.Draw(canvas)
    # All caps: Sofia's lowercase к is a Latin k with an ascender.
    # The logo itself uses АНГЛИЙСКИЙ МАЯК, so the title matches it.
    title_font = load_font(FONT_TITLE, 88, "ExtraBold")
    sub_font = load_font(FONT_BODY, 50, "Bold")
    white = (*C["white"], 255)
    shadow = (*C["teal_deep"], 160)

    title_w = title_font.getlength(TITLE_TEXT)
    sub_w = sub_font.getlength(SUBTITLE_TEXT)
    block_w = max(title_w, sub_w)

    cx = W / 2
    if cx + block_w / 2 > lighthouse_left - 48:
        cx = max(block_w / 2 + 36, lighthouse_left - 48 - block_w / 2)

    title_x = cx - title_w / 2
    sub_x = cx - sub_w / 2

    ascent, _d = title_font.getmetrics()
    sub_ascent, _sd = sub_font.getmetrics()
    gap = 56
    top = H * 0.30 - (ascent + gap + sub_ascent) / 2
    title_baseline = top + ascent
    sub_baseline = title_baseline + gap + sub_ascent

    for dx, dy in ((0, 3), (3, 3)):
        draw.text((title_x + dx, title_baseline + dy), TITLE_TEXT, font=title_font, fill=shadow, anchor="ls")
        draw.text((sub_x + dx, sub_baseline + dy), SUBTITLE_TEXT, font=sub_font, fill=shadow, anchor="ls")
    draw.text((title_x, title_baseline), TITLE_TEXT, font=title_font, fill=white, anchor="ls")
    draw.text((sub_x, sub_baseline), SUBTITLE_TEXT, font=sub_font, fill=white, anchor="ls")

    print(f"align cx={cx:.1f} title_w={title_w:.1f} sub_w={sub_w:.1f}")
    print(f"title_x={title_x:.1f} sub_x={sub_x:.1f} lh_left={lighthouse_left}")


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
    try:
        shutil.copy(zip_path, artifacts / "oblozhka-vk-angliyskiy-mayak.zip")
    except OSError:
        pass
    print("wrote memo, palette and cover", cover.size, memo.size)


if __name__ == "__main__":
    main()
