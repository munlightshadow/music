#!/usr/bin/env python3
"""Собрать вводный модуль в редактируемый PPTX 16:9 из тех же HTML-слайдов, что и PDF."""

from __future__ import annotations

import html as html_lib
import shutil
import sys
from pathlib import Path

from lxml import html as lhtml
from lxml.html import HtmlElement
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt
from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from intro_student_presentation import slides, IMG_DIR  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT_STUDENT = ROOT / "03-curriculum" / "intro-student" / "вводный-модуль.pptx"
OUT_PDF_DIR = ROOT / "pdf" / "03-curriculum" / "intro-student"

W, H = 13.333, 7.5
TEAL = (14, 138, 138)
TEAL_DARK = (14, 95, 95)
ORANGE = (224, 122, 47)
DARK = (34, 34, 34)
MUTED = (92, 101, 112)
PAGE = (122, 131, 140)
WHITE = (255, 255, 255)
GOOD = (27, 127, 78)
BAD = (180, 35, 24)
KIM_BG = (244, 247, 247)
OK_BG = (243, 248, 245)
BAD_BG = (253, 244, 243)
EX_BG = (247, 247, 244)
TH_BG = (231, 243, 243)
ROW_BG = (250, 252, 252)
BORDER = (197, 208, 208)


def rgb(t):
    return RGBColor(int(t[0]), int(t[1]), int(t[2]))


def set_run_font(run, size, color, bold=False, italic=False, name="Calibri"):
    run.font.size = Pt(size)
    run.font.color.rgb = rgb(color)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", name)


def add_rect(slide, x, y, w, h, fill):
    sh = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    sh.fill.solid()
    sh.fill.fore_color.rgb = rgb(fill)
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def add_round(slide, x, y, w, h, fill):
    sh = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    sh.fill.solid()
    sh.fill.fore_color.rgb = rgb(fill)
    sh.line.fill.background()
    try:
        sh.adjustments[0] = 0.5
    except Exception:
        pass
    sh.shadow.inherit = False
    return sh


def add_box(slide, x, y, w, h, fill, accent):
    """Card with a left accent bar."""
    add_rect(slide, x, y, w, h, fill)
    add_rect(slide, x, y, 0.07, h, accent)


def deco_bars(slide):
    add_rect(slide, 0, 0, W, 0.10, TEAL)
    add_rect(slide, 0, 0.145, W, 0.032, TEAL)
    add_rect(slide, 0, H - 0.10, W, 0.10, TEAL)
    add_rect(slide, 0, H - 0.177, W, 0.032, TEAL)


def footer(slide, n, total):
    add_text(slide, 0.70, H - 0.42, 9.6, 0.24, "Вводный модуль · курс подготовки к ЕГЭ", 10, PAGE)
    add_text(slide, W - 1.85, H - 0.42, 1.15, 0.24, f"{n} / {total}", 11, PAGE, align=PP_ALIGN.RIGHT)


def add_text(
    slide,
    x,
    y,
    w,
    h,
    text,
    size=18,
    color=DARK,
    bold=False,
    italic=False,
    align=PP_ALIGN.LEFT,
    anchor=MSO_ANCHOR.TOP,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    try:
        tf._txBody.bodyPr.set("anchor", {MSO_ANCHOR.TOP: "t", MSO_ANCHOR.MIDDLE: "ctr", MSO_ANCHOR.BOTTOM: "b"}[anchor])
    except Exception:
        pass
    lines = text.replace("\xa0", " ").split("\n") or [""]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(4) if len(lines) > 1 else Pt(0)
        p.clear()
        run = p.add_run()
        run.text = line if line else " "
        set_run_font(run, size, color, bold, italic)
    return box


def add_runs_to_paragraph(p, runs, size, default_color=DARK):
    p.clear()
    if not runs:
        run = p.add_run()
        run.text = " "
        set_run_font(run, size, default_color)
        return
    for text, bold, italic, color in runs:
        run = p.add_run()
        run.text = text
        set_run_font(run, size, color or default_color, bold, italic)


def inline_runs(node: HtmlElement, bold=False, italic=False, code=False):
    """Flatten an HTML node into (text, bold, italic, color) runs."""
    out: list[tuple[str, bool, bool, tuple | None]] = []
    if node.text:
        color = TEAL_DARK if code else None
        out.append((node.text, bold or code, italic, color))
    for child in node:
        tag = child.tag.lower() if isinstance(child.tag, str) else ""
        if tag == "br":
            out.append(("\n", False, False, None))
        elif tag in ("b", "strong"):
            out.extend(inline_runs(child, bold=True, italic=italic, code=code))
        elif tag in ("i", "em"):
            out.extend(inline_runs(child, bold=bold, italic=True, code=code))
        elif tag == "code":
            out.extend(inline_runs(child, bold=True, italic=italic, code=True))
        else:
            out.extend(inline_runs(child, bold=bold, italic=italic, code=code))
        if child.tail:
            out.append((child.tail, bold, italic, None))
    return out


def node_text(node: HtmlElement) -> str:
    if node is None:
        return ""
    return html_lib.unescape(" ".join(node.text_content().replace("\n", " ").split()))


def node_multiline(node: HtmlElement) -> str:
    if node is None:
        return ""
    raw = html_lib.unescape(node.text_content())
    lines = [line.rstrip() for line in raw.splitlines()]
    return "\n".join(lines).strip("\n")


def parse_root(fragment: str) -> HtmlElement:
    root = lhtml.fromstring(f"<root>{fragment}</root>")
    for br in root.xpath(".//br"):
        br.tail = "\n" + (br.tail or "")
    return root


def add_rich_textbox(slide, x, y, w, h, runs, size, color=DARK, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    # Split on explicit newlines into paragraphs
    paras: list[list] = [[]]
    for text, bold, italic, c in runs:
        parts = text.split("\n")
        for i, part in enumerate(parts):
            if i:
                paras.append([])
            if part:
                paras[-1].append((part, bold, italic, c))
    for i, pruns in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(0)
        add_runs_to_paragraph(p, pruns, size, color)
    return box


def add_table(slide, x, y, w, h, headers, rows, font=12):
    data = [headers] + rows
    rcount, ccount = len(data), len(data[0])
    tbl_shape = slide.shapes.add_table(rcount, ccount, Inches(x), Inches(y), Inches(w), Inches(h))
    table = tbl_shape.table
    widths = [Emu(int(Inches(w) * share)) for share in _col_shares(headers, ccount)]
    leftover = Inches(w) - sum(widths)
    widths[-1] = widths[-1] + leftover
    for c, width in enumerate(widths):
        table.columns[c].width = width
    for r, row in enumerate(data):
        for c, cell_text in enumerate(row):
            cell = table.cell(r, c)
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            p.clear()
            run = p.add_run()
            run.text = str(cell_text)
            header = r == 0
            set_run_font(run, font, TEAL_DARK if header else DARK, bold=header)
            cell.text_frame.word_wrap = True
            fill = TH_BG if header else (ROW_BG if r % 2 == 0 else WHITE)
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(fill)
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
                ln = etree.SubElement(tcPr, qn(tag))
                ln.set("w", "6350")
                sf = etree.SubElement(ln, qn("a:solidFill"))
                srgb = etree.SubElement(sf, qn("a:srgbClr"))
                srgb.set("val", "C5D0D0")
    return table


def _col_shares(headers, n):
    joined = " ".join(headers).lower()
    if n == 4 and "баллы" in joined:
        return [0.18, 0.38, 0.16, 0.28]
    if n == 3 and "ошибка" in joined:
        return [0.14, 0.48, 0.38]
    if n == 3:
        return [0.16, 0.46, 0.38]
    if n == 4:
        return [0.20, 0.18, 0.32, 0.30]
    return [1 / n] * n


def cover_slide(slide, root, n, total):
    deco_bars(slide)
    h1 = root.find(".//h1")
    ps = root.findall(".//p")
    add_text(slide, 0.9, 2.15, 11.5, 1.3, node_text(h1).upper(), 34, ORANGE, True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    y = 3.55
    for p in ps:
        add_text(slide, 1.2, y, 10.9, 0.55, node_text(p), 16, DARK, align=PP_ALIGN.CENTER)
        y += 0.5
    footer(slide, n, total)


def section_slide(slide, root, n, total):
    deco_bars(slide)
    num = root.find(".//div[@class='num']")
    h1 = root.find(".//h1")
    muted = root.find(".//p")
    title = "\n".join(t.strip() for t in node_multiline(h1).splitlines() if t.strip())
    add_text(slide, 0.85, 2.15, 11.6, 0.4, node_text(num).upper(), 14, ORANGE, True)
    add_text(slide, 0.85, 2.55, 11.6, 1.8, title, 36, TEAL, True)
    if muted is not None and node_text(muted):
        add_text(slide, 0.85, 4.55, 11.6, 0.8, node_text(muted), 16, MUTED)
    footer(slide, n, total)


def big_slide(slide, root, n, total):
    deco_bars(slide)
    number = node_text(root.find(".//div[@class='n']"))
    caption = node_multiline(root.find(".//p"))
    add_text(slide, 0.7, 1.85, 12.0, 1.6, number, 68, TEAL, True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, 1.3, 3.7, 10.7, 1.6, caption, 18, DARK, align=PP_ALIGN.CENTER)
    footer(slide, n, total)


def content_slide(slide, root, n, total):
    deco_bars(slide)
    h1 = root.find("./h1")
    body = root.find("./div")
    small = body is not None and (body.get("class") or "") == "small"
    title = node_text(h1)
    title_size = 22 if small or len(title) > 48 else 26
    add_text(slide, 0.70, 0.32, 12.0, 0.72 if len(title) > 42 else 0.55, title, title_size, TEAL, True)

    y = 1.05 if len(title) > 42 else 0.95
    bottom = 6.95
    blocks = list(body) if body is not None else []
    # If body has leading text, ignore — all content is in children
    layout_blocks(slide, blocks, 0.70, y, 11.93, bottom, small)
    footer(slide, n, total)


def layout_blocks(slide, blocks, x, y, w, bottom, small):
    if not blocks:
        return
    remaining = max(0.4, bottom - y)
    kinds = [_kind(b) for b in blocks]
    weights = []
    for k in kinds:
        if k == "table":
            weights.append(2.4)
        elif k in ("kim", "example", "shots", "img"):
            weights.append(3.6)
        elif k == "ul":
            weights.append(2.0)
        elif k == "tag":
            weights.append(0.42)
        elif k == "p":
            weights.append(0.45)
        else:
            weights.append(0.6)
    total_w = sum(weights) or 1
    # Leave 0.08in gaps between blocks
    gaps = 0.10 * max(0, len(blocks) - 1)
    usable = remaining - gaps
    heights = [usable * (wt / total_w) for wt in weights]
    # Minimums
    mins = []
    for k in kinds:
        if k == "tag":
            mins.append(0.34)
        elif k == "p":
            mins.append(0.32)
        elif k == "ul":
            mins.append(0.9)
        elif k == "table":
            mins.append(1.4)
        elif k in ("shots", "img"):
            mins.append(3.2)
        else:
            mins.append(1.1)
    # Redistribute if mins overflow
    for i, mn in enumerate(mins):
        heights[i] = max(heights[i], mn)
    extra = sum(heights) + gaps - remaining
    if extra > 0:
        flex = [i for i, k in enumerate(kinds) if k in ("kim", "example", "ul", "table", "shots", "img")]
        if flex:
            cut = extra / len(flex)
            for i in flex:
                heights[i] = max(mins[i], heights[i] - cut)

    cy = y
    for block, kind, hgt in zip(blocks, kinds, heights):
        hgt = min(hgt, bottom - cy)
        if hgt < 0.25:
            break
        draw_block(slide, block, kind, x, cy, w, hgt, small)
        cy += hgt + 0.10


def _kind(block: HtmlElement) -> str:
    tag = block.tag.lower() if isinstance(block.tag, str) else ""
    cls = block.get("class") or ""
    classes = cls.split()
    if tag == "table":
        return "table"
    if tag == "ul":
        return "ul"
    if tag == "pre" or "kim" in classes:
        return "kim"
    if tag == "div" and "example" in classes:
        return "example"
    if tag == "span" and "tag" in classes:
        return "tag"
    if tag == "img":
        return "img"
    if tag == "div" and "shots" in classes:
        return "shots"
    if tag == "p":
        return "p"
    return "other"


def draw_block(slide, block, kind, x, y, w, h, small):
    if kind == "ul":
        draw_ul(slide, block, x, y, w, h, small)
    elif kind == "table":
        draw_table_block(slide, block, x, y, w, h, small)
    elif kind == "kim":
        draw_kim(slide, block, x, y, w, h, small)
    elif kind == "example":
        draw_example(slide, block, x, y, w, h)
    elif kind == "tag":
        draw_tag(slide, block, x, y)
    elif kind == "p":
        draw_p(slide, block, x, y, w, h, small)
    elif kind in ("img", "shots"):
        draw_shots(slide, block, x, y, w, h)
    else:
        text = node_text(block)
        if text:
            add_text(slide, x, y, w, h, text, 13 if small else 15, DARK)


def draw_ul(slide, block, x, y, w, h, small):
    items = block.findall("./li")
    n = max(len(items), 1)
    row_h = min(0.78, h / n)
    size = 13 if small or n >= 7 else (14 if n >= 6 else 16)
    if n >= 8:
        size = 12
    cy = y
    for li in items:
        runs = inline_runs(li)
        # prefix bullet
        box = slide.shapes.add_textbox(Inches(x), Inches(cy), Inches(w), Inches(row_h))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.level = 0
        p.space_after = Pt(4)
        # bullet via run
        bullet_run = [("•  ", False, False, TEAL)] + runs
        add_runs_to_paragraph(p, _flatten_runs(bullet_run), size, DARK)
        cy += row_h


def _flatten_runs(runs):
    out = []
    for text, bold, italic, color in runs:
        if "\n" in text:
            # keep as is; paragraph helper splits? we already put in one p
            text = text.replace("\n", " ")
        out.append((text, bold, italic, color))
    return out


def draw_table_block(slide, block, x, y, w, h, small):
    headers = [node_text(th) for th in block.findall(".//th")]
    rows = [[node_text(td) for td in tr.findall("./td")] for tr in block.findall(".//tbody/tr")]
    if not headers:
        first = block.find(".//tr")
        if first is not None:
            headers = [node_text(c) for c in first]
            rows = [[node_text(td) for td in tr.findall("./td") or list(tr)] for tr in block.findall(".//tr")[1:]]
    n_rows = 1 + len(rows)
    table_h = min(h, 0.42 * n_rows + 0.08)
    add_table(slide, x, y, w, table_h, headers, rows, font=11 if small else 12)


def draw_kim(slide, block, x, y, w, h, small):
    add_box(slide, x, y, w, h, KIM_BG, TEAL)
    text = node_multiline(block)
    size = 10 if small or text.count("\n") > 14 else 11
    add_multiline(slide, x + 0.18, y + 0.10, w - 0.28, h - 0.18, text, size, DARK)


def draw_example(slide, block, x, y, w, h):
    classes = (block.get("class") or "").split()
    if "ok" in classes:
        bg, accent = OK_BG, GOOD
    elif "bad" in classes:
        bg, accent = BAD_BG, BAD
    else:
        bg, accent = EX_BG, ORANGE
    add_box(slide, x, y, w, h, bg, accent)
    text = node_multiline(block)
    size = 10 if text.count("\n") > 10 or len(text) > 700 else 11
    add_multiline(slide, x + 0.18, y + 0.10, w - 0.28, h - 0.18, text, size, DARK)


def draw_tag(slide, block, x, y):
    classes = (block.get("class") or "").split()
    fill = GOOD if "good" in classes else BAD if "bad" in classes else TEAL
    text = node_text(block)
    width = min(11.5, 0.11 * max(len(text), 12) + 0.45)
    add_round(slide, x, y, width, 0.32, fill)
    add_text(slide, x + 0.08, y + 0.02, width - 0.12, 0.28, text, 11, WHITE, True, anchor=MSO_ANCHOR.MIDDLE)


def draw_p(slide, block, x, y, w, h, small):
    classes = (block.get("class") or "").split()
    color = MUTED if "muted" in classes or "credit" in classes else DARK
    size = 11 if "credit" in classes else (12 if small or "muted" in classes else 14)
    runs = inline_runs(block)
    add_rich_textbox(slide, x, y, w, h, runs, size, color)


def draw_shots(slide, block, x, y, w, h):
    from PIL import Image as PILImage

    if block.tag == "img":
        srcs = [block.get("src") or ""]
    else:
        srcs = [img.get("src") or "" for img in block.findall(".//img")]
    paths = []
    for src in srcs:
        name = Path(src).name
        path = IMG_DIR / name
        if path.exists():
            paths.append(path)
    if not paths:
        return
    gap = 0.12
    n = len(paths)
    cell_w = (w - gap * (n - 1)) / n
    for i, path in enumerate(paths):
        with PILImage.open(path) as im:
            iw, ih = im.size
        box_w, box_h = cell_w, h
        img_aspect = iw / ih if ih else 1
        box_aspect = box_w / box_h if box_h else 1
        if img_aspect > box_aspect:
            nw, nh = box_w, box_w / img_aspect
        else:
            nw, nh = box_h * img_aspect, box_h
        ox = x + i * (cell_w + gap) + (cell_w - nw) / 2
        oy = y + (h - nh) / 2
        slide.shapes.add_picture(str(path), Inches(ox), Inches(oy), Inches(nw), Inches(nh))


def add_multiline(slide, x, y, w, h, text, size, color):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(1)
        p.space_before = Pt(0)
        p.clear()
        run = p.add_run()
        run.text = line if line else " "
        set_run_font(run, size, color, name="Calibri")
    return box


def render(fragment: str, prs: Presentation, n: int, total: int):
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    # white background
    add_rect(slide, 0, 0, W, H, WHITE)
    root = parse_root(fragment)
    if root.find(".//div[@class='cover']") is not None:
        cover_slide(slide, root.find(".//div[@class='cover']"), n, total)
    elif root.find(".//div[@class='section']") is not None:
        section_slide(slide, root.find(".//div[@class='section']"), n, total)
    elif root.find(".//div[@class='big']") is not None:
        big_slide(slide, root.find(".//div[@class='big']"), n, total)
    else:
        content_slide(slide, root, n, total)


def build(path: Path) -> int:
    specs = slides()
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    total = len(specs)
    for i, fragment in enumerate(specs, 1):
        render(fragment, prs, i, total)
    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(path))
    return total


def main():
    n = build(OUT_STUDENT)
    OUT_PDF_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT_STUDENT, OUT_PDF_DIR / OUT_STUDENT.name)
    print(f"OK  {OUT_STUDENT.relative_to(ROOT)}  ({n} slides)")
    print(f"OK  {(OUT_PDF_DIR / OUT_STUDENT.name).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
