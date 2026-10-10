#!/usr/bin/env python3
"""Genera widget.jpg (formato widget XL 4x6 di iOS 27) dall'index.html del giorno.

Uso:  python3 make_widget.py            (legge index.html, scrive widget.jpg)
      python3 make_widget.py in.html out.jpg

Il widget mostra: testata con data, notizia principale Italia (grande, con foto),
Estero e Tecnologia affiancate (con foto), una seconda notizia per area in una riga.
Le foto vengono riprese dalle hero card di index.html (gia' incorporate in base64).
"""
import html
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Widget XL su iPhone: 364 x 594 punti (4x6 slot). Render a 3x -> 1092 x 1782 px.
W, H, SCALE = 364, 594, 3

SECTIONS = [("i", "Italia", "#EC672C", "#F0864C"),
            ("e", "Estero", "#E85A38", "#FF7A59"),
            ("t", "Tecnologia", "#5F4FC7", "#7C6CE0")]


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def parse(index_html):
    soup = BeautifulSoup(index_html, "html.parser")
    date_el = soup.select_one(".rail-date")
    date = ""
    if date_el:
        span = date_el.find("span")
        if span:
            span.extract()
        date = clean(date_el.get_text(" "))
    data = {}
    for key, *_ in SECTIONS:
        card = soup.select_one(f".hero-card.{key}")
        img = card.select_one(".hero-photo img") if card else None
        title = clean(card.select_one("h2").get_text()) if card and card.select_one("h2") else ""
        others = [clean(h.get_text()) for h in soup.select(f".list-col.{key} .row h4")]
        data[key] = {"img": (img.get("src") if img else "") or "", "title": title,
                     "second": others[0] if others else ""}
    return date, data


def photo(src, color):
    if src.startswith("data:image"):
        return f'<div class="ph" style="background:{color} url(\'{src}\') center/cover no-repeat"></div>'
    return f'<div class="ph" style="background:{color}"></div>'


def build(date, data):
    e = html.escape
    i, est, tec = (data[k] for k, *_ in SECTIONS)
    (_, _, ci, pi), (_, _, ce, pe), (_, _, ct, pt) = SECTIONS
    rows = "".join(
        f'<div class="row"><span class="dot" style="background:{c}"></span><span>{e(data[k]["second"])}</span></div>'
        for k, _, c, _ in SECTIONS if data[k]["second"])
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;background:#FFF8F3;font-family:Inter,"DejaVu Sans",sans-serif;-webkit-font-smoothing:antialiased}}
.wrap{{width:{W}px;height:{H}px;display:flex;flex-direction:column;padding:16px 14px 14px}}
.head{{display:flex;justify-content:space-between;align-items:baseline;padding:0 4px 10px}}
.brand{{font-size:20px;font-weight:800;color:#B4451A;letter-spacing:-.01em}}
.date{{font-size:13px;font-weight:600;color:#8A4A2C}}
.card{{border-radius:18px;overflow:hidden;display:flex;flex-direction:column;color:#fff}}
.ph{{flex:1;min-height:0}}
.body{{padding:9px 12px 11px}}
.tag{{font-size:11px;font-weight:700;opacity:.85;text-transform:uppercase;letter-spacing:.06em}}
.big h2{{font-size:17px;line-height:1.25;font-weight:700;margin-top:3px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.big{{height:236px}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:9px;height:196px}}
.small h2{{font-size:13.5px;line-height:1.25;font-weight:700;margin-top:2px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.small .body{{padding:8px 10px 10px;height:92px}}
.rows{{margin-top:12px;display:flex;flex-direction:column;gap:7px;padding:0 4px}}
.row{{display:flex;align-items:center;gap:8px;font-size:12.5px;font-weight:500;color:#3B1E10}}
.row span:last-child{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.dot{{width:8px;height:8px;border-radius:50%;flex:none}}
</style></head><body><div class="wrap">
<div class="head"><span class="brand">Rassegna</span><span class="date">{e(date)} · 6:30</span></div>
<div class="card big" style="background:{ci}">{photo(i["img"], pi)}
<div class="body"><div class="tag">Italia</div><h2>{e(i["title"])}</h2></div></div>
<div class="pair">
<div class="card small" style="background:{ce}">{photo(est["img"], pe)}
<div class="body"><div class="tag">Estero</div><h2>{e(est["title"])}</h2></div></div>
<div class="card small" style="background:{ct}">{photo(tec["img"], pt)}
<div class="body"><div class="tag">Tecnologia</div><h2>{e(tec["title"])}</h2></div></div>
</div>
<div class="rows">{rows}</div>
</div></body></html>"""


def main():
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "widget.jpg")
    date, data = parse(src.read_text(encoding="utf-8"))
    page_html = build(date, data)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        page.set_content(page_html, wait_until="load")
        page.screenshot(path=str(out), type="jpeg", quality=82, clip={"x": 0, "y": 0, "width": W, "height": H})
        browser.close()
    print(f"OK: {out} ({W * SCALE}x{H * SCALE}) — {date}")


if __name__ == "__main__":
    main()
