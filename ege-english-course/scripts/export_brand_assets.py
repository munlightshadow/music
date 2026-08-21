#!/usr/bin/env python3
"""Собрать PNG-логотипы из SVG через Chrome (для PDF и PPTX)."""

from __future__ import annotations

import subprocess
import sys
from collections import deque
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import BRAND_DIR, LOGO_ICON_PNG, LOGO_ICON_SVG, LOGO_ROW_PNG, LOGO_STACK_PNG, hex_of, TEAL_DARK
from intro_student_presentation import CHROME, CHROME_PROFILE

TMP = Path("/tmp/ege-brand")
TAG_GRAY = "#707070"
FONT = 'Inter, "Noto Sans", Arial, sans-serif'


def chrome_shot(html: Path, png: Path, w: int, h: int) -> None:
    CHROME_PROFILE.mkdir(parents=True, exist_ok=True)
    png.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        CHROME,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--hide-scrollbars",
        "--no-first-run",
        "--no-default-browser-check",
        "--allow-file-access-from-files",
        f"--window-size={w},{h}",
        f"--screenshot={png}",
        f"--user-data-dir={CHROME_PROFILE}",
        html.resolve().as_uri(),
    ]
    result = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
    if result.returncode != 0 or not png.exists() or png.stat().st_size < 200:
        raise SystemExit(f"Chrome screenshot failed for {html.name}\n{result.stderr[-2000:]}")


def flood_white_from_edges(im: Image.Image, threshold: int = 248) -> Image.Image:
    """Drop page background only. Keep the white lighthouse inside the circle."""
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


def trim(path: Path, pad: int = 8) -> None:
    im = Image.open(path).convert("RGBA")
    px = im.load()
    w, h = im.size
    mask = Image.new("L", im.size, 0)
    m = mask.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 8 and (r < 250 or g < 250 or b < 250):
                m[x, y] = 255
    bbox = mask.getbbox()
    if not bbox:
        flood_white_from_edges(im).save(path)
        return
    l, t, r, b = bbox
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(im.width, r + pad)
    b = min(im.height, b + pad)
    flood_white_from_edges(im.crop((l, t, r, b))).save(path)


def write(path: Path, html: str) -> None:
    path.write_text(html, encoding="utf-8")


def main() -> int:
    TMP.mkdir(parents=True, exist_ok=True)
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    icon_svg = LOGO_ICON_SVG.read_text(encoding="utf-8")
    write(
        TMP / "icon.html",
        f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>html,body{{margin:0;background:#fff}}svg{{display:block;width:640px;height:640px;margin:40px}}</style>
</head><body>{icon_svg}</body></html>""",
    )
    chrome_shot(TMP / "icon.html", LOGO_ICON_PNG, 720, 720)
    trim(LOGO_ICON_PNG, 2)

    icon_uri = LOGO_ICON_PNG.resolve().as_uri()
    teal = hex_of(TEAL_DARK)
    write(
        TMP / "row.html",
        f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
html,body{{margin:0;background:#fff}}
.row{{display:flex;align-items:center;gap:26px;padding:28px 36px;width:1180px;font-family:{FONT}}}
img{{width:176px;height:176px}}
h1{{margin:0 0 10px;font-size:44px;letter-spacing:.12em;color:{teal};font-weight:700}}
p{{margin:0;font-size:18px;color:{TAG_GRAY};font-weight:400}}
</style></head><body>
<div class="row"><img src="{icon_uri}" alt=""><div><h1>АНГЛИЙСКИЙ МАЯК</h1><p>подготовка к ОГЭ и ЕГЭ по английскому</p></div></div>
</body></html>""",
    )
    chrome_shot(TMP / "row.html", LOGO_ROW_PNG, 1280, 260)
    trim(LOGO_ROW_PNG, 6)

    write(
        TMP / "stack.html",
        f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
html,body{{margin:0;background:#fff}}
.stack{{width:720px;padding:36px 28px 40px;text-align:center;font-family:{FONT}}}
img{{width:228px;height:228px;display:block;margin:0 auto}}
h1{{margin:22px 0 10px;font-size:36px;letter-spacing:.14em;color:{teal};font-weight:700}}
p{{margin:0;font-size:17px;color:{TAG_GRAY};font-weight:400}}
</style></head><body>
<div class="stack"><img src="{icon_uri}" alt=""><h1>АНГЛИЙСКИЙ МАЯК</h1><p>подготовка к ОГЭ и ЕГЭ по английскому</p></div>
</body></html>""",
    )
    chrome_shot(TMP / "stack.html", LOGO_STACK_PNG, 780, 480)
    trim(LOGO_STACK_PNG, 6)

    for p in (LOGO_ICON_PNG, LOGO_ROW_PNG, LOGO_STACK_PNG):
        print(f"OK  {p.relative_to(p.parents[1])}  {Image.open(p).size}  {p.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
