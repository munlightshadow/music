#!/usr/bin/env python3
"""Собрать PNG-логотипы из векторного файла дизайнера (Frame_4)."""

from __future__ import annotations

import subprocess
import sys
from collections import deque
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import (
    BRAND_DIR,
    COVER_BG_PNG,
    LOGO_ICON_ON_DARK_PNG,
    LOGO_ICON_PNG,
    LOGO_MARK_PNG,
    LOGO_ROW_PNG,
    LOGO_STACK_PNG,
    TEAL_DEEP,
    TEAL_MID,
)

SOURCE_PDF = BRAND_DIR / "logo-source.pdf"
TMP = Path("/tmp/ege-logo-src")
DPI = 144  # страница 2500 pt → 5000 px


def flood_white_from_edges(im: Image.Image, threshold: int = 250) -> Image.Image:
    """Убрать белый холст, не трогая белую башню и скалы внутри круга."""
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()

    def is_bg(x: int, y: int) -> bool:
        r, g, b, a = px[x, y]
        return a > 0 and r >= threshold and g >= threshold and b >= threshold

    seen = bytearray(w * h)
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        q.append((x, 0))
        q.append((x, h - 1))
    for y in range(h):
        q.append((0, y))
        q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h:
            continue
        i = y * w + x
        if seen[i]:
            continue
        seen[i] = 1
        if not is_bg(x, y):
            continue
        px[x, y] = (255, 255, 255, 0)
        q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return im


def content_bbox(im: Image.Image, threshold: int = 250) -> tuple[int, int, int, int] | None:
    px = im.load()
    w, h = im.size
    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 8 and (r < threshold or g < threshold or b < threshold):
                if x < minx:
                    minx = x
                if y < miny:
                    miny = y
                if x > maxx:
                    maxx = x
                if y > maxy:
                    maxy = y
    if maxx < 0:
        return None
    return minx, miny, maxx + 1, maxy + 1


def pad_bbox(bbox: tuple[int, int, int, int], size: tuple[int, int], pad: int) -> tuple[int, int, int, int]:
    l, t, r, b = bbox
    w, h = size
    return max(0, l - pad), max(0, t - pad), min(w, r + pad), min(h, b + pad)


def render_pdf(pdf: Path) -> Image.Image:
    TMP.mkdir(parents=True, exist_ok=True)
    prefix = TMP / "frame"
    for old in TMP.glob("frame*.png"):
        old.unlink()
    cmd = ["pdftocairo", "-png", "-r", str(DPI), str(pdf), str(prefix)]
    subprocess.run(cmd, check=True)
    pages = sorted(TMP.glob("frame*.png"))
    if not pages:
        raise SystemExit("pdftocairo did not write a PNG")
    return Image.open(pages[0]).convert("RGBA")


def split_lockup(lock: Image.Image) -> tuple[Image.Image, Image.Image]:
    """Circle on top, wordmark below — from the designer vertical lockup."""
    w, h = lock.size
    px = lock.load()
    # rows with ink
    ink_rows = []
    for y in range(h):
        n = 0
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 8 and (r < 250 or g < 250 or b < 250):
                n += 1
        if n > 12:
            ink_rows.append(y)
    if not ink_rows:
        raise SystemExit("empty lockup")
    # gap between emblem and title
    gap_y = None
    for i in range(1, len(ink_rows)):
        if ink_rows[i] - ink_rows[i - 1] > 40:
            gap_y = (ink_rows[i - 1] + ink_rows[i]) // 2
            break
    if gap_y is None:
        gap_y = int(h * 0.62)
    emblem = lock.crop((0, 0, w, gap_y))
    word = lock.crop((0, gap_y, w, h))
    eb = content_bbox(emblem)
    wb = content_bbox(word)
    if not eb or not wb:
        raise SystemExit("could not split emblem/wordmark")
    emblem = emblem.crop(pad_bbox(eb, emblem.size, 2))
    word = word.crop(pad_bbox(wb, word.size, 2))
    return emblem, word


def make_row(icon: Image.Image, word: Image.Image) -> Image.Image:
    """Horizontal lockup: circular mark + designer wordmark."""
    target_h = max(word.height, 120)
    scale = target_h / icon.height
    iw = max(1, int(icon.width * scale))
    ih = max(1, int(icon.height * scale))
    icon_s = icon.resize((iw, ih), Image.Resampling.LANCZOS)
    gap = max(18, int(ih * 0.12))
    canvas = Image.new("RGBA", (iw + gap + word.width, max(ih, word.height)), (255, 255, 255, 0))
    canvas.paste(icon_s, (0, (canvas.height - ih) // 2), icon_s)
    canvas.paste(word, (iw + gap, (canvas.height - word.height) // 2), word)
    return canvas


def make_icon_frame4(icon: Image.Image) -> Image.Image:
    """Frame 4 — ночной диск: тёмное небо, белый маяк, золотые лучи, тонкая бирюзовая обводка."""
    im = icon.convert("RGBA")
    px = im.load()
    w, h = im.size
    night = (10, 24, 32, 255)
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            if r > 180 and g > 140 and b < 170:
                continue  # gold
            if r > 220 and g > 220 and b > 220:
                continue  # white tower / waves
            # средний бирюзовый небосвод Frame 5 → ночь Frame 4
            if g > r + 12 and b > r + 8 and g > 70 and max(r, g, b) > 90:
                px[x, y] = night
    from PIL import ImageDraw

    draw = ImageDraw.Draw(im)
    teal = (0x46, 0x8A, 0x9D, 255)
    draw.ellipse((2, 2, w - 3, h - 3), outline=teal, width=max(3, w // 110))
    return im


def make_white_mark(icon: Image.Image) -> Image.Image:
    """Маяк белый с жёлтыми лучами, без круга — на синий титул."""
    src = icon.convert("RGBA")
    px = src.load()
    w, h = src.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    opx = out.load()
    cx = w / 2
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            if r > 180 and g > 140 and b < 170:
                opx[x, y] = (r, g, b, a)
                continue
            if r > 210 and g > 210 and b > 210:
                opx[x, y] = (255, 255, 255, a)
                continue
            # тёмная половина башни → белая; море/небо не берём
            if max(r, g, b) < 95 and abs(x - cx) < w * 0.22 and y < h * 0.78:
                opx[x, y] = (255, 255, 255, a)
    bbox = out.getbbox()
    if bbox:
        out = out.crop(pad_bbox(bbox, out.size, 8))
    return out


def make_cover_bg(mark: Image.Image, width: int = 1920, height: int = 1080) -> Image.Image:
    """Синий градиент из брендбука, маяк в правом нижнем углу."""
    bg = Image.new("RGB", (width, height))
    px = bg.load()
    a, b = TEAL_MID, TEAL_DEEP
    for y in range(height):
        for x in range(width):
            t = min(1.0, (x / width) * 0.42 + (y / height) * 0.58)
            px[x, y] = (
                int(a[0] + (b[0] - a[0]) * t),
                int(a[1] + (b[1] - a[1]) * t),
                int(a[2] + (b[2] - a[2]) * t),
            )
    rgba = bg.convert("RGBA")
    mh = int(height * 0.38)
    scale = mh / mark.height
    mw = max(1, int(mark.width * scale))
    mark_s = mark.resize((mw, mh), Image.Resampling.LANCZOS)
    pad = int(height * 0.055)
    rgba.paste(mark_s, (width - mw - pad, height - mh - pad), mark_s)
    return rgba


def main() -> int:
    src = SOURCE_PDF
    if not src.exists():
        raise SystemExit(f"Нет {src}. Положите векторный файл дизайнера как brand/logo-source.pdf")
    page = render_pdf(src)
    bbox = content_bbox(page)
    if not bbox:
        raise SystemExit("designer PDF looks empty")
    lock = page.crop(pad_bbox(bbox, page.size, 8))
    emblem, word = split_lockup(lock)

    icon = flood_white_from_edges(emblem)
    ib = content_bbox(icon)
    if ib:
        icon = icon.crop(pad_bbox(ib, icon.size, 2))
    stack = flood_white_from_edges(lock)
    sb = content_bbox(stack)
    if sb:
        stack = stack.crop(pad_bbox(sb, stack.size, 4))
    row = make_row(icon, flood_white_from_edges(word))
    icon_frame4 = make_icon_frame4(icon)
    mark = make_white_mark(icon)
    cover = make_cover_bg(mark)

    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    frame5 = BRAND_DIR / "logo-frame5.pdf"
    if src.resolve() != frame5.resolve():
        import shutil

        shutil.copy2(src, frame5)
    icon.save(LOGO_ICON_PNG)
    row.save(LOGO_ROW_PNG)
    stack.save(LOGO_STACK_PNG)
    icon_frame4.save(LOGO_ICON_ON_DARK_PNG)
    mark.save(LOGO_MARK_PNG)
    cover.save(COVER_BG_PNG)
    for p in (
        LOGO_ICON_PNG,
        LOGO_ROW_PNG,
        LOGO_STACK_PNG,
        LOGO_ICON_ON_DARK_PNG,
        LOGO_MARK_PNG,
        COVER_BG_PNG,
    ):
        print(f"OK  {p.relative_to(p.parents[1])}  {Image.open(p).size}  {p.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
