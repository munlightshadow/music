# PDF-снимки пакета курса

Папка повторяет структуру исходников `ege-english-course/`.

| Файл | Что это |
| --- | --- |
| [INDEX.pdf](INDEX.pdf) | Оглавление всех PDF |
| [_полный-пакет.pdf](_полный-пакет.pdf) | Все документы одним файлом |
| остальные `.pdf` | По одному на каждый `.md` / `.yaml` |

Исходники Markdown остаются главными. PDF — для чтения и печати.

Презентация вводного модуля для ученика (не из Markdown, отдельный генератор):

- редактируемый PPTX: [../03-curriculum/intro-student/вводный-модуль.pptx](../03-curriculum/intro-student/вводный-модуль.pptx) (копия: [03-curriculum/intro-student/вводный-модуль.pptx](03-curriculum/intro-student/вводный-модуль.pptx))
- [03-curriculum/intro-student/вводный-модуль.pdf](03-curriculum/intro-student/вводный-модуль.pdf) (69 слайдов, со сканами демоверсии и работ; роли преподавателя, тьютора, куратора)
- речь эксперту к показу: [../03-curriculum/intro-student/presentation-script.md](../03-curriculum/intro-student/presentation-script.md)
- памятка родителям: [../03-curriculum/intro-student/parent-guide.md](../03-curriculum/intro-student/parent-guide.md)
- картинки: `03-curriculum/intro-student/img/`
- пересобрать картинки: `python3 ege-english-course/scripts/extract_intro_images.py`
- пересобрать PDF и PPTX: `python3 ege-english-course/scripts/intro_student_presentation.py` (нужен `python-pptx`)

Пересобрать остальные снимки:

```bash
pip install markdown
python3 ege-english-course/scripts/md_to_pdf.py
```

Нужен Google Chrome (headless).
