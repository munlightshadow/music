#!/usr/bin/env python3
"""Build the student intro-module presentation (widescreen PDF and PPTX)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PDF = ROOT / "pdf/03-curriculum/intro-student/вводный-модуль.pdf"
TMP = Path("/tmp/ege-intro-pres")
CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")
CHROME_PROFILE = Path("/tmp/ege-chrome-pdf-profile")

CSS = r"""
@page { size: 13.333in 7.5in; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: "Liberation Sans", "Noto Sans", "DejaVu Sans", sans-serif;
  color: #222;
  background: #fff;
}
.slide {
  width: 13.333in;
  height: 7.5in;
  padding: 0.55in 0.7in 0.5in;
  page-break-after: always;
  position: relative;
  overflow: hidden;
  background: #fff;
}
.slide:last-child { page-break-after: auto; }
.bars-top, .bars-bot {
  position: absolute; left: 0; right: 0; height: 18px;
}
.bars-top { top: 0; border-top: 10px solid #0e8a8a; border-bottom: 3px solid #0e8a8a; }
.bars-bot { bottom: 0; border-bottom: 10px solid #0e8a8a; border-top: 3px solid #0e8a8a; }
.pg {
  position: absolute; right: 0.55in; bottom: 0.22in;
  font-size: 11pt; color: #7a838c;
}
.kicker {
  position: absolute; left: 0.7in; bottom: 0.22in;
  font-size: 10pt; color: #7a838c;
}
h1 {
  font-size: 28pt; color: #0e8a8a; margin: 0 0 16px;
  line-height: 1.15;
}
h2 { font-size: 20pt; color: #0e8a8a; margin: 0 0 12px; }
.cover {
  display: flex; flex-direction: column; justify-content: center;
  align-items: center; text-align: center; height: 100%;
  padding-bottom: 0.3in;
}
.cover h1 {
  font-size: 34pt; color: #e07a2f; letter-spacing: 0.02em;
  text-transform: uppercase; margin: 0 0 14px;
}
.cover p { font-size: 16pt; margin: 6px 0; color: #333; }
.section {
  display: flex; flex-direction: column; justify-content: center;
  height: 100%; padding-bottom: 0.25in;
}
.section .num { font-size: 14pt; color: #e07a2f; letter-spacing: 0.12em; text-transform: uppercase; }
.section h1 { font-size: 40pt; margin-top: 8px; }
.big {
  display: flex; flex-direction: column; justify-content: center;
  align-items: center; text-align: center; height: 100%;
}
.big .n { font-size: 72pt; color: #0e8a8a; font-weight: 700; line-height: 1; }
.big p { font-size: 18pt; margin: 16px 0 0; max-width: 10.5in; }
ul { margin: 0; padding-left: 1.1em; font-size: 16pt; line-height: 1.45; }
li { margin: 0 0 8px; }
.small ul, .small p, .small li { font-size: 13.5pt; }
.tiny ul, .tiny p, .tiny li, .tiny pre { font-size: 11.5pt; line-height: 1.35; }
p { font-size: 16pt; line-height: 1.4; margin: 0 0 10px; }
pre, .kim {
  font-family: "Liberation Sans", "Noto Sans", sans-serif;
  background: #f4f7f7;
  border: 1px solid #cfe3e3;
  border-left: 6px solid #0e8a8a;
  padding: 10px 14px;
  font-size: 12pt;
  line-height: 1.35;
  white-space: pre-wrap;
  margin: 0 0 10px;
}
.example {
  background: #f7f7f4;
  border: 1px solid #ddd8c8;
  border-left: 6px solid #e07a2f;
  padding: 10px 14px;
  font-size: 12pt;
  line-height: 1.35;
  white-space: pre-wrap;
  margin: 0 0 8px;
}
.ok { border-left-color: #1b7f4e; background: #f3f8f5; }
.bad { border-left-color: #b42318; background: #fdf4f3; }
table { border-collapse: collapse; width: 100%; font-size: 13.5pt; margin: 6px 0 0; }
th, td { border: 1px solid #c5d0d0; padding: 6px 8px; text-align: left; vertical-align: top; }
th { background: #e7f3f3; color: #0e5f5f; }
.cols { display: flex; gap: 28px; }
.cols > div { flex: 1; }
.tag {
  display: inline-block; background: #0e8a8a; color: #fff;
  font-size: 11pt; padding: 2px 10px; border-radius: 999px; margin-bottom: 8px;
}
.tag.good { background: #1b7f4e; }
.tag.bad { background: #b42318; }
.muted { color: #5c6570; font-size: 13pt; }
"""


def wrap(inner: str, n: int, total: int, klass: str = "") -> str:
    return f"""
<section class="slide {klass}">
  <div class="bars-top"></div>
  <div class="bars-bot"></div>
  {inner}
  <div class="kicker">Вводный модуль · курс подготовки к ЕГЭ</div>
  <div class="pg">{n} / {total}</div>
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
        "Показываем бланки: куда писать на экзамене.",
        "Удачные и неудачные ответы на 37, 38 и говорение.",
    ])))
    a(big("82", "максимум первичных баллов за весь ЕГЭ:<br>письменная часть 62 + устная 20"))
    a(h("Письменная часть · 190 минут · 62 балла", tbl(
        ["Задания", "Раздел", "Баллы", "Куда"],
        [
            ["1–9", "Аудирование", "20", "бланк № 1"],
            ["10–18", "Чтение", "20", "бланк № 1"],
            ["19–36", "Грамматика и лексика", "18", "бланк № 1"],
            ["37", "Личное письмо другу", "6", "бланк № 2"],
            ["38", "Эссе по таблице или диаграмме", "14", "бланк № 2"],
        ],
    ) + '<p class="muted" style="margin-top:12px">Рекомендуемое время: аудирование 30 мин (идёт с записью), чтение 30, грамматика 40, письмо 90.</p>'))
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
        "<b>Productive:</b> Zoom → тьютору письмо 37, эссе 38 и задание 4 → итоговый тест.",
        "В 37 / 38 / 4 каждого модуля есть аспект <b>про Россию</b>.",
        "<b>РКЗ и организация</b> — полностью с первой сдачи. <b>Язык</b> — только по уже пройденным темам.",
    ])))

    a(section("Часть 1", "Письменная часть<br>задания 1–36", "Кратко: формат, чтобы не удивиться в бланке № 1."))
    a(h("Аудирование · задания 1–9 · 20 баллов", ul([
        "<b>1</b> — соответствие: кто что говорит (основное содержание).",
        "<b>2</b> — верно / неверно / в тексте не сказано.",
        "<b>3–9</b> — выбор ответа по интервью (полное понимание).",
        "Запись идёт один раз по инструкции КИМ. Ответы — в бланк № 1.",
        "На курсе стратегии аудирования — в рецептивной фазе каждого модуля.",
    ])))
    a(h("Чтение · задания 10–18 · 20 баллов", ul([
        "<b>10</b> — заголовки к абзацам (основное содержание).",
        "<b>11</b> — вставить пропущенные фрагменты (связи в тексте).",
        "<b>12–18</b> — выбор ответа (полное понимание).",
        "Объём текстов на экзамене — до 900 слов. Есть и несплошные тексты (таблицы) — это готовит к заданию 38.",
    ])))
    a(h("Грамматика и лексика · задания 19–36 · 18 баллов", ul([
        "<b>19–24</b> — грамматика: поставить слово в нужную форму (6 баллов).",
        "<b>25–29</b> — словообразование (5 баллов).",
        "<b>30–36</b> — выбор лексики в связном тексте (7 баллов).",
        "В бланке № 1: слова заглавными буквами, без лишних символов.",
        "На курсе грамматика копится по модулям. Тьютор в 37/38/4 комментирует только уже пройденное.",
    ])))

    a(section("Часть 2", "Задание 37<br>электронное письмо", "Подробно. Сначала задание — потом работы."))
    a(big("6 баллов", "максимум за письмо другу<br>РКЗ 2 · организация 2 · язык 2"))
    a(h("Сначала само задание", """
<p class="muted">Так выглядит КИМ. Дальше разберём, что с ним делать.</p>
<pre class="kim">37. You have received an email message from your English-speaking pen-friend Olive:

From: Olive@mail.uk
To: Russian_friend@ege.ru
Subject: St. Petersburg

…At college we are doing projects on the historic cities of the world.
If I choose St. Petersburg in Russia, what places of interest should I write about?
Is St. Petersburg popular among foreign and local tourists, and why?
What season is the best to visit St. Petersburg?
We’ve just returned from the trip to the seaside…

Write an email to Olive.
In your message:
  – answer her questions;
  – ask 3 questions about the trip.
Write 100–140 words. Remember the rules of email writing.</pre>
"""))
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
    a(h("Удачный ответ · 6 из 6", """
<span class="tag good">работа 8311 · Olive · 105 слов · К1 2 · К2 2 · К3 2</span>
<div class="example ok">Dear Olive,

Thanks for your email. I hope you're doing fine.

In your email you ask me some questions about St. Petersburg. I think you should write about Hermitage and Petergof. In my opinion St Petersburg is popular among foreign and local tourists because it's the most beautiful historic city of the world. I think summer is the best season to visit St. Petersburg.

By the way, I want to ask you some questions about the trip. How long was your trip? What interesting things did you see? Did you go to the trip by yourself?

I guess that's all for now. Write back soon.
Best wishes,
Liza</div>
<p class="muted">Язык не идеальный — так и бывает на 6. Petergof друг поймёт. Запятой после In my opinion нет — одну пунктуацию простили.</p>
""", small=True))
    a(h("Почему это 6, а не обрубок", ul([
        "Есть Dear Olive, Write back soon, Best wishes и только имя.",
        "Три ответа по существу, в том числе про Россию — так, что англичанин поймёт.",
        "Три вопроса <b>про поездку</b>, не про погоду.",
        "Абзацы и отдельные строки на месте.",
        "На курсе с первой сдачи требуем содержание и организацию как здесь. Язык комментируем по пройденным темам.",
    ])))
    a(h("Сначала задание · потом ноль", """
<pre class="kim">From: Mike@mail.uk  Subject: Mobile devices
…I’ve recently been involved in a school survey on gadgets and devices.
What device is your favourite, if any? What do you usually use it for?
Do you consider using mobile phones essential for young people, why or why not?
I’ve recently returned from a nice summer camp…
— answer his questions; ask 3 questions about the summer camp.</pre>
<span class="tag bad">работа 8447 · 0 из 6</span>
<div class="example bad">Hey, Mike.
How's it going? … Actually, i'm really glad to hear you again…
Wanna tell me more about your timespan out there?
Is it was nice or not? Can you recommend me visit any or better not?
I’ll be waiting for your emails.
Best wishes,
Danil</div>
""", small=True))
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
    a(h("Сначала само задание", """
<pre class="kim">38.1 Imagine that you are doing a project on why some Zetlanders refuse
to attend music schools. You have found some data on the subject – the
results of a survey (see the table below). Comment on the survey data
and give your opinion on the subject of the project.

The survey question: Why do you refuse to attend a music school?
  No fast result                         29%
  Time-consuming                         23%
  Not interested in music                19%
  Far from home                          15%
  No money for a quality instrument      14%

Write 200–250 words. Use the following plan:
  – make an opening statement on the subject of the project;
  – select and report 2–3 facts;
  – make 1–2 comparisons where relevant and give your comments;
  – outline a problem that can arise with learning to play a musical
    instrument and suggest a way of solving it;
  – conclude by giving and explaining your opinion on whether one
    should be able to play a musical instrument.</pre>
""", small=True))
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
    a(h("Удачный ответ · 12 из 14", """
<span class="tag good">работа 1025 · 224 слова · РКЗ 3 · орг. 2 · лекс. 2 · гр. 3 · орф. 2</span>
<div class="example ok">Nowadays people do not value music. As part of my project on why some Zetlanders refuse to attend music schools, I have found a table containing some relevant results of the opinion polls that I am going to comment on.

According to the data, the majority of the respondents choose "No fast result" … The second most sizeable group vote for "Time-consuming" (23%). … the least favoured option is "No money for a quality instrument" (14%)…

Looking more closely at the table, … "Not interested in music" … more widespread … than "Far from home" … 4 percentage points…

… one of the problems … is that one can not find a suitable teacher. … A person should attend trial lessons…

In conclusion, I believe that being able to play a musical instrument is important. That is because a person can always find comfort in music.</div>
""", small=True))
    a(h("Почему 12, а не 14", ul([
        "Есть проект, тема и opinion polls. Три факта с цифрами. Проблема из плана. Явное I believe.",
        "Сняли организацию и лексику: сравнили 19% и 15% (разница 4 пункта — слабое сравнение), комментарий про «другие хобби» из таблицы не следует.",
        "<i>vote for</i>, <i>learning techniques</i> вместо teaching methods; <i>can not</i> раздельно.",
        "На курсе лучше сразу сравнивать несхожие цифры, например 29% и 14%.",
        "Содержание и организацию с первой сдачи требуем как здесь. Язык — по пройденным темам.",
    ])))
    a(h("Сначала задание · потом ноль", """
<pre class="kim">38.1 … project on the preparations for the New Year that Zetlanders
consider most important … survey …
  Tidy the house 36% · Decorate a New Year tree 34% · Cook traditional
  dishes 20% · Buy presents 7% · Buy a new outfit 3%
… outline a problem that can arise with organizing a New Year party …
… opinion on the importance of preparing for New Year celebrations
well in advance.</pre>
<span class="tag bad">работа 8781 · 218 слов · 0 из 14</span>
<div class="example bad">… I have just found some data … and organised it in the table below.
… only third percent of respondents …
… 20 per cent … is only slightly lower than … decorate a New Year tree.
… only seven per cent of respondent buy presents …
In conclusion, I belive that people will celebrate New Year funny …</div>
""", small=True))
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
    a(h("Задание 1 · чтение вслух · 1 балл", """
<p>Подготовка 1,5 мин. Читать 1,5 мин. Ставят 1 или 0.</p>
<pre class="kim">Task 1. You have 1.5 minutes to read the text silently, then be ready
to read it out aloud. You will not have more than 1.5 minutes to read it.

Lake Baikal in Siberia is the deepest freshwater lake on Earth. It holds
about one fifth of the world’s unfrozen fresh water. In winter the surface
is covered with thick ice, and people walk and even drive on it. In summer
the water is cold but very clear. Scientists study unique fish and plants
that live only here. For many Russians Baikal is not just a lake but a
symbol of nature that must be protected.</pre>
<p class="muted">На экзамене текст другой. Важно: дочитать до конца, не пропускать слова, паузы по смыслу, звуки и ударение.</p>
""", small=True))
    a(h("Задание 1 · на что смотрят", ul([
        "Интонация, звуки, словесное и фразовое ударение.",
        "Уложиться в 1,5 минуты и дочитать текст.",
        "Не читать того, чего нет, и не пропускать строки.",
        "Риск нуля: речь почти не прочитать; 3+ смысловые замены звуков; пропуск 3+ слов; пауза, ломающая смысл.",
        "На курсе фонетика идёт по шагам 1–20. Сборка чтения вслух — к модулям 18–20.",
    ])))
    a(h("Задание 2 · четыре вопроса · 4 балла", """
<pre class="kim">Task 2. Study the advertisement.
You are considering going to the mountains and now you’d like to get
more information. In 1.5 minutes you are to ask four direct questions
to find out about the following:

        Join our journey to the mountains!

1) duration of the tour
2) price for one
3) student discounts
4) special equipment needed

You have 20 seconds to ask each question.</pre>
""", small=True))
    a(h("Задание 2 · как спрашивать", ul([
        "По <b>1 баллу</b> за вопрос. Каждый вопрос оценивают отдельно.",
        "Вступление и прощание <b>не нужны</b>.",
        "Строго по подсказке. If / whether → только общий вопрос.",
        "Первый вопрос должен прояснить, куда звоните: не How much is it? без названия.",
        "Последний вариант, даже если исправились на худший, и есть тот, что засчитают.",
        "Норма: <i>How long does the tour last?</i> · <i>How much does it cost for one person?</i> · <i>Are there any student discounts?</i> · <i>What special equipment is needed?</i>",
    ])))
    a(h("Задание 3 · интервью · 5 баллов", """
<p>Вопросы на экране вы <b>не видите заранее</b>. Слушайте. 40 секунд на ответ, 2–3 фразы. По 1 баллу за ответ.</p>
<pre class="kim">Interviewer: Hello everybody! It’s Teenagers Round the World Channel.
Our guest today is a teenager from Russia and we are going to discuss
teenagers’ attitude to local places of interest.

– What are some of the places of interest in your region? Why should
  a tourist see them?
– Is it important to preserve historical places? Why or why not?
– What is your favourite place in your home town? Why do you like it?
– What sort of places will be interesting for people in the future? Why?
– How can we make teenagers be more interested in local culture?</pre>
""", small=True))
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
    a(h("Сначала само задание", """
<pre class="kim">Task 4. Imagine that you and your friend are doing a school project
“Summer holidays”. You have found some photos to illustrate it but for
technical reasons you cannot send them now. Leave a voice message to
your friend explaining your choice of the photos and sharing some ideas
about the project. In 2.5 minutes be ready to:

  ● explain the choice of the illustrations for the project by briefly
    describing them and noting the differences;
  ● mention the advantages (1–2) of the two types of summer holidays;
  ● mention the disadvantages (1–2) of the two types of summer holidays;
  ● express your opinion on the subject of the project – which of these
    ways of spending summer holidays you preferred as a child and why.

You will speak for not more than 3 minutes (12–15 sentences).
You have to talk continuously.</pre>
""", small=True))
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
    a(h("Удачный ответ · 9 из 10", """
<span class="tag good">ответ 0487 · Summer holidays · РКЗ 4 · орг. 3 · язык 2</span>
<div class="example ok">Hi, Ann. How are you doing? I have found some photos for our project “Summer holidays”. … In the first picture … a mother with her daughter … in the garden planting. … The second picture … father with his son … on the beach. … two different types of summer holidays – in the countryside and on the beach.

The main advantage of … countryside is that you can help your parents with gardening … but … energy- and time-consuming … The main benefit of … the beach is that it’s very relaxing … disadvantage … sunstroke …

Talking about me, when I was a child, I preferred spending holidays on a beach because I was keen on swimming … That’s all what I wanted to say. Let me know what you think. Goodbye.</div>
<p class="muted">Язык 2, не 3: what do you think, a summer holidays, injure. Связки перед плюсами можно было явнее. Содержание закрыто.</p>
""", small=True))
    a(h("Неудачный ответ · 0 из 10", """
<span class="tag bad">ответ 9213 · Family pastime</span>
<div class="example bad">Hello, my dear friend! I’ve found two photos for hour project Family Pastime. And I’d like discuss with you. I chose these photos because they best illustrate family pastime. In the first picture we can see a family who spend their time on smart phone. Whiles in second picture we can see family who walking outside.

[дальше — длинные паузы, обрывки, достоинства не названы, мнение не разобрать]</div>
<p>Приветствие и слово project сами по себе задание не спасают. Нет различия, связанного с проектом, нет плюсов и минусов двух типов, нет понятного мнения. Содержание &lt; 50% → всё задание 0.</p>
<p class="muted">Ещё хуже обрубок без друга и проекта: “I’d like to compare and contrast two pictures… I like shopping online.”</p>
""", small=True))
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
    a(h("Три продукта каждые модуль", tbl(
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
        "Устные 1–3 знаете по формату; тренируете в Zoom и в фонетике.",
        "Задания 1–36 — в рецептивной фазе и в тесте модуля.",
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
        "--no-pdf-header-footer",
        f"--user-data-dir={CHROME_PROFILE}",
        f"--print-to-pdf={OUT_PDF}",
        html_path.resolve().as_uri(),
    ]
    result = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90)
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
