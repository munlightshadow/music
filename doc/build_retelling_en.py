#!/usr/bin/env python3
"""Turn the English retelling .txt into a copyable Word .docx (1:1 paragraphs)."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "ODNKNR_5_klass_retelling_en.txt"
OUT = ROOT / "ODNKNR_5_klass_retelling_en.docx"

H1 = {
    "Part I. Introduction and Russia’s culture as a dialogue of peoples",
    "Part II. Patriotism, humanism, religions, labor, intellect",
    "Part III. Aesthetic culture",
    "How this retelling is arranged",
    "Contents of the retelling",
}

H2 = {
    "An address to fifth-graders and the textbook’s symbols",
    "What culture is",
    "Russia’s culture as a dialogue among the cultures of different peoples",
    "The human being as creator and bearer of culture",
    "Figures canonized as Orthodox saints",
    "The moral culture of the person and of society",
    "Conscience, justice, and the intelligentsia",
    "Patriotism as a citizen’s moral feeling",
    "Humanism, mercy, and charity",
    "Religion and morality in Russia’s traditional religions",
    "Labor as a universal human value",
    "The intellectual culture of Russian society",
    "Aesthetic values and the arts",
    "Folk art and ornament",
    "Aesthetics born of religion: church, icon, mosque",
    "The course in one closing thought",
    "A short glossary of the retelling",
}

TITLE_LINES = {
    "Foundations of the Spiritual and Moral Culture",
    "of the Peoples of Russia",
    "Grade 5",
}

TOC_ORDER = [
    "Part I. Introduction and Russia’s culture as a dialogue of peoples",
    "An address to fifth-graders and the textbook’s symbols",
    "What culture is",
    "Russia’s culture as a dialogue among the cultures of different peoples",
    "The human being as creator and bearer of culture",
    "Figures canonized as Orthodox saints",
    "The moral culture of the person and of society",
    "Conscience, justice, and the intelligentsia",
    "Part II. Patriotism, humanism, religions, labor, intellect",
    "Patriotism as a citizen’s moral feeling",
    "Humanism, mercy, and charity",
    "Religion and morality in Russia’s traditional religions",
    "Labor as a universal human value",
    "The intellectual culture of Russian society",
    "Part III. Aesthetic culture",
    "Aesthetic values and the arts",
    "Folk art and ornament",
    "Aesthetics born of religion: church, icon, mosque",
    "The course in one closing thought",
]


def set_run_font(run, name="Times New Roman", size=14, bold=False, italic=False, color=None):
    run.bold = bold
    run.italic = italic
    run.font.name = name
    run.font.size = Pt(size)
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        from lxml import etree

        rFonts = etree.SubElement(rPr, qn("w:rFonts"))
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:eastAsia"), name)
    rFonts.set(qn("w:cs"), name)
    if color is not None:
        run.font.color.rgb = color


def add_para(doc, text, *, size=14, bold=False, italic=False, center=False, color=None, space_before=0, space_after=8, indent=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = 1.15
    if indent:
        pf.first_line_indent = Cm(1.25)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    elif center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic, color=color)
    return p


def load_lines():
    text = SRC.read_text(encoding="utf-8-sig")
    marker = "=" * 80
    if marker in text:
        text = text.split(marker, 1)[1]
    return [ln.rstrip() for ln in text.strip().splitlines()]


def main():
    lines = load_lines()
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2)
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)

    burgundy = RGBColor(0x8B, 0x1A, 0x1A)
    brown = RGBColor(0x4A, 0x2C, 0x0A)
    gray = RGBColor(0x55, 0x55, 0x55)

    toc_index = 0
    for ln in lines:
        if not ln.strip():
            continue
        if toc_index < len(TOC_ORDER) and ln == TOC_ORDER[toc_index]:
            add_para(doc, ln, size=13, bold=ln.startswith("Part "), space_after=2)
            toc_index += 1
            continue
        if ln in TITLE_LINES:
            size = 22 if ln != "Grade 5" else 18
            add_para(doc, ln, size=size, bold=True, center=True, color=burgundy, space_before=6, space_after=6)
            continue
        if ln.startswith("A retelling of the textbook"):
            add_para(doc, ln, size=16, italic=True, center=True, space_before=12, space_after=12)
            continue
        if ln.startswith("Based on N. F.") or ln.startswith("“Foundations") or ln.startswith("2nd stereotyped"):
            add_para(doc, ln, size=12, center=True, space_after=4)
            continue
        if ln.startswith("This is not a copy"):
            add_para(doc, ln, size=12, italic=True, center=True, color=gray, space_before=12, space_after=18)
            continue
        if ln in H1:
            add_para(doc, ln, size=18, bold=True, color=burgundy, space_before=18, space_after=8)
            continue
        if ln in H2:
            add_para(doc, ln, size=16, bold=True, color=brown, space_before=14, space_after=8)
            continue
        if ln.startswith("From the ") and "scan" in ln:
            add_para(doc, ln, size=12, italic=True, center=True, color=gray, space_before=4, space_after=12)
            continue
        if ln == "End of the retelling":
            add_para(doc, ln, size=12, italic=True, center=True, color=gray, space_before=24, space_after=8)
            continue
        add_para(doc, ln, size=14, indent=True)

    doc.save(OUT)
    print("saved", OUT, "paragraphs", len(doc.paragraphs))


if __name__ == "__main__":
    main()
