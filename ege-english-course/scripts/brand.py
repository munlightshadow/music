"""Фирменный стиль «Английский Маяк» — цвета дизайнера и пути к логотипу."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAND_DIR = ROOT / "brand"

# Палитра из файла дизайнера (порядок как на свотчах).
TEAL_DARK = (0x21, 0x41, 0x49)  # #214149
SKY = (0xA5, 0xD2, 0xDF)  # #A5D2DF
TEAL = (0x46, 0x8A, 0x9D)  # #468A9D
CHARCOAL = (0x49, 0x4F, 0x55)  # #494F55
STEEL = (0xA8, 0xB2, 0xBB)  # #A8B2BB
GOLD = (0xC1, 0x9B, 0x4F)  # #C19B4F
WHITE = (0xFF, 0xFF, 0xFF)
GOLD_LIGHT = (0xF3, 0xD5, 0x93)  # #F3D593
TEAL_MID = (0x48, 0x8D, 0xA0)  # #488DA0
TEAL_DEEP = (0x1A, 0x33, 0x3A)  # #1A333A

INK = CHARCOAL
MUTED = (0x70, 0x78, 0x7C)
PAGE = STEEL
KIM_BG = (0xF3, 0xF7, 0xF8)
TH_BG = (0xE4, 0xF1, 0xF4)
BORDER = (0xC5, 0xD0, 0xD4)
OK = (0x2F, 0x6F, 0x5A)
BAD = (0xA3, 0x3B, 0x32)

NAME = "Английский Маяк"
TAGLINE = "подготовка к ОГЭ и ЕГЭ по английскому"
COURSE = "Курс подготовки к ЕГЭ по английскому"

LOGO_ICON_SVG = BRAND_DIR / "logo-icon.svg"
LOGO_ROW_SVG = BRAND_DIR / "logo-row.svg"
LOGO_STACK_SVG = BRAND_DIR / "logo-stack.svg"
LOGO_ICON_PNG = BRAND_DIR / "logo-icon.png"
LOGO_ROW_PNG = BRAND_DIR / "logo-row.png"
LOGO_STACK_PNG = BRAND_DIR / "logo-stack.png"


def hex_of(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def css_vars() -> str:
    return f"""
  --teal-dark: {hex_of(TEAL_DARK)};
  --sky: {hex_of(SKY)};
  --teal: {hex_of(TEAL)};
  --charcoal: {hex_of(CHARCOAL)};
  --steel: {hex_of(STEEL)};
  --gold: {hex_of(GOLD)};
  --gold-light: {hex_of(GOLD_LIGHT)};
  --teal-mid: {hex_of(TEAL_MID)};
  --teal-deep: {hex_of(TEAL_DEEP)};
  --white: {hex_of(WHITE)};
  --ink: {hex_of(INK)};
  --muted: {hex_of(MUTED)};
  --rule: {hex_of(STEEL)};
  --head: {hex_of(TH_BG)};
  --code-bg: {hex_of(KIM_BG)};
""".strip(
        "\n"
    )
