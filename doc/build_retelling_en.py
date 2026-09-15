#!/usr/bin/env python3
"""Build the English retelling DOCX from ODNKNR_5_klass_retelling_en.txt."""

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
}

H2 = {
    "How this retelling is arranged",
    "Contents of the retelling",
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

TOC_ITEMS = [
    "Part I. Introduction and Russia’s culture as a dialogue of peoples",
    "    An address to fifth-graders and the textbook’s symbols",
    "    What culture is",
    "    Russia’s culture as a dialogue among the cultures of different peoples",
    "    The human being as creator and bearer of culture",
    "    Figures canonized as Orthodox saints",
    "    The moral culture of the person and of society",
    "    Conscience, justice, and the intelligentsia",
    "Part II. Patriotism, humanism, religions, labor, intellect",
    "    Patriotism as a citizen’s moral feeling",
    "    Humanism, mercy, and charity",
    "    Religion and morality in Russia’s traditional religions",
    "    Labor as a universal human value",
    "    The intellectual culture of Russian society",
    "Part III. Aesthetic culture",
    "    Aesthetic values and the arts",
    "    Folk art and ornament",
    "    Aesthetics born of religion: church, icon, mosque",
    "    The course in one closing thought",
]


def set_run_font(run, name="Times New Roman", size=14, bold=False, italic=False, color=None):
    run.bold = bold
    run.italic = italic
    run.font.name = name
    run.font.size = Pt(size)
    r = run._element
    rPr = r.get_or_add_rPr()
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


def add_heading_styled(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18 if level == 1 else 14)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    size = {1: 18, 2: 16, 3: 14}[level]
    color = RGBColor(0x8B, 0x1A, 0x1A) if level == 1 else RGBColor(0x4A, 0x2C, 0x0A)
    run = p.add_run(text)
    set_run_font(run, size=size, bold=True, color=color)
    return p


def add_body(doc, text, first_line=True, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.15
    if first_line:
        p.paragraph_format.first_line_indent = Cm(1.25)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    set_run_font(run, size=14, italic=italic)
    return p


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(12)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_run_font(run, size=12, italic=True, color=RGBColor(0x55, 0x55, 0x55))
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if p.runs:
        p.runs[0].text = text
        set_run_font(p.runs[0], size=14)
    else:
        run = p.add_run(text)
        set_run_font(run, size=14)
    return p


def load_body_lines():
    text = SRC.read_text(encoding="utf-8-sig")
    marker = "=" * 80
    if marker in text:
        text = text.split(marker, 1)[1]
    lines = [ln.rstrip() for ln in text.strip().splitlines()]
    return [ln for ln in lines if ln.strip()]


def add_title_page(doc):
    for _ in range(3):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Foundations of the Spiritual and Moral Culture\nof the Peoples of Russia")
    set_run_font(run, size=26, bold=True, color=RGBColor(0x8B, 0x1A, 0x1A))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Grade 5")
    set_run_font(run, size=20, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    run = p.add_run("A retelling of the textbook in the author’s own words")
    set_run_font(run, size=16, italic=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    run = p.add_run(
        "Based on N. F. Vinogradova’s textbook\n"
        "“Foundations of the Spiritual and Moral Culture of the Peoples of Russia.” Grade 5.\n"
        "2nd stereotyped edition. Moscow: Prosveshcheniye, 2022."
    )
    set_run_font(run, size=12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(36)
    run = p.add_run(
        "This is not a copy of the textbook. It is an independent retelling of its ideas "
        "and stories, following the three parts of the scan in order "
        "(pages 1–30, 31–60, and 61–72)."
    )
    set_run_font(run, size=12, italic=True, color=RGBColor(0x44, 0x44, 0x44))


def add_front_matter(doc, how_arranged):
    doc.add_page_break()
    add_heading_styled(doc, "How this retelling is arranged", 1)
    add_body(doc, how_arranged)

    add_heading_styled(doc, "Contents of the retelling", 1)
    for item in TOC_ITEMS:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.left_indent = Cm(0 if not item.startswith("    ") else 1)
        run = p.add_run(item.strip())
        set_run_font(run, size=13, bold=item.startswith("Part "))


def main():
    lines = load_body_lines()

    # Skip title-page lines already hardcoded; keep the "How this retelling" paragraph.
    how_arranged = None
    start = 0
    for i, ln in enumerate(lines):
        if ln == "How this retelling is arranged":
            how_arranged = lines[i + 1]
            # Skip through contents list until first Part I body heading block
            for j in range(i + 2, len(lines)):
                if lines[j].startswith("Part I.") and j > i + 5:
                    # The TOC also starts with Part I; the body Part I is the second occurrence
                    # after "Contents of the retelling"
                    start = j
                    break
            break

    # Find the second "Part I." — first is in contents
    part_hits = [idx for idx, ln in enumerate(lines) if ln.startswith("Part I.")]
    if len(part_hits) >= 2:
        start = part_hits[1]
    elif part_hits:
        start = part_hits[0]

    if how_arranged is None:
        raise SystemExit("Could not find the front-matter paragraph")

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2)
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)

    add_title_page(doc)
    add_front_matter(doc, how_arranged)

    in_glossary = False
    for ln in lines[start:]:
        if ln in H1:
            doc.add_page_break()
            add_heading_styled(doc, ln, 1)
            in_glossary = False
            continue
        if ln.startswith("From the ") and "scan" in ln:
            add_caption(doc, ln)
            continue
        if ln in H2:
            add_heading_styled(doc, ln, 2)
            in_glossary = ln == "A short glossary of the retelling"
            continue
        if ln == "End of the retelling":
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(24)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run("End of the retelling")
            set_run_font(run, size=12, italic=True, color=RGBColor(0x66, 0x66, 0x66))
            continue
        if in_glossary and " — " in ln and not ln.startswith("At the end"):
            add_bullet(doc, ln)
            continue
        add_body(doc, ln)

    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
