#!/usr/bin/env python3
"""Build the student intro-module presentation (widescreen PDF and PPTX)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PDF = ROOT / "pdf/03-curriculum/intro-student/вводный-модуль.pdf"
IMG_DIR = ROOT / "03-curriculum/intro-student/img"
TMP = Path("/tmp/ege-intro-pres")
CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")
CHROME_PROFILE = Path("/tmp/ege-chrome-pdf-profile")

CSS = r"""
@page { size: 13.333in 7.5in; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: "Liberation Sans", "Noto Sans", "DejaVu Sans", sans-serif;
  color: #494F55;
  background: #fff;
}
.slide {
  width: 13.333in;
  height: 7.5in;
  padding: 0.52in 0.7in 0.52in;
  page-break-after: always;
  position: relative;
  overflow: hidden;
  background: #fff;
}
.slide:last-child { page-break-after: auto; }
.gold-top { position: absolute; left: 0; right: 0; top: 0; height: 5px; background: #C19B4F; }
.teal-top { position: absolute; left: 0; right: 0; top: 5px; height: 7px; background: #214149; }
.gold-bot { position: absolute; left: 0; right: 0; bottom: 7px; height: 3px; background: #C19B4F; }
.teal-bot { position: absolute; left: 0; right: 0; bottom: 0; height: 7px; background: #214149; }
.logo-header {
  position: absolute; top: 0.20in; right: 0.55in; height: 0.42in; width: auto;
}
.logo-foot {
  position: absolute; left: 0.52in; bottom: 0.15in; height: 0.32in; width: auto;
}
.pg {
  position: absolute; right: 0.55in; bottom: 0.18in;
  font-size: 11pt; color: #A8B2BB;
}
.kicker {
  position: absolute; left: 0.95in; bottom: 0.18in;
  font-size: 10pt; color: #A8B2BB;
}
h1 {
  font-size: 28pt; color: #214149; margin: 0 0 16px;
  line-height: 1.15;
}
h2 { font-size: 20pt; color: #468A9D; margin: 0 0 12px; }
.cover {
  display: flex; flex-direction: column; justify-content: center;
  align-items: flex-start; text-align: left; height: 100%;
  padding: 0.7in 5.6in 0.55in 0.95in;
}
.cover .logo-stack { display: none; }
.cover h1 {
  font-size: 34pt; color: #FFFFFF; letter-spacing: 0.04em;
  text-transform: uppercase; margin: 0 0 14px;
}
.cover p { font-size: 16pt; margin: 6px 0; color: #A5D2DF; }
.cover-slide { background: #1A333A; }
.cover-slide .cover-bg {
  position: absolute; inset: 0; width: 100%; height: 100%;
  object-fit: cover; z-index: 0;
}
.cover-slide .cover, .cover-slide .kicker, .cover-slide .pg { position: relative; z-index: 1; }
.cover-slide .logo-header, .cover-slide .logo-foot,
.cover-slide .gold-top, .cover-slide .teal-top,
.cover-slide .gold-bot, .cover-slide .teal-bot { display: none; }
.cover-slide .kicker, .cover-slide .pg { color: #A5D2DF; }
.section-slide { background: #214149; color: #fff; }
.section-slide h1 { color: #F3D593; }
.section-slide .muted { color: #A5D2DF; }
.section-slide .logo-header { display: none; }
.section-slide .kicker, .section-slide .pg { color: #A5D2DF; }
.section {
  display: flex; flex-direction: column; justify-content: center;
  height: 100%; padding-bottom: 0.25in;
}
.section .num { font-size: 14pt; color: #C19B4F; letter-spacing: 0.12em; text-transform: uppercase; }
.section h1 { font-size: 40pt; margin-top: 8px; }
.big {
  display: flex; flex-direction: column; justify-content: center;
  align-items: center; text-align: center; height: 100%;
}
.big .n { font-size: 72pt; color: #468A9D; font-weight: 700; line-height: 1; }
.big p { font-size: 18pt; margin: 16px 0 0; max-width: 10.5in; }
ul { margin: 0; padding-left: 1.1em; font-size: 16pt; line-height: 1.45; }
li { margin: 0 0 8px; }
.small ul, .small p, .small li { font-size: 13.5pt; }
.tiny ul, .tiny p, .tiny li, .tiny pre { font-size: 11.5pt; line-height: 1.35; }
p { font-size: 16pt; line-height: 1.4; margin: 0 0 10px; }
pre, .kim {
  font-family: "Liberation Sans", "Noto Sans", sans-serif;
  background: #F3F7F8;
  border: 1px solid #C5D0D4;
  border-left: 6px solid #468A9D;
  padding: 10px 14px;
  font-size: 12pt;
  line-height: 1.35;
  white-space: pre-wrap;
  margin: 0 0 10px;
}
.example {
  background: #FBF8F1;
  border: 1px solid #E6D7B3;
  border-left: 6px solid #C19B4F;
  padding: 10px 14px;
  font-size: 12pt;
  line-height: 1.35;
  white-space: pre-wrap;
  margin: 0 0 8px;
}
.ok { border-left-color: #2F6F5A; background: #f3f8f5; }
.bad { border-left-color: #A33B32; background: #fdf4f3; }
table { border-collapse: collapse; width: 100%; font-size: 13.5pt; margin: 6px 0 0; }
th, td { border: 1px solid #C5D0D4; padding: 6px 8px; text-align: left; vertical-align: top; }
th { background: #E4F1F4; color: #214149; }
.cols { display: flex; gap: 28px; }
.cols > div { flex: 1; }
.tag {
  display: inline-block; background: #468A9D; color: #fff;
  font-size: 11pt; padding: 2px 10px; border-radius: 999px; margin-bottom: 8px;
}
.tag.good { background: #2F6F5A; }
.tag.bad { background: #A33B32; }
.muted { color: #70787C; font-size: 13pt; }
.shots { display: flex; gap: 14px; justify-content: center; align-items: flex-start; }
.shots img.shot {
  display: block;
  max-height: 5.45in;
  max-width: 12.1in;
  object-fit: contain;
  border: 1px solid #C5D0D4;
  background: #fff;
}
.shots.n2 img.shot { max-width: 6.05in; max-height: 5.35in; }
.credit { font-size: 11pt; color: #A8B2BB; margin: 0 0 8px; }
"""


def wrap(inner: str, n: int, total: int, klass: str = "") -> str:
    extra = klass
    header = '<img class="logo-header" src="img/logo-row.png" alt="Английский Маяк">'
    foot_icon = '<img class="logo-foot" src="img/logo-icon.png" alt="">'
    bg = ""
    if 'class="cover"' in inner:
        extra = f"{extra} cover-slide".strip()
        header = ""
        foot_icon = ""
        bg = '<img class="cover-bg" src="img/cover-bg.png" alt="">'
    elif 'class="section"' in inner:
        extra = f"{extra} section-slide".strip()
        header = ""
        foot_icon = '<img class="logo-foot" src="img/logo-icon-on-dark.png" alt="">'
    return f"""
<section class="slide {extra}">
  {bg}
  <div class="gold-top"></div>
  <div class="teal-top"></div>
  {header}
  {inner}
  {foot_icon}
  <div class="kicker">Английский Маяк · вводный модуль</div>
  <div class="pg">{n} / {total}</div>
  <div class="gold-bot"></div>
  <div class="teal-bot"></div>
</section>
"""


def cover(title: str, *lines: str) -> str:
    ps = "".join(f"<p>{x}</p>" for x in lines)
    return f'<div class="cover"><h1>{title}</h1>{ps}</div>'


def section(label: str, title: str, note: str = "") -> str:
    extra = f'<p class="muted">{note}</p>' if note else ""
    return f'<div class="section"><div class="num">{label}</div><h1>{title}</h1>{extra}</div>'


def big(n: str, caption: str) -> str:
    return f'<div class="big"><div class="n">{n}</div><p>{caption}</p></div>'


def h(title: str, body: str, small: bool = False) -> str:
    cls = ' class="small"' if small else ""
    return f"<h1>{title}</h1><div{cls}>{body}</div>"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def tbl(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{x}</th>" for x in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def shot(title: str, credit: str, *names: str) -> str:
    imgs = "".join(f'<img class="shot" src="img/{n}" alt="">' for n in names)
    cap = f'<p class="credit">{credit}</p>' if credit else ""
    return f'<h1>{title}</h1><div>{cap}<div class="shots n{len(names)}">{imgs}</div></div>'


def slides() -> list[str]:
    s: list[str] = []
    a = s.append

    a(cover(
        "Вводный модуль",
        "Курс подготовки к ЕГЭ по английскому языку",
        "Как устроен экзамен · все задания · баллы · бланки · шаблоны · примеры",
    ))
    a(h("Сегодня по порядку", ul([
        "Письменная часть: задания <b>1–36</b> кратко, затем <b>37</b> и <b>38</b> подробно.",
        "Устная часть: задания <b>1, 2, 3</b> кратко, затем <b>4</b> подробно.",
        "Сначала <b>само задание</b> — потом разбор работы.",
        "Кто с вами на курсе: <b>преподаватель</b>, <b>тьютор</b>, <b>куратор</b>.",
        "Показываем бланки: куда писать на экзамене.",
        "Удачные и неудачные ответы на 37, 38 и говорение.",
    ])))
    a(big("82", "максимум первичных баллов за весь ЕГЭ:<br>письменная часть 62 + устная 20"))
    a(h("Письменная часть · 190 минут · 62 балла", tbl(
        ["Задания", "Раздел", "Баллы", "Куда"],
        [
            ["1–9", "Аудирование", "12", "бланк № 1"],
            ["10–18", "Чтение", "12", "бланк № 1"],
            ["19–36", "Грамматика и лексика", "18", "бланк № 1"],
            ["37", "Личное письмо другу", "6", "бланк № 2"],
            ["38", "Эссе по таблице или диаграмме", "14", "бланк № 2"],
        ],
    ) + '<p class="muted" style="margin-top:12px">Рекомендуемое время: аудирование 30 мин (идёт с записью), чтение 30, грамматика 40, письмо 90. Задание 1 = 2 балла, 2 = 3, 3–9 по 1. Задание 10 = 3, 11 = 2, 12–18 по 1.</p>'))
    a(h("Устная часть · ~17 минут · 20 баллов · отдельный день", tbl(
        ["Задание", "Что делать", "Баллы", "Черновик"],
        [
            ["1", "Прочитать текст вслух", "1", "нет"],
            ["2", "Задать 4 вопроса по рекламе", "4", "нет"],
            ["3", "Ответить на 5 вопросов интервью", "5", "нет"],
            ["4", "Голосовое другу по двум фото", "10", "нет"],
        ],
    ) + '<p class="muted" style="margin-top:12px">Бумажного бланка ответов нет. Всё — в микрофон. Идёт аудио- и видеозапись.</p>'))
    a(h("Бланк ответов № 1", ul([
        "Сюда переносят <b>только задания 1–36</b>.",
        "Одна клетка — один символ. Буквы <b>заглавные</b>, печатные.",
        "Без пробелов, точек, запятых, кавычек.",
        "Исправления — в поле замены.",
        "Письмо 37 и эссе 38 сюда <b>не писать</b>.",
        "Сначала работаете в КИМ, на перенос оставьте время.",
    ])))
    a(shot(
        "Как заполнять бланк № 1",
        "Демоверсия КИМ ЕГЭ 2025, инструкция к письменной части.",
        "demo-blank-instruction.png",
    ))
    a(h("Бланк ответов № 2", ul([
        "Сюда пишете <b>только 37 и 38</b>. Укажите номер задания.",
        "Для 38 укажите <b>38.1 или 38.2</b> — выбран только один вариант.",
        "Числительные в 38 пишите <b>цифрами</b>.",
        "Проверяют только то, что в бланке. Черновик эксперт не читает.",
        "Адрес и тему письма (From / To / Subject) <b>не копировать</b>.",
        "Пишите через строчку — так проще править. Почерк должен читаться однозначно.",
        "Если 38 не влезло — дополнительный бланк № 2, не бланк № 1.",
    ])))
    a(h("Как устроен этот курс", ul([
        "После диагностики — этот вводный модуль. Дальше рабочие модули.",
        "<b>Receptive:</b> лексика, грамматика, чтение, аудирование, фонетика, тексты про Россию и English World — автопроверка.",
        "<b>Productive:</b> урок с преподавателем в Zoom → тьютору письмо 37, эссе 38 и задание 4 → итоговый тест.",
        "Расписание и дедлайны — <b>куратор</b>. Он английский не проверяет.",
        "В 37 / 38 / 4 каждого модуля есть аспект <b>про Россию</b>.",
        "<b>РКЗ и организация</b> — полностью с первой сдачи. <b>Язык</b> — только по уже пройденным темам.",
    ])))
    a(h("Кто с вами работает", tbl(
        ["Роль", "Что делает", "Чего не делает"],
        [
            ["Преподаватель", "Урок Zoom: живая речь на теме модуля", "Не ставит баллы за 37 / 38 / 4"],
            ["Тьютор", "Проверяет письмо, эссе и голосовое как эксперт", "Не ведёт Zoom и не гоняет дедлайны"],
            ["Куратор", "Расписание, дедлайны, связь с семьёй", "Не проверяет английский"],
        ],
    )))
    a(h("К кому с каким вопросом", ul([
        "<b>Преподаватель</b> — как сказать на уроке, как звучит фраза, что было в Zoom.",
        "<b>Тьютор</b> — баллы и комментарий к этой работе: что исправить сейчас.",
        "<b>Куратор</b> — когда Zoom, когда дедлайн, не открывается модуль, вопрос семьи про прогресс.",
        "Сегодня вас ведёт эксперт вводного модуля. Дальше на курсе — эти три роли.",
        "Письмо тьютору «во сколько занятие?» и куратору «поставьте 14 за эссе» — не туда.",
    ])))

    a(section("Часть 1", "Письменная часть<br>задания 1–36", "Кратко: формат и сами задания из демоверсии 2025."))
    a(h("Аудирование · задания 1–9 · 12 баллов", ul([
        "<b>1</b> — соответствие: кто что говорит (основное содержание). Максимум 2 балла.",
        "<b>2</b> — верно / неверно / в тексте не сказано. Максимум 3 балла.",
        "<b>3–9</b> — выбор ответа по интервью (полное понимание). По 1 баллу.",
        "Запись идёт один раз по инструкции КИМ. Ответы — в бланк № 1.",
        "На курсе стратегии аудирования — в рецептивной фазе каждого модуля.",
    ])))
    a(shot(
        "Аудирование · задания 1–2",
        "Демоверсия КИМ ЕГЭ 2025. Таблица здесь — только поле для ответов, не данные для анализа.",
        "demo-listening-1-2.png",
    ))
    a(shot(
        "Аудирование · задания 3–9",
        "Демоверсия КИМ ЕГЭ 2025: интервью, выбор 1 / 2 / 3.",
        "demo-listening-3-9.png",
    ))
    a(h("Чтение · задания 10–18 · 12 баллов", ul([
        "<b>10</b> — заголовки к абзацам (основное содержание). Максимум 3 балла.",
        "<b>11</b> — вставить пропущенные фрагменты (связи в тексте). Максимум 2 балла.",
        "<b>12–18</b> — выбор ответа по связному тексту (полное понимание). По 1 баллу.",
        "Тексты — сплошные: статьи, заметки. <b>Таблиц и диаграмм в чтении нет.</b>",
        "Таблица/круговая диаграмма — это задание <b>38</b> (письмо), не раздел «Чтение».",
        "Объём текстов на экзамене — до 900 слов.",
    ])))
    a(shot(
        "Чтение · задание 10",
        "Демоверсия КИМ ЕГЭ 2025: короткие тексты + заголовки. «Таблица» внизу — только сетка ответов.",
        "demo-reading-10.png",
    ))
    a(shot(
        "Чтение · задание 11",
        "Демоверсия КИМ ЕГЭ 2025: один текст с пропусками A–F.",
        "demo-reading-11.png",
    ))
    a(shot(
        "Чтение · задания 12–18",
        "Демоверсия КИМ ЕГЭ 2025: длинный сплошной текст, выбор ответа. Несплошных текстов нет.",
        "demo-reading-12.png",
    ))
    a(h("Грамматика и лексика · задания 19–36 · 18 баллов", ul([
        "<b>19–24</b> — грамматика: поставить слово в нужную форму (6 баллов).",
        "<b>25–29</b> — словообразование (5 баллов).",
        "<b>30–36</b> — выбор лексики в связном тексте (7 баллов).",
        "В бланке № 1: слова заглавными буквами, без лишних символов.",
        "На курсе грамматика копится по модулям. Тьютор в 37/38/4 комментирует только уже пройденное.",
    ])))
    a(shot(
        "Грамматика · задания 19–24",
        "Демоверсия КИМ ЕГЭ 2025. Может быть один текст или два коротких (помечено «ИЛИ»).",
        "demo-grammar-19-24.png",
    ))
    a(shot(
        "Словообразование · задания 25–29",
        "Демоверсия КИМ ЕГЭ 2025: образовать родственное слово от опорного.",
        "demo-wordformation-25-29.png",
    ))

    a(section("Часть 2", "Задание 37<br>электронное письмо", "Подробно. Сначала задание — потом работы."))
    a(big("6 баллов", "максимум за письмо другу<br>РКЗ 2 · организация 2 · язык 2"))
    a(shot(
        "Задание 37 · демоверсия 2025",
        "Так выглядит КИМ. Дальше разберём, что с ним делать. Тема — русская литература: три вопроса другу и новость про подарок.",
        "demo-writing-37.png",
    ))
    a(h("Что сделать", ul([
        "Ответить на <b>все три</b> вопроса друга — полно и точно.",
        "Задать <b>три своих вопроса</b> именно про его новость (здесь — поездка на море).",
        "Соблюсти правила письма: вежливость + оформление.",
        "Писать в бланк № 2. From / To / Subject не копировать.",
        "Если по содержанию 0 — язык и организацию уже не ставят. Всё письмо 0.",
    ])))
    a(h("Объём", ul([
        "В задании написано <b>100–140</b> слов.",
        "В схеме эксперта допуск <b>90–154</b>.",
        "Меньше 90 → письмо <b>не проверяют</b>, 0 за всё.",
        "Больше 154 → проверяют только первые <b>140</b> слов. Могут выпасть вопросы, Write back soon и подпись.",
        "Считают всё: артикли, предлоги, обращение, подпись. <i>don't</i> = одно слово.",
    ])))
    a(h("Шесть аспектов содержания (РКЗ)", tbl(
        ["Аспект", "Что должно быть", "Частая ошибка"],
        [
            ["1–3", "Полный ответ на каждый вопрос", "да/нет; не на тот вопрос; транслит про Россию"],
            ["4", "Три вопроса про новость друга", "просьба Wanna tell me; вопрос уже отвечен в стимуле"],
            ["5", "Спасибо и/или радость + надежда на ответ", "своя формула I’ll be waiting for your emails"],
            ["6", "Dear/Hi + имя; завершение; только имя", "Hey; адрес и дата; фамилия"],
        ],
    ) + '<p class="muted" style="margin-top:10px">К1: 2 — все аспекты или 1 неточность; 1 — 2–3 неточности; 0 — 3+ пропуска.</p>', small=True))
    a(h("Шаблон оформления", """
<pre class="kim">Dear [Name],

Thank you for your letter. It was great to hear from you.

[Абзац: ответы на три вопроса друга.]

[Абзац: три вопроса другу по его новости.]

Write back soon.
Best wishes,
[только ваше имя]</pre>
<ul>
<li><code>Dear Kevin,</code> / <code>Hi Kevin,</code> — да. <code>Hey Kevin</code> — <b>нет</b>.</li>
<li>Обращение, завершающая фраза и подпись — <b>отдельные строки</b>.</li>
<li>Абзацы должны быть видны. Один простой абзац из одной короткой фразы — слабо.</li>
</ul>
""", small=True))
    a(shot(
        "Удачный ответ · 6 из 6",
        "Работа 8311, скан из мр Пч. Olive / St. Petersburg · 105 слов · К1 2 · К2 2 · К3 2.",
        "work-8311.png",
    ))
    a(h("Почему это 6, а не обрубок", ul([
        "Есть Dear Olive, Write back soon, Best wishes и только имя.",
        "Три ответа по существу, в том числе про Россию — так, что англичанин поймёт.",
        "Три вопроса <b>про поездку</b>, не про погоду.",
        "Абзацы и отдельные строки на месте.",
        "На курсе с первой сдачи требуем содержание и организацию как здесь. Язык комментируем по пройденным темам.",
    ])))
    a(shot(
        "Сначала задание · потом ноль",
        "Работа 8447, скан из мр Пч. Hey Mike · 0 из 6. Обращение Hey и вопросы не по новости.",
        "work-8447.png",
    ))
    a(h("Почему сразу ноль", ul([
        "<code>Hey</code> не принимают как обращение задания 37.",
        "<i>to hear you</i> вместо <i>to hear from you</i> — формула вежливости не засчитана.",
        "<i>I’ll be waiting for your emails</i> — такого клише нет.",
        "«Вопросы»: просьба; вопрос, на который друг уже ответил (<i>a nice summer camp</i>); вопрос не про этот лагерь.",
        "Дальше язык уже не проверяют.",
    ])))
    a(h("Ловушка про Россию", ul([
        "Если друг спрашивает про русские книги, фильмы, места — пишите так, чтобы он <b>узнал</b> название.",
        "Работа 4798: <i>Prestuplenie, nakasanie</i> и <i>mertvie dushi</i> — сбой коммуникации, аспект не принят.",
        "Нужно: <i>Crime and Punishment</i>, <i>Dead Souls</i> (можно добавить русское имя рядом).",
        "Та же работа ещё и длиннее 154 слов: из проверки выпали третий вопрос и подпись. Итого 0.",
        "На курсе в каждом письме будет вопрос про Россию — это правило с первой сдачи.",
    ])))
    a(h("Чек-лист 37 перед бланком № 2", ul([
        "90–154 слова, лучше 100–140.",
        "Dear / Hi + имя, не Hey.",
        "Спасибо за письмо.",
        "Три ответа по существу.",
        "Три вопроса про новость друга, не просьбы.",
        "Write back soon (или одно завершение) + только имя на отдельных строках.",
        "Нет адреса и даты.",
    ])))

    a(section("Часть 3", "Задание 38<br>эссе по таблице / диаграмме", "Официальный стиль. Это не CV и не деловое письмо."))
    a(big("14 баллов", "максимум за эссе<br>РКЗ 3 · организация 3 · лексика 3 · грамматика 3 · орфография 2"))
    a(h("Выбрать только одно", ul([
        "В КИМ два варианта: <b>38.1 таблица</b> или <b>38.2 круговая диаграмма</b>.",
        "В бланке № 2 напишите номер: 38.1 или 38.2.",
        "Числительные — <b>цифрами</b> (37%, не thirty-seven percent).",
        "Будут только таблицы и круговые диаграммы.",
        "Высокий язык без анализа данных высокие баллы не даст. Содержание важнее.",
        "Если по РКЗ 0 — вся работа 0.",
    ])))
    a(shot(
        "Задание 38.1 · таблица · демоверсия 2025",
        "Выбираете только один вариант. Таблица или круговая диаграмма — здесь, в 38, не в чтении. Почему жители Zetland не ходят в театр.",
        "demo-writing-38-1.png",
    ))
    a(shot(
        "Задание 38.2 · круговая диаграмма · демоверсия 2025",
        "Тот же КИМ: альтернатива — pie chart про изучение иностранных языков.",
        "demo-writing-38-2.png",
    ))
    a(h("Пять абзацев = шесть аспектов РКЗ", tbl(
        ["Абзац", "Что написать", "Нельзя"],
        [
            ["1", "Проект + тема + survey / opinion poll", "«я составил таблицу ниже»"],
            ["2", "2–3 факта с цифрами и вопросом опроса", "факты без цифр"],
            ["3", "1–2 существенных сравнения + комментарий", "29% vs 23% как much more"],
            ["4", "Проблема из формулировки плана + решение", "проблема не про эту сферу"],
            ["5", "I think / I believe именно про последний пункт", "мнение не на тот вопрос"],
            ["стиль", "Нейтральный официальный", "kids, gonna, риторические вопросы"],
        ],
    ), small=True))
    a(h("Объём 38", ul([
        "В задании <b>200–250</b>. Допуск <b>180–275</b>.",
        "Меньше 180 → 0 за всё.",
        "Больше 275 → проверяют только первые <b>250</b> слов. Заключение может выпасть — и РКЗ падает.",
        "Введение и заключение примерно равны. Основа не короче, чем они вместе.",
        "Больше 30% списанного текста → 0.",
    ])))
    a(h("Шаблон фраз", """
<pre class="kim">While doing a project on …, I have found some data on the subject –
the results of a survey.

According to the data, …% of respondents…
As can be seen from the table, the most / least popular option is…

Compared with … (X%), … is higher / lower (Y%). This may be because…

One problem that can arise with … is…
A possible way to solve it is…

In conclusion, I believe that … because …</pre>
<p>Не пишите <i>I organised it in the table below</i> — таблицы «ниже» в бланке нет, и вы её не составляли.</p>
""", small=True))
    a(shot(
        "Удачный ответ · 12 из 14",
        "Работа 1025, скан из мр Пч. Музыкальные школы · 224 слова · РКЗ 3 · орг. 2 · лекс. 2 · гр. 3 · орф. 2.",
        "work-1025.png",
    ))
    a(h("Почему 12, а не 14", ul([
        "Есть проект, тема и opinion polls. Три факта с цифрами. Проблема из плана. Явное I believe.",
        "Сняли организацию и лексику: сравнили 19% и 15% (разница 4 пункта — слабое сравнение), комментарий про «другие хобби» из таблицы не следует.",
        "<i>vote for</i>, <i>learning techniques</i> вместо teaching methods; <i>can not</i> раздельно.",
        "На курсе лучше сразу сравнивать несхожие цифры, например 29% и 14%.",
        "Содержание и организацию с первой сдачи требуем как здесь. Язык — по пройденным темам.",
    ])))
    a(shot(
        "Сначала задание · потом ноль",
        "Работа 8781, скан из мр Пч. Новый год · 218 слов · 0 из 14. «Сам организовал таблицу ниже», цифры словами, вывод не по плану.",
        "work-8781.png",
    ))
    a(h("Почему ноль, хотя абзацев пять", ul([
        "Нет survey: «сам организовал таблицу ниже».",
        "Факты без нормальных цифр (<i>only third percent</i>).",
        "20% названы slightly lower, чем 34% — это не сравнение.",
        "7% — не «только 7% покупают подарки», а «7% считают покупку подарков самым важным».",
        "Заключение не про подготовку заранее и из‑за ошибок его не понять.",
        "Ещё ловушка объёма: работа 5806 на 279 слов потеряла вывод — РКЗ стало 1. Лучше 220 слов с целым заключением.",
    ])))
    a(h("Чек-лист 38 перед бланком № 2", ul([
        "180–275 слов, лучше 200–250.",
        "Номер 38.1 или 38.2.",
        "Во вступлении: проект + тема + survey / opinion poll.",
        "2–3 факта с цифрами.",
        "Сравнение несхожих цифр + комментарий.",
        "Проблема из плана + решение.",
        "I think / I believe именно про последний пункт плана.",
        "Пять абзацев, нейтральный стиль.",
    ])))

    a(section("Часть 4", "Устная часть<br>задания 1–3", "Кратко. Черновиков нет — ничего записывать нельзя."))
    a(big("20 баллов", "вся устная часть: 1 + 4 + 5 + 10<br>ответ только голосом, ~17 минут вместе с подготовкой"))
    a(shot(
        "Говорение · задание 1 · демоверсия 2025",
        "Подготовка 1,5 мин, читать 1,5 мин. Ставят 1 или 0. Текст про water hole в саванне.",
        "demo-speaking-1.png",
    ))
    a(h("Задание 1 · на что смотрят", ul([
        "Интонация, звуки, словесное и фразовое ударение.",
        "Уложиться в 1,5 минуты и дочитать текст.",
        "Не читать того, чего нет, и не пропускать строки.",
        "Риск нуля: речь почти не прочитать; 3+ смысловые замены звуков; пропуск 3+ слов; пауза, ломающая смысл.",
        "На курсе фонетика идёт по шагам 1–20. Сборка чтения вслух — к модулям 18–20.",
    ])))
    a(shot(
        "Говорение · задание 2 · демоверсия 2025",
        "ФИПИ, демоверсия: реклама хоккейного клуба и 4 опорных пункта.",
        "demo-speaking-2.png",
    ))
    a(h("Задание 2 · как спрашивать", ul([
        "По <b>1 баллу</b> за вопрос. Каждый вопрос оценивают отдельно.",
        "Вступление и прощание <b>не нужны</b>.",
        "Строго по подсказке. If / whether → только общий вопрос.",
        "Первый вопрос должен прояснить, куда звоните: не How much is it? без названия.",
        "Последний вариант, даже если исправились на худший, и есть тот, что засчитают.",
        "Норма: <i>How long does the tour last?</i> · <i>How much does it cost for one person?</i> · <i>Are there any student discounts?</i> · <i>What special equipment is needed?</i>",
    ])))
    a(shot(
        "Говорение · задание 3 · демоверсия 2025",
        "Вопросы на экране заранее не видите — слушайте. 40 секунд, 2–3 фразы, по 1 баллу. Интервью про одежду; на экзамене звучит в наушниках.",
        "demo-speaking-3.png",
    ))
    a(h("Задание 3 · как отвечать", ul([
        "Каждый вопрос звучит один раз. Можно секунду подумать — нельзя молчать до нуля.",
        "Полный ответ: все детали вопроса (what <b>and</b> why).",
        "Не обязательно говорить все 40 секунд.",
        "Ошибки языка не снимают балл, если друг по интервью вас понял.",
        "На курсе живая практика — Zoom. Тьютору 1–3 каждую неделю не сдаём.",
        "В одном из вопросов интервью тоже бывает аспект про Россию / ваш регион.",
    ])))

    a(section("Часть 5", "Задание 4<br>голосовое другу", "Основной устный продукт курса. С первой сдачи тьютору."))
    a(big("10 баллов", "максимум за монолог<br>РКЗ 4 · организация 3 · язык 3"))
    a(shot(
        "Говорение · задание 4 · демоверсия 2025",
        "Так выглядит КИМ. Фото другу сейчас не отправляете — только голос. Проект Volunteering, 12–15 фраз, не больше 3 минут.",
        "demo-speaking-4.png",
    ))
    a(h("Что это за ситуация", ul([
        "Друг <b>не видит</b> фото. Не говорите «я уже отправил картинки».",
        "Обращайтесь к другу по имени, you.",
        "Каждый пункт плана — примерно 2–3 фразы, всё связано с <b>темой проекта</b>.",
        "Подготовка 2,5 минуты. Говорить не больше 3 минут. Запись оборвётся сама.",
        "Можно меньше 3 минут. Можно исправляться.",
        "Если по содержанию 0 — язык и организацию не ставят.",
    ])))
    a(h("Четыре аспекта и объём фраз", tbl(
        ["Аспект", "Что сказать", "Ошибка"],
        [
            ["1", "Оба фото + различие + почему это этот проект", "описал одежду, не назвал тему"],
            ["2", "Плюсы обоих типов, не одного", "плюсы только «своего» фото"],
            ["3", "Минусы обоих типов", "минус картинки, а не типа отдыха"],
            ["4", "Мнение в той форме, что в задании, + почему", "I like photo 1"],
        ],
    ) + """<p style="margin-top:10px">12–15 фраз — цель. ≤7 → 0 за всё. 8–9 → максимум 1 по РКЗ. 10–11 → максимум 2.</p>""", small=True))
    a(h("Шаблон монолога", """
<pre class="kim">Hi, Ann! I’ve found two photos for our project “Summer holidays”.
I can’t send them now, so I’m leaving a voice message.

In the first photo I can see … In the second photo … The main difference
is … That’s why these photos illustrate our project: they show two types of …

As for the advantages, the main advantage of … is … The main advantage of … is …
Talking about the disadvantages, … / On the other hand, …

As for me, when I was a child I preferred … because …

That’s all I wanted to say. Let me know what you think. Bye!</pre>
""", small=True))
    a(shot(
        "Удачный ответ · 9 из 10",
        "Ответ 0487, скан разбора из мр УЧ. Summer holidays · РКЗ 4 · орг. 3 · язык 2. Устная работа — аудио; здесь страница экспертного разбора со словами ответа.",
        "work-0487.png",
    ))
    a(shot(
        "Неудачный ответ · 0 из 10",
        "Ответ 9213, скан из мр УЧ. Family pastime. Нет различия про проект, нет плюсов/минусов двух типов, мнение не разобрать → содержание &lt; 50% → всё задание 0.",
        "work-9213.png",
    ))
    a(h("Чек-лист 4 перед записью", ul([
        "12–15 фраз, не меньше 7.",
        "Hi + имя.",
        "Названа тема проекта. Фото другу сейчас не отправляете.",
        "Оба фото + различие про эту тему.",
        "Плюс и минус двух типов.",
        "Мнение в той форме, которая в задании (prefer / preferred as a child).",
        "Bye / Let me know what you think.",
    ])))

    a(section("Часть 6", "Что сдаёте тьютору", "С первого рабочего модуля — как на экзамене."))
    a(h("Три продукта каждый модуль", tbl(
        ["Задание", "Максимум", "Что проверяем сразу", "Язык"],
        [
            ["37 письмо", "6", "РКЗ + организация + объём", "только пройденные темы"],
            ["38 эссе", "14", "РКЗ + организация + объём + стиль", "только пройденные темы"],
            ["4 монолог", "10", "4 аспекта + вход/выход + фразы", "лексика, грамматика, фонетика — накопительно"],
        ],
    ) + '<p style="margin-top:14px">Тьютор ставит те же баллы, что эксперт. В комментариях: «исправить сейчас» и «отметили, пока не требуем».</p>', small=True))
    a(h("Перед первой сдачей", ul([
        "Ещё раз посмотрите эту презентацию — особенно задание, шаблон и чек-лист.",
        "В каждой работе будет вопрос или аспект про Россию.",
        "Устные 1–3 знаете по формату; тренируете с преподавателем в Zoom и в фонетике.",
        "Задания 1–36 — в рецептивной фазе и в тесте модуля.",
        "Дедлайн первой сдачи скажет <b>куратор</b>. Три работы — <b>тьютору</b>.",
        "Дальше — ваш первый рабочий модуль.",
    ])))
    a(cover(
        "Встретимся в первом рабочем модуле",
        "Регулярность важнее идеального старта.",
        "Ошибки — это материал для следующего шага, не приговор.",
    ))
    return s


def main() -> int:
    parts = slides()
    total = len(parts)
    inner = "".join(wrap(html, i, total) for i, html in enumerate(parts, 1))
    doc = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Вводный модуль — презентация для ученика</title>
  <style>{CSS}</style>
</head>
<body>
{inner}
</body>
</html>
"""
    TMP.mkdir(parents=True, exist_ok=True)
    img_tmp = TMP / "img"
    if img_tmp.exists():
        shutil.rmtree(img_tmp)
    shutil.copytree(IMG_DIR, img_tmp)
    from brand import COVER_BG_PNG, LOGO_ICON_ON_DARK_PNG, LOGO_ICON_PNG, LOGO_MARK_PNG, LOGO_ROW_PNG, LOGO_STACK_PNG

    for src in (
        LOGO_ICON_PNG,
        LOGO_ROW_PNG,
        LOGO_STACK_PNG,
        LOGO_ICON_ON_DARK_PNG,
        LOGO_MARK_PNG,
        COVER_BG_PNG,
    ):
        if src.exists():
            shutil.copy2(src, img_tmp / src.name)
        shutil.copy2(src, img_tmp / src.name)
    html_path = TMP / "intro.html"
    html_path.write_text(doc, encoding="utf-8")
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    CHROME_PROFILE.mkdir(parents=True, exist_ok=True)
    cmd = [
        CHROME,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--no-first-run",
        "--no-default-browser-check",
        "--allow-file-access-from-files",
        "--no-pdf-header-footer",
        f"--user-data-dir={CHROME_PROFILE}",
        f"--print-to-pdf={OUT_PDF}",
        html_path.resolve().as_uri(),
    ]
    result = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)
    if result.returncode != 0 or not OUT_PDF.exists() or OUT_PDF.stat().st_size < 20000:
        raise SystemExit(
            f"Chrome failed ({result.returncode})\n{result.stderr[-4000:]}\nsize={OUT_PDF.stat().st_size if OUT_PDF.exists() else 0}"
        )
    print(f"OK  {OUT_PDF.relative_to(ROOT)}  ({OUT_PDF.stat().st_size} bytes, {total} slides)")
    from intro_student_pptx import main as write_pptx

    write_pptx()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
