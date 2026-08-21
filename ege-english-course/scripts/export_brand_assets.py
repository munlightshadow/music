#!/usr/bin/env python3
"""Собрать PNG-логотипы из SVG через Chrome (для PDF и PPTX)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import BRAND_DIR, LOGO_ICON_PNG, LOGO_ICON_SVG, LOGO_ROW_PNG, LOGO_STACK_PNG, hex_of, CHARCOAL, TEAL_DARK
from intro_student_presentation import CHROME, CHROME_PROFILE

TMP = Path("/tmp/ege-brand")


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


def knock_white(im: Image.Image, threshold: int = 248) -> Image.Image:
    """Make near-white pixels transparent so lockups sit on dark or light slides."""
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 0 and r >= threshold and g >= threshold and b >= threshold:
                px[x, y] = (255, 255, 255, 0)
    return im


def trim(path: Path, pad: int = 8) -> None:
    im = Image.open(path).convert("RGBA")
    bg = im.getpixel((0, 0))
    bbox = im.getbbox()
    if bg[0] > 240 and bg[1] > 240 and bg[2] > 240:
        mask = Image.new("L", im.size, 0)
        px = im.load()
        m = mask.load()
        w, h = im.size
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if a > 8 and (r < 250 or g < 250 or b < 250):
                    m[x, y] = 255
        bbox = mask.getbbox()
    if not bbox:
        knock_white(im).save(path)
        return
    l, t, r, b = bbox
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(im.width, r + pad)
    b = min(im.height, b + pad)
    knock_white(im.crop((l, t, r, b))).save(path)


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
    trim(LOGO_ICON_PNG, 4)

    icon_uri = LOGO_ICON_PNG.resolve().as_uri()
    teal = hex_of(TEAL_DARK)
    gray = hex_of(CHARCOAL)
    write(
        TMP / "row.html",
        f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
html,body{{margin:0;background:#fff}}
.row{{display:flex;align-items:center;gap:28px;padding:24px 32px;width:1100px;font-family:"Liberation Sans","Noto Sans",Arial,sans-serif}}
img{{width:168px;height:168px}}
h1{{margin:0 0 8px;font-size:42px;letter-spacing:.08em;color:{teal};font-weight:700}}
p{{margin:0;font-size:18px;color:{gray}}}
</style></head><body>
<div class="row"><img src="{icon_uri}" alt=""><div><h1>АНГЛИЙСКИЙ МАЯК</h1><p>подготовка к ОГЭ и ЕГЭ по английскому</p></div></div>
</body></html>""",
    )
    chrome_shot(TMP / "row.html", LOGO_ROW_PNG, 1200, 240)
    trim(LOGO_ROW_PNG, 6)

    write(
        TMP / "stack.html",
        f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
html,body{{margin:0;background:#fff}}
.stack{{width:640px;padding:28px 24px 36px;text-align:center;font-family:"Liberation Sans","Noto Sans",Arial,sans-serif}}
img{{width:200px;height:200px}}
h1{{margin:18px 0 8px;font-size:34px;letter-spacing:.1em;color:{teal};font-weight:700}}
p{{margin:0;font-size:16px;color:{gray}}}
</style></head><body>
<div class="stack"><img src="{icon_uri}" alt=""><h1>АНГЛИЙСКИЙ МАЯК</h1><p>подготовка к ОГЭ и ЕГЭ по английскому</p></div>
</body></html>""",
    )
    chrome_shot(TMP / "stack.html", LOGO_STACK_PNG, 700, 400)
    trim(LOGO_STACK_PNG, 6)

    for p in (LOGO_ICON_PNG, LOGO_ROW_PNG, LOGO_STACK_PNG):
        print(f"OK  {p.relative_to(p.parents[1])}  {Image.open(p).size}  {p.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
