# PDF-снимки пакета курса

Папка повторяет структуру исходников `ege-english-course/`.

| Файл | Что это |
| --- | --- |
| [INDEX.pdf](INDEX.pdf) | Оглавление всех PDF |
| [_полный-пакет.pdf](_полный-пакет.pdf) | Все документы одним файлом |
| остальные `.pdf` | По одному на каждый `.md` / `.yaml` |

Исходники Markdown остаются главными. PDF — для чтения и печати.

Презентация вводного модуля для ученика (не из Markdown, отдельный генератор):

- [03-curriculum/intro-student/вводный-модуль.pdf](03-curriculum/intro-student/вводный-модуль.pdf)
- пересобрать: `python3 ege-english-course/scripts/intro_student_presentation.py`

Пересобрать остальные снимки:

```bash
pip install markdown
python3 ege-english-course/scripts/md_to_pdf.py
```

Нужен Google Chrome (headless).
