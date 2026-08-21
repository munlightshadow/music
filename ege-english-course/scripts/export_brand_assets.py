#!/usr/bin/env python3
"""Вырезать PNG-логотипы из растра PDF дизайнера.

Вектор в файле неполный (Type 3, пустые глифы). Страницу растрируем
и кропаем lockup как на макете — без пересборки круга.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from collections import deque
from collections.abc import Callable
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import (
    BRAND_DIR,
    COVER_BG_PNG,
    LOGO_FRAME_DARK_PDF,
    LOGO_FRAME_LIGHT_PDF,
    LOGO_ICON_ON_DARK_PNG,
    LOGO_ICON_PNG,
    LOGO_MARK_PNG,
    LOGO_ROW_ON_DARK_PNG,
    LOGO_ROW_PNG,
    LOGO_SOURCE_PDF,
    LOGO_STACK_ON_DARK_PNG,
    LOGO_STACK_PNG,
    TEAL_DEEP,
    TEAL_MID,
)

TMP = Path("/tmp/ege-logo-src")
DPI = 216  # 2500 pt → 7500 px


def flood_white_from_edges(
    im: Image.Image,
    threshold: int = 250,
    protect: Callable[[int, int], bool] | None = None,
) -> Image.Image:
    """Прозрачный холст с краёв. protect — диск маяка, белое небо не трогаем."""
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()

    def is_bg(x: int, y: int) -> bool:
        if protect is not None and protect(x, y):
            return False
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


def render_pdf(pdf: Path, prefix: str) -> Image.Image:
    TMP.mkdir(parents=True, exist_ok=True)
    stem = TMP / prefix
    for old in TMP.glob(f"{prefix}*.png"):
        old.unlink()
    subprocess.run(["pdftocairo", "-png", "-r", str(DPI), str(pdf), str(stem)], check=True)
    pages = sorted(TMP.glob(f"{prefix}*.png"))
    if not pages:
        raise SystemExit(f"pdftocairo did not write a PNG for {pdf.name}")
    return Image.open(pages[0]).convert("RGBA")


def split_emblem_word(lock: Image.Image) -> tuple[Image.Image, Image.Image, int]:
    """Круг сверху, набор снизу — по щели в растре страницы."""
    w, h = lock.size
    px = lock.load()
    ink_rows: list[int] = []
    for y in range(h):
        n = 0
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 8 and (r < 250 or g < 250 or b < 250):
                n += 1
        if n > 12:
            ink_rows.append(y)
    if not ink_rows:
        raise SystemExit("empty lockup crop")
    gap_y = int(h * 0.62)
    for i in range(1, len(ink_rows)):
        if ink_rows[i] - ink_rows[i - 1] > 30:
            gap_y = (ink_rows[i - 1] + ink_rows[i]) // 2
            break
    emblem = lock.crop((0, 0, w, gap_y))
    word = lock.crop((0, gap_y, w, h))
    return emblem, word, gap_y


def fitted_circle(emblem: Image.Image) -> tuple[float, float, float]:
    bb = content_bbox(emblem)
    if not bb:
        w, h = emblem.size
        return (w - 1) / 2.0, (h - 1) / 2.0, min(w, h) / 2.0
    l, t, r, b = bb
    cx = (l + r - 1) / 2.0
    cy = (t + b - 1) / 2.0
    rad = max(r - l, b - t) / 2.0 + 1.5
    return cx, cy, rad


def knock_outside_circle(im: Image.Image, circle: tuple[float, float, float]) -> Image.Image:
    im = im.convert("RGBA")
    cx, cy, rad = circle
    r2 = rad * rad
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            if (x - cx) ** 2 + (y - cy) ** 2 > r2:
                px[x, y] = (255, 255, 255, 0)
    bb = content_bbox(im)
    if bb:
        im = im.crop(pad_bbox(bb, im.size, 2))
    return im


def make_row(icon: Image.Image, word: Image.Image) -> Image.Image:
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


def lockup_from_page(page: Image.Image) -> tuple[Image.Image, Image.Image, Image.Image]:
    """Вырезать lockup с страницы PDF как есть."""
    bbox = content_bbox(page)
    if not bbox:
        raise SystemExit("PDF page looks empty")
    lock = page.crop(pad_bbox(bbox, page.size, 6))
    emblem, word, _gap = split_emblem_word(lock)
    cx, cy, rad = fitted_circle(emblem)

    def protect(x: int, y: int) -> bool:
        return (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad

    stack = flood_white_from_edges(lock, protect=protect)
    sb = content_bbox(stack)
    if sb:
        stack = stack.crop(pad_bbox(sb, stack.size, 2))
    icon = knock_outside_circle(emblem, (cx, cy, rad))
    word_c = flood_white_from_edges(word)
    wb = content_bbox(word_c)
    if not wb:
        raise SystemExit("wordmark not found under the circle")
    word_c = word_c.crop(pad_bbox(wb, word_c.size, 2))
    row = make_row(icon, word_c)
    return icon, stack, row


def make_white_mark(icon: Image.Image) -> Image.Image:
    """Маяк белый с жёлтыми лучами — на синий титул."""
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
            if max(r, g, b) < 95 and abs(x - cx) < w * 0.22 and y < h * 0.78:
                opx[x, y] = (255, 255, 255, a)
    bbox = out.getbbox()
    if bbox:
        out = out.crop(pad_bbox(bbox, out.size, 8))
    return out


def make_cover_bg(mark: Image.Image, width: int = 1920, height: int = 1080) -> Image.Image:
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
    light_pdf = LOGO_FRAME_LIGHT_PDF if LOGO_FRAME_LIGHT_PDF.exists() else LOGO_SOURCE_PDF
    dark_pdf = LOGO_FRAME_DARK_PDF
    if not light_pdf.exists():
        raise SystemExit(f"Нет светлого PDF {light_pdf}")
    if not dark_pdf.exists():
        raise SystemExit(f"Нет тёмного PDF {dark_pdf}")

    icon_l, stack_l, row_l = lockup_from_page(render_pdf(light_pdf, "light"))
    icon_d, stack_d, row_d = lockup_from_page(render_pdf(dark_pdf, "dark"))
    mark = make_white_mark(icon_d)
    cover = make_cover_bg(mark)

    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    if light_pdf.resolve() != LOGO_SOURCE_PDF.resolve():
        shutil.copy2(light_pdf, LOGO_SOURCE_PDF)

    icon_l.save(LOGO_ICON_PNG)
    row_l.save(LOGO_ROW_PNG)
    stack_l.save(LOGO_STACK_PNG)
    icon_d.save(LOGO_ICON_ON_DARK_PNG)
    row_d.save(LOGO_ROW_ON_DARK_PNG)
    stack_d.save(LOGO_STACK_ON_DARK_PNG)
    mark.save(LOGO_MARK_PNG)
    cover.save(COVER_BG_PNG)
    for p in (
        LOGO_ICON_PNG,
        LOGO_ROW_PNG,
        LOGO_STACK_PNG,
        LOGO_ICON_ON_DARK_PNG,
        LOGO_ROW_ON_DARK_PNG,
        LOGO_STACK_ON_DARK_PNG,
        LOGO_MARK_PNG,
        COVER_BG_PNG,
    ):
        print(f"OK  {p.relative_to(p.parents[1])}  {Image.open(p).size}  {p.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
