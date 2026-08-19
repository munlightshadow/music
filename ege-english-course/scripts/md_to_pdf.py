#!/usr/bin/env python3
"""Convert ege-english-course Markdown/YAML sources to print PDFs via HTML + Chrome."""

from __future__ import annotations

import html
import os
import re
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "pdf"
CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")
CHROME_PROFILE = Path("/tmp/ege-chrome-pdf-profile")

LANDSCAPE = {
    "03-curriculum/module-index.md",
    "03-curriculum/russia-strand.md",
    "03-curriculum/phonetics-strand.md",
    "03-curriculum/solutions-mapping.md",
    "03-curriculum/cumulative-checklist.md",
    "curriculum.yaml",
    "02-content-spec/tested-vs-not-tested.md",
    "02-content-spec/grammar.md",
}

CSS = """
:root {
  --ink: #1a1a1a;
  --muted: #555;
  --rule: #c8c8c8;
  --head: #f3f3f3;
  --code-bg: #f6f6f6;
}
* { box-sizing: border-box; }
html, body {
  margin: 0;
  padding: 0;
  color: var(--ink);
  font-family: "Liberation Serif", "Noto Serif", "DejaVu Serif", "Times New Roman", serif;
  font-size: 11pt;
  line-height: 1.45;
}
.page {
  padding: 0;
}
.banner {
  font-family: "Liberation Sans", "Noto Sans", "DejaVu Sans", sans-serif;
  font-size: 8.5pt;
  color: var(--muted);
  border-bottom: 1px solid var(--rule);
  padding-bottom: 8px;
  margin-bottom: 16px;
}
.banner .src { word-break: break-all; }
h1, h2, h3, h4 {
  font-family: "Liberation Sans", "Noto Sans", "DejaVu Sans", sans-serif;
  line-height: 1.25;
  page-break-after: avoid;
}
h1 { font-size: 20pt; margin: 0 0 14px; }
h2 { font-size: 14pt; margin: 22px 0 8px; border-bottom: 1px solid var(--rule); padding-bottom: 3px; }
h3 { font-size: 12pt; margin: 16px 0 6px; }
h4 { font-size: 11pt; margin: 12px 0 4px; }
p, ul, ol { margin: 0 0 8px; }
li { margin: 0 0 3px; }
a { color: inherit; text-decoration: underline; }
code, pre, .yaml, .mermaid {
  font-family: "JetBrains Mono", "DejaVu Sans Mono", "Liberation Mono", monospace;
}
code {
  font-size: 0.88em;
  background: var(--code-bg);
  padding: 0.05em 0.28em;
  border-radius: 3px;
}
pre {
  background: var(--code-bg);
  border: 1px solid var(--rule);
  padding: 8px 10px;
  font-size: 8.5pt;
  line-height: 1.35;
  white-space: pre-wrap;
  word-break: break-word;
  page-break-inside: auto;
}
.mermaid {
  background: #fafafa;
  border: 1px dashed var(--rule);
  padding: 10px 12px;
  font-size: 9pt;
  white-space: pre-wrap;
  margin: 0 0 12px;
}
.mermaid-label {
  font-family: "Liberation Sans", "Noto Sans", sans-serif;
  font-size: 8pt;
  color: var(--muted);
  margin-bottom: 4px;
}
table {
  border-collapse: collapse;
  width: 100%;
  margin: 0 0 14px;
  font-size: 8.5pt;
  page-break-inside: auto;
}
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th, td {
  border: 1px solid #bbb;
  padding: 4px 6px;
  vertical-align: top;
  text-align: left;
}
th {
  background: var(--head);
  font-family: "Liberation Sans", "Noto Sans", "DejaVu Sans", sans-serif;
  font-weight: 600;
}
blockquote {
  margin: 0 0 10px;
  padding: 4px 0 4px 12px;
  border-left: 3px solid #888;
  color: #333;
}
hr { border: 0; border-top: 1px solid var(--rule); margin: 16px 0; }
.doc-break { page-break-before: always; }
@page {
  size: A4 portrait;
  margin: 14mm 12mm 16mm 12mm;
}
"""

CSS_LANDSCAPE = CSS.replace(
    "size: A4 portrait;\n  margin: 14mm 12mm 16mm 12mm;",
    "size: A4 landscape;\n  margin: 12mm 10mm 14mm 10mm;",
) + "\ntable { font-size: 8pt; }\n"


def relativize(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def collect_sources() -> list[Path]:
    files: list[Path] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = relativize(path)
        if rel.startswith("pdf/") or rel.startswith("scripts/"):
            continue
        if path.suffix.lower() in {".md", ".yaml", ".yml"}:
            files.append(path)
    return files


def mermaid_to_html(match: re.Match[str]) -> str:
    body = html.escape(match.group(1).strip("\n"))
    return (
        '<div class="mermaid-wrap">'
        '<div class="mermaid-label">Схема (исходник Mermaid)</div>'
        f'<pre class="mermaid">{body}</pre>'
        "</div>"
    )


def md_to_html_body(text: str) -> str:
    text = re.sub(r"```mermaid\n(.*?)```", mermaid_to_html, text, flags=re.S)
    return markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
        output_format="html5",
    )


def wrap_document(title: str, source: str, body: str, landscape: bool) -> str:
    klass = "landscape" if landscape else "portrait"
    css = CSS_LANDSCAPE if landscape else CSS
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>{css}</style>
</head>
<body class="{klass}">
  <div class="page">
    <div class="banner">
      Курс подготовки к ЕГЭ по английскому · PDF-снимок исходника
      <div class="src">{html.escape(source)}</div>
    </div>
    {body}
  </div>
</body>
</html>
"""


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def source_to_html(path: Path) -> tuple[str, str, bool]:
    rel = relativize(path)
    raw = path.read_text(encoding="utf-8")
    landscape = rel in LANDSCAPE
    if path.suffix.lower() in {".yaml", ".yml"}:
        title = path.stem
        body = (
            f"<h1>{html.escape(title)}</h1>"
            f"<pre class='yaml'>{html.escape(raw)}</pre>"
        )
    else:
        title = first_heading(raw, path.stem)
        body = f"<h1>{html.escape(title)}</h1>" + md_to_html_body(
            re.sub(r"^# .+\n+", "", raw, count=1)
        )
    html_doc = wrap_document(title, rel, body, landscape)
    return html_doc, title, landscape


def chrome_pdf(html_path: Path, pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    CHROME_PROFILE.mkdir(parents=True, exist_ok=True)
    cmd = [
        CHROME,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--no-first-run",
        "--no-default-browser-check",
        "--no-pdf-header-footer",
        f"--user-data-dir={CHROME_PROFILE}",
        f"--print-to-pdf={pdf_path}",
        html_path.resolve().as_uri(),
    ]
    result = subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=60,
    )
    if result.returncode != 0 or not pdf_path.exists() or pdf_path.stat().st_size < 200:
        raise RuntimeError(
            f"Chrome failed for {pdf_path.name} (code {result.returncode})\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-4000:]}"
        )


def write_index(items: list[tuple[str, str]]) -> str:
    rows = "\n".join(
        f"<tr><td>{html.escape(src)}</td><td>{html.escape(title)}</td></tr>"
        for src, title in items
    )
    body = f"""
    <h1>PDF-версии файлов курса</h1>
    <p>Снимок всех Markdown- и YAML-файлов пакета <code>ege-english-course</code> на момент генерации.
    Исходники остаются главными; PDF — для чтения и печати.</p>
    <table>
      <thead><tr><th>Исходник</th><th>Заголовок</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """
    return wrap_document("PDF-версии файлов курса", "pdf/INDEX.pdf", body, False)


def main() -> int:
    tmp = Path("/tmp/ege-pdf-build")
    tmp.mkdir(exist_ok=True)
    sources = collect_sources()
    if not sources:
        print("No sources found", file=sys.stderr)
        return 1

    index_items: list[tuple[str, str]] = []
    combined_parts: list[str] = []

    for path in sources:
        rel = relativize(path)
        html_doc, title, landscape = source_to_html(path)
        html_path = tmp / (rel.replace("/", "__") + ".html")
        html_path.write_text(html_doc, encoding="utf-8")
        pdf_rel = Path(rel).with_suffix(".pdf")
        pdf_path = PDF_DIR / pdf_rel
        chrome_pdf(html_path, pdf_path)
        size = pdf_path.stat().st_size
        if size < 500:
            print(f"WARN small pdf: {pdf_rel} ({size} bytes)", file=sys.stderr)
        print(f"OK  {pdf_rel}  ({size} bytes)")
        index_items.append((rel, title))
        klass = "landscape" if landscape else "portrait"
        # Keep only inner page for combined file; re-wrap later.
        inner = re.search(r'<div class="page">(.*)</div>\s*</body>', html_doc, re.S)
        fragment = inner.group(1) if inner else html_doc
        combined_parts.append(
            f'<section class="doc-break {klass}"><div class="page">{fragment}</div></section>'
        )

    index_html = write_index(index_items)
    index_path = tmp / "INDEX.html"
    index_path.write_text(index_html, encoding="utf-8")
    chrome_pdf(index_path, PDF_DIR / "INDEX.pdf")
    print("OK  INDEX.pdf")

    combined = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Курс ЕГЭ по английскому — полный пакет</title>
  <style>{CSS}
    section.landscape table {{ font-size: 8pt; }}
    @page {{ size: A4 portrait; margin: 14mm 12mm 16mm 12mm; }}
  </style>
</head>
<body class="portrait">
{"".join(combined_parts)}
</body>
</html>
"""
    combined_html = tmp / "FULL.html"
    combined_html.write_text(combined, encoding="utf-8")
    chrome_pdf(combined_html, PDF_DIR / "_полный-пакет.pdf")
    print("OK  _полный-пакет.pdf")
    return 0


if __name__ == "__main__":
    sys.exit(main())
