#!/usr/bin/env python3
"""Crop demo KIM pages and FIPI sample works into images for the intro presentation."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "03-curriculum" / "intro-student" / "img"
TMP = Path("/tmp/ege-intro-img")

UPLOADS = Path("/home/ubuntu/.cursor/projects/workspace/uploads")
PCH = UPLOADS / "angl_yaz_pch_mr_ege_2025_compressed_8659.pdf"
UCH = UPLOADS / "angl_yaz_uch_mr_ege_2025_8c4b.pdf"
DEMO_PCH = Path("/tmp/fipi/demo-pch.pdf")
DEMO_UCH = Path("/tmp/fipi/demo-uch.pdf")
DEMO_URL_P = "https://4ege.ru/upp/25/2demo-ege-2025/en-p.pdf"
DEMO_URL_U = "https://4ege.ru/upp/25/2demo-ege-2025/en-u.pdf"


def ensure_demo():
    DEMO_PCH.parent.mkdir(parents=True, exist_ok=True)
    if not DEMO_PCH.exists() or DEMO_PCH.stat().st_size < 10000:
        subprocess.check_call(["curl", "-fsSL", "-A", "Mozilla/5.0", "-o", str(DEMO_PCH), DEMO_URL_P])
    if not DEMO_UCH.exists() or DEMO_UCH.stat().st_size < 10000:
        subprocess.check_call(["curl", "-fsSL", "-A", "Mozilla/5.0", "-o", str(DEMO_UCH), DEMO_URL_U])


def ppm(pdf: Path, dest: Path, first: int, last: int, dpi: int = 160):
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(
        ["pdftoppm", "-png", "-r", str(dpi), "-f", str(first), "-l", str(last), str(pdf), str(dest)]
    )


def split_2up(path: Path) -> tuple[Image.Image, Image.Image]:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    m = 10
    left = im.crop((m, m, w // 2 - 4, h - m))
    right = im.crop((w // 2 + 4, m, w - m, h - m))
    return left, right


def frac(im: Image.Image, l, t, r, b) -> Image.Image:
    w, h = im.size
    return im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))


def save(im: Image.Image, name: str):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(path, "PNG", optimize=True)
    print(f"  {path.name}  {im.size[0]}x{im.size[1]}  {path.stat().st_size}b")


def vstack(images: list[Image.Image]) -> Image.Image:
    w = max(i.size[0] for i in images)
    scaled = []
    for im in images:
        if im.size[0] != w:
            nh = int(im.size[1] * w / im.size[0])
            im = im.resize((w, nh), Image.Resampling.LANCZOS)
        scaled.append(im)
    h = sum(i.size[1] for i in scaled)
    out = Image.new("RGB", (w, h), (255, 255, 255))
    y = 0
    for im in scaled:
        out.paste(im, (0, y))
        y += im.size[1]
    return out


def main():
    ensure_demo()
    TMP.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    def listed(prefix: str) -> list[Path]:
        files = sorted(TMP.glob(f"{prefix}-*.png"))
        if not files:
            raise FileNotFoundError(prefix)
        return files

    ppm(DEMO_PCH, TMP / "dp", 2, 10, 150)
    ppm(DEMO_UCH, TMP / "du", 2, 4, 150)
    ppm(PCH, TMP / "mrw", 26, 28, 150)
    ppm(PCH, TMP / "w8311", 93, 93, 160)
    ppm(PCH, TMP / "w8447", 101, 101, 160)
    ppm(PCH, TMP / "w1025", 135, 136, 160)
    ppm(PCH, TMP / "w8781", 155, 155, 160)
    ppm(UCH, TMP / "o0487", 91, 91, 150)
    ppm(UCH, TMP / "o9213", 99, 100, 150)

    dp, du, mrw = listed("dp"), listed("du"), listed("mrw")
    l, r = split_2up(dp[0])
    save(l, "demo-blank-instruction.png")
    save(r, "demo-listening-1-2.png")
    l, r = split_2up(dp[1])
    save(l, "demo-listening-3-9.png")
    save(r, "demo-listening-3-9b.png")
    l, r = split_2up(dp[2])
    save(vstack([l, r]), "demo-reading-10.png")
    l, r = split_2up(dp[3])
    save(l, "demo-reading-11.png")
    save(r, "demo-reading-12.png")
    l, r = split_2up(dp[5])
    save(l, "demo-grammar-19-24.png")
    l, r = split_2up(dp[6])
    save(l, "demo-wordformation-25-29.png")
    save(r, "demo-lexis-30-36.png")
    _, r = split_2up(dp[7])
    save(r, "demo-writing-37.png")

    m26 = Image.open(mrw[0]).convert("RGB")
    m27 = Image.open(mrw[1]).convert("RGB")
    m28 = Image.open(mrw[2]).convert("RGB")
    save(frac(m26, 0.04, 0.42, 0.96, 0.97), "demo-writing-37-mr.png")
    save(frac(m27, 0.04, 0.22, 0.96, 0.97), "demo-writing-38-1.png")
    save(frac(m28, 0.04, 0.03, 0.96, 0.62), "demo-writing-38-2.png")

    _, r = split_2up(du[0])
    save(r, "demo-speaking-1.png")
    l, r = split_2up(du[1])
    save(l, "demo-speaking-2.png")
    save(r, "demo-speaking-3.png")
    l, _ = split_2up(du[2])
    save(l, "demo-speaking-4.png")

    save(frac(Image.open(listed("w8311")[0]).convert("RGB"), 0.07, 0.055, 0.93, 0.52), "work-8311.png")
    save(frac(Image.open(listed("w8447")[0]).convert("RGB"), 0.07, 0.30, 0.93, 0.97), "work-8447.png")
    w1025 = listed("w1025")
    save(
        vstack(
            [
                frac(Image.open(w1025[0]).convert("RGB"), 0.07, 0.30, 0.93, 0.985),
                frac(Image.open(w1025[1]).convert("RGB"), 0.07, 0.04, 0.93, 0.285),
            ]
        ),
        "work-1025.png",
    )
    save(frac(Image.open(listed("w8781")[0]).convert("RGB"), 0.05, 0.035, 0.95, 0.97), "work-8781.png")
    save(Image.open(listed("o0487")[0]).convert("RGB"), "work-0487.png")
    o9213 = listed("o9213")
    save(
        vstack(
            [
                frac(Image.open(o9213[0]).convert("RGB"), 0.04, 0.04, 0.96, 0.96),
                frac(Image.open(o9213[1]).convert("RGB"), 0.04, 0.04, 0.96, 0.55),
            ]
        ),
        "work-9213.png",
    )

    print(f"OK  {len(list(OUT.glob('*.png')))} images → {OUT}")


if __name__ == "__main__":
    main()
