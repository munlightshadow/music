#!/usr/bin/env python3
"""Собрать PNG-логотипы: Frame 5 (светлый вектор) и Frame 4 (тёмный кадр)."""

from __future__ import annotations

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
    LOGO_FRAME5_PDF,
    LOGO_ICON_ON_DARK_PNG,
    LOGO_ICON_PNG,
    LOGO_MARK_PNG,
    LOGO_ROW_ON_DARK_PNG,
    LOGO_ROW_PNG,
    LOGO_STACK_ON_DARK_PNG,
    LOGO_STACK_PNG,
    TEAL,
    TEAL_DEEP,
    TEAL_MID,
)

SOURCE_PDF = BRAND_DIR / "logo-source.pdf"
TMP = Path("/tmp/ege-logo-src")
DPI = 144  # страница 2500 pt → 5000 px


def flood_white_from_edges(
    im: Image.Image,
    threshold: int = 250,
    protect: Callable[[int, int], bool] | None = None,
) -> Image.Image:
    """Убрать белый холст. protect(x, y) — пиксели внутри круга, их не трогаем."""
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


def find_emblem_circle(im: Image.Image) -> tuple[float, float, float] | None:
    """Окружность цветного диска — по бирюзовому небу/воде."""
    px = im.load()
    w, h = im.size
    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            if g > r + 8 and b > r + 4 and g > 70 and max(r, g, b) > 90:
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
    cx = (minx + maxx) / 2.0
    cy = (miny + maxy) / 2.0
    rad = max(maxx - minx, maxy - miny) / 2.0 + 3
    return cx, cy, rad


def circle_protect(circle: tuple[float, float, float] | None):
    if circle is None:
        return None
    cx, cy, rad = circle

    def protect(x: int, y: int) -> bool:
        return (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad

    return protect


def knock_outside_circle(im: Image.Image, circle: tuple[float, float, float] | None = None) -> Image.Image:
    """Прозрачность только снаружи диска — белая башня внутри остаётся."""
    im = im.convert("RGBA")
    circle = circle or find_emblem_circle(im)
    if circle is None:
        return im
    cx, cy, rad = circle
    px = im.load()
    w, h = im.size
    r2 = rad * rad
    for y in range(h):
        for x in range(w):
            if (x - cx) ** 2 + (y - cy) ** 2 > r2:
                px[x, y] = (255, 255, 255, 0)
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


def make_stack(icon: Image.Image, word: Image.Image) -> Image.Image:
    """Vertical lockup: circular mark above the designer wordmark."""
    gap = max(16, int(icon.height * 0.08))
    width = max(icon.width, word.width)
    height = icon.height + gap + word.height
    canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    canvas.paste(icon, ((width - icon.width) // 2, 0), icon)
    canvas.paste(word, ((width - word.width) // 2, icon.height + gap), word)
    return canvas


def _is_gold(r: int, g: int, b: int) -> bool:
    return r > 180 and g > 140 and b < 170 and r + g > b * 2


def _is_white(r: int, g: int, b: int) -> bool:
    return r > 220 and g > 220 and b > 220


def _is_sky(r: int, g: int, b: int) -> bool:
    """Бирюзовый небосвод / вода Frame 5 (не золото, не башня)."""
    return g > r + 8 and b > r + 4 and g > 70 and max(r, g, b) > 90


def make_icon_frame4(icon: Image.Image) -> Image.Image:
    """Frame 4 — ночной диск: тёмное небо, белый маяк, чёрный купол, синие волны, бирюзовая обводка."""
    from PIL import ImageDraw

    im = icon.convert("RGBA")
    px = im.load()
    w, h = im.size
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    rad = min(w, h) / 2.0 - 1
    night = (12, 22, 32, 255)
    rock = (10, 12, 16, 255)
    shadow = (186, 216, 226, 255)
    wave = (70, 138, 157, 255)
    dome = (8, 10, 12, 255)
    ring = (*TEAL, 255)

    def in_circle(x: int, y: int, inset: float = 0.0) -> bool:
        return (x - cx) ** 2 + (y - cy) ** 2 <= (rad - inset) ** 2

    # 1) небо/вода → ночь (окна-прорези тоже становятся тёмными)
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 8 or not in_circle(x, y):
                continue
            if _is_gold(r, g, b):
                continue
            if _is_sky(r, g, b):
                px[x, y] = night

    # 2) тёмная половина башни → светло-голубая тень (башня читается белой)
    for y in range(h):
        ny = y / h
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 8 or not in_circle(x, y):
                continue
            if _is_gold(r, g, b) or _is_white(r, g, b):
                continue
            # уже ночное небо / прорези окон — не высветлять
            if r <= 20 and g <= 32 and b <= 42:
                continue
            if max(r, g, b) < 100 and abs(x - cx) < w * 0.24 and 0.16 < ny < 0.68:
                px[x, y] = shadow

    # 3) белые скалы → тёмные; тонкие белые линии в воде → бирюза
    for y in range(h):
        ny = y / h
        if ny < 0.66:
            continue
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 8 or not in_circle(x, y) or not _is_white(r, g, b):
                continue
            run = 0
            for dy in range(-6, 7):
                yy = y + dy
                if 0 <= yy < h:
                    rr, gg, bb, aa = px[x, yy]
                    if aa > 8 and _is_white(rr, gg, bb):
                        run += 1
            if run <= 4:
                px[x, y] = wave
            else:
                px[x, y] = rock

    # 3b) оставшаяся вода Frame 5 → ночь, волны уже бирюзовые
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 8 or not in_circle(x, y):
                continue
            if _is_gold(r, g, b) or _is_white(r, g, b):
                continue
            if g > r + 8 and b > r and max(r, g, b) < 120:
                px[x, y] = night

    # 4) чёрный купол над фонарём
    for y in range(h):
        ny = y / h
        if ny < 0.12 or ny > 0.22:
            continue
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 8 or not in_circle(x, y):
                continue
            if _is_gold(r, g, b):
                continue
            if abs(x - cx) < w * 0.075 and (_is_white(r, g, b) or max(r, g, b) > 140):
                px[x, y] = dome

    draw = ImageDraw.Draw(im)
    ring_w = max(4, w // 90)
    draw.ellipse((2, 2, w - 3, h - 3), outline=ring, width=ring_w)
    return im


def recolor_word_teal(word: Image.Image) -> Image.Image:
    """Frame 4: тёмный наборный логотип → бирюза #468A9D, антиалиас сохраняется альфой."""
    im = word.convert("RGBA")
    px = im.load()
    w, h = im.size
    tr, tg, tb = TEAL
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            lum = (r + g + b) / 3.0
            if lum >= 248:
                px[x, y] = (255, 255, 255, 0)
                continue
            k = max(0.0, min(1.0, (248 - lum) / 215.0))
            px[x, y] = (tr, tg, tb, int(round(a * k)))
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
    circle = find_emblem_circle(emblem)
    protect = circle_protect(circle)

    icon = knock_outside_circle(emblem, circle)
    ib = content_bbox(icon)
    if ib:
        # content_bbox игнорирует белое — сдвигаем protect? после crop координаты круга меняются.
        # проще ещё раз вырезать по кругу в новых координатах.
        icon = icon.crop(pad_bbox(ib, icon.size, 2))
        icon = knock_outside_circle(icon)
    word_clear = flood_white_from_edges(word)
    stack = flood_white_from_edges(lock, protect=protect)
    sb = content_bbox(stack)
    if sb:
        stack = stack.crop(pad_bbox(sb, stack.size, 4))
    row = make_row(icon, word_clear)
    icon_frame4 = make_icon_frame4(icon)
    word_frame4 = recolor_word_teal(word_clear)
    row_frame4 = make_row(icon_frame4, word_frame4)
    stack_frame4 = make_stack(icon_frame4, word_frame4)
    mark = make_white_mark(icon)
    cover = make_cover_bg(mark)

    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    if src.resolve() != LOGO_FRAME5_PDF.resolve():
        import shutil

        shutil.copy2(src, LOGO_FRAME5_PDF)
    icon.save(LOGO_ICON_PNG)
    row.save(LOGO_ROW_PNG)
    stack.save(LOGO_STACK_PNG)
    icon_frame4.save(LOGO_ICON_ON_DARK_PNG)
    row_frame4.save(LOGO_ROW_ON_DARK_PNG)
    stack_frame4.save(LOGO_STACK_ON_DARK_PNG)
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
