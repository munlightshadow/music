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

    core = doc.core_properties
    core.author = ""
    core.last_modified_by = ""
    core.comments = ""
    core.title = (
        "Foundations of the Spiritual and Moral Culture of the Peoples of Russia. "
        "Grade 5. A retelling"
    )

    doc.save(OUT)
    strip_word_locks(OUT)
    write_rtf(ROOT / "ODNKNR_5_klass_retelling_en.rtf", lines)
    print("saved", OUT, "paragraphs", len(doc.paragraphs))


def strip_word_locks(path: Path) -> None:
    """Remove thumbnail/customXml leftovers and any protection flags Word may honor."""
    import io
    import zipfile
    from datetime import datetime, timezone
    from lxml import etree

    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    EP = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
    CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
    DCTERMS = "http://purl.org/dc/terms/"
    REL = "http://schemas.openxmlformats.org/package/2006/relationships"
    CT = "http://schemas.openxmlformats.org/package/2006/content-types"

    skip = {
        "docProps/thumbnail.jpeg",
        "word/stylesWithEffects.xml",
        "customXml/item1.xml",
        "customXml/itemProps1.xml",
        "customXml/_rels/item1.xml.rels",
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            name = info.filename
            if name in skip or name.startswith("customXml/"):
                continue
            data = zin.read(name)

            if name == "word/settings.xml":
                root = etree.fromstring(data)
                for tag in (
                    f"{{{W}}}documentProtection",
                    f"{{{W}}}writeProtection",
                    f"{{{W}}}revisionView",
                    f"{{{W}}}savePreviewPicture",
                ):
                    for el in root.findall(tag):
                        root.remove(el)
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

            elif name == "docProps/app.xml":
                root = etree.fromstring(data)
                ns = {"ep": EP}
                app = root.find("ep:Application", ns)
                if app is not None:
                    app.text = "Microsoft Office Word"
                sec = root.find("ep:DocSecurity", ns)
                if sec is not None:
                    sec.text = "0"
                else:
                    el = etree.SubElement(root, f"{{{EP}}}DocSecurity")
                    el.text = "0"
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

            elif name == "docProps/core.xml":
                root = etree.fromstring(data)
                now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                for tag in (f"{{{DCTERMS}}}created", f"{{{DCTERMS}}}modified"):
                    el = root.find(tag)
                    if el is not None:
                        el.text = now
                desc = root.find("{http://purl.org/dc/elements/1.1/}description")
                if desc is not None:
                    desc.text = ""
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

            elif name == "_rels/.rels":
                root = etree.fromstring(data)
                for rel in list(root):
                    target = rel.get("Target", "")
                    if "thumbnail" in target:
                        root.remove(rel)
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

            elif name == "word/_rels/document.xml.rels":
                root = etree.fromstring(data)
                for rel in list(root):
                    target = rel.get("Target", "")
                    rtype = rel.get("Type", "")
                    if "customXml" in target or "stylesWithEffects" in target or "customXml" in rtype:
                        root.remove(rel)
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

            elif name == "[Content_Types].xml":
                root = etree.fromstring(data)
                for el in list(root):
                    part = el.get("PartName", "")
                    if "customXml" in part or "stylesWithEffects" in part or part.endswith("thumbnail.jpeg"):
                        root.remove(el)
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

            zout.writestr(name, data)

    path.write_bytes(buf.getvalue())


def rtf_escape(text: str) -> str:
    out = []
    for ch in text:
        o = ord(ch)
        if ch in "\\{}":
            out.append("\\" + ch)
        elif ch == "\n":
            out.append("\\par\n")
        elif o < 128:
            out.append(ch)
        else:
            signed = o if o <= 32767 else o - 65536
            out.append(f"\\u{signed}?")
    return "".join(out)


def write_rtf(path: Path, lines: list[str]) -> None:
    parts = [
        r"{\rtf1\ansi\deff0\nouicompat",
        r"{\fonttbl{\f0 Times New Roman;}}",
        r"\viewkind4\uc1\pard\sa160\sl276\slmult1\f0\fs28 ",
    ]
    for ln in lines:
        parts.append(rtf_escape(ln) + r"\par" + "\n")
    parts.append("}\n")
    path.write_text("".join(parts), encoding="ascii", errors="strict")
    print("saved", path)


if __name__ == "__main__":
    main()
    ru = ROOT / "ODNKNR_5_klass_pereskaz.docx"
    if ru.exists():
        strip_word_locks(ru)
        print("unlocked", ru)
