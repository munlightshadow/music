#!/usr/bin/env python3
"""Собрать стартовые шаблоны PDF и PPTX с логотипом и палитрой бренда."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import (  # noqa: E402
    BRAND_DIR,
    COURSE,
    LOGO_ICON_PNG,
    LOGO_ROW_PNG,
    LOGO_STACK_ON_DARK_PNG,
    LOGO_STACK_PNG,
    NAME,
    ROOT,
    TAGLINE,
    hex_of,
    GOLD,
    GOLD_LIGHT,
    TEAL,
    TEAL_DARK,
    TEAL_DEEP,
    TEAL_MID,
)
from intro_student_pptx import TEMPLATE_OUT, write_pptx_template  # noqa: E402
from md_to_pdf import chrome_pdf, wrap_document, prepare_assets, TMP  # noqa: E402

PDF_TEMPLATE = BRAND_DIR / "шаблон-документа.pdf"


def write_pdf_template() -> Path:
    prepare_assets(TMP)
    for src in (LOGO_ROW_PNG, LOGO_ICON_PNG, LOGO_STACK_PNG, LOGO_STACK_ON_DARK_PNG):
        if src.exists():
            shutil.copy2(src, TMP / src.name)
    row = (TMP / LOGO_ROW_PNG.name).resolve().as_uri()
    icon = (TMP / LOGO_ICON_PNG.name).resolve().as_uri()
    stack = (TMP / LOGO_STACK_PNG.name).resolve().as_uri()
    stack4 = (TMP / LOGO_STACK_ON_DARK_PNG.name).resolve().as_uri()
    swatches = [
        ("#214149", "основной тёмно-бирюзовый — заголовки, тёмные слайды"),
        ("#468A9D", "бирюза — подзаголовки, ссылки, теги"),
        ("#A5D2DF", "небо — вторичный акцент, текст на тёмном"),
        ("#C19B4F", "золото — линии, маркеры, рамки акцентов"),
        ("#F3D593", "светлое золото — заголовки на тёмном фоне"),
        ("#494F55", "уголь — основной текст"),
        ("#A8B2BB", "сталь — второстепенный текст, линии таблиц"),
        ("#FFFFFF", "белый — фон документов и контентных слайдов"),
    ]
    cells = "".join(
        f'<tr><td><span class="swatch" style="background:{code}"></span> '
        f"<code>{code}</code></td><td>{desc}</td></tr>"
        for code, desc in swatches
    )
    body = f"""
    <div style="text-align:center;margin:0 0 18px">
      <img src="{stack}" alt="{NAME}" style="height:140px;width:auto">
    </div>
    <h1>Шаблон документа</h1>
    <p>Так выглядят PDF курса «{NAME}»: в шапке светлый кадр (светлый круг вокруг маяка),
    золотая линия под ним, заголовки цветом бренда, подвал с круглой маркой.</p>
    <h2>Когда копировать этот файл</h2>
    <p>Дублируйте <code>brand/шаблон-документа.pdf</code>, только если нужен пустой макет.
    Обычные материалы курса собираются из Markdown:</p>
    <pre>python3 ege-english-course/scripts/md_to_pdf.py</pre>
    <h2>Палитра дизайнера</h2>
    <table>
      <thead><tr><th>Цвет</th><th>Роль</th></tr></thead>
      <tbody>{cells}</tbody>
    </table>
    <h3>Градиенты</h3>
    <ul>
      <li>золото: {hex_of(GOLD)} → {hex_of(GOLD_LIGHT)}</li>
      <li>бирюза: {hex_of(TEAL_MID)} → {hex_of(TEAL_DEEP)}</li>
    </ul>
    <blockquote>Акцентная цитата или подсказка тьютору — золотая полоса слева.</blockquote>
    <h2>Иерархия заголовков</h2>
    <p>H1 — {hex_of(TEAL_DARK)}. H2 — тот же цвет с золотым подчёркиванием. H3 — {hex_of(TEAL)}.</p>
    <pre>Код и YAML остаются моноширинными, фон — светлая бирюза.</pre>
    <p style="color:#70787C">{NAME} · {TAGLINE} · {COURSE}</p>
    <p><img src="{icon}" alt="" style="height:48px;width:auto;margin-right:10px">
       <img src="{row}" alt="{NAME}" style="height:48px;width:auto"></p>
    <h2>Тёмный кадр</h2>
    <p>Тёмный кадр — тёмный круг вокруг маяка. На чёрном ставим диск и набор.
    На слайдах цвета <code>#214149</code> — только диск, без строки названия.</p>
    <div style="background:#0A0A0A;padding:28px 16px;text-align:center;margin:12px 0 0">
      <img src="{stack4}" alt="{NAME}" style="height:150px;width:auto">
    </div>
    """
    html_doc = wrap_document("Шаблон документа", "brand/шаблон-документа.pdf", body, False)
    html_path = TMP / "brand-template.html"
    html_path.write_text(html_doc, encoding="utf-8")
    chrome_pdf(html_path, PDF_TEMPLATE)
    return PDF_TEMPLATE


def main() -> int:
    pptx = write_pptx_template(TEMPLATE_OUT)
    pdf = write_pdf_template()
    print(f"OK  {pptx.relative_to(ROOT)}")
    print(f"OK  {pdf.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
