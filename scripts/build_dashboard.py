"""בונה את הדשבורד (HTML עצמאי) מהגרפים ומהמספרים של שלב 7."""
import base64, pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
b64 = lambda n: base64.b64encode((ROOT / "outputs/figures" / n).read_bytes()).decode()
df = pd.read_csv(ROOT / "outputs/Student_tests_results_clean.csv")
c, n = df[df["Test preparation course"] == "completed"], df[df["Test preparation course"] == "none"]
gap = {s: c[s].mean() - n[s].mean() for s in ["Math score", "Reading score", "Writing score"]}
assert round(gap["Math score"], 1) == 5.4 and round(gap["Reading score"], 1) == 7.3 and round(gap["Writing score"], 1) == 9.9

# ---- מפת חום כטבלת HTML (טקסט חד וקריא במקום תמונה) ----
SUBJ = [("Math score", "מתמטיקה"), ("Reading score", "קריאה"), ("Writing score", "כתיבה")]
EDU = [("some high school", "תיכון חלקי"), ("high school", "תיכון מלא"),
       ("some college", "לימודים על־תיכוניים חלקיים"), ("associate's degree", "תואר מכללה (דו־שנתי)"),
       ("bachelor's degree", "תואר ראשון"), ("master's degree", "תואר שני")]
RAMP = ["#e8f0fb", "#9cc0ef", "#2a78d6", "#14407a"]
def ramp(t):
    t = min(max(t, 0), 1) * (len(RAMP) - 1); i = min(int(t), len(RAMP) - 2); f = t - i
    a, b = [tuple(int(h[k:k + 2], 16) for k in (1, 3, 5)) for h in (RAMP[i], RAMP[i + 1])]
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * f) for x, y in zip(a, b))
cells = {}
for e, _ in EDU:
    sub = df[df["Parental level of education"] == e]
    sc, sn = sub[sub["Test preparation course"] == "completed"], sub[sub["Test preparation course"] == "none"]
    for s, _ in SUBJ:
        cells[(e, s)] = (sc[s].mean() - sn[s].mean(), len(sc), len(sn))
vmax = max(v for v, _, _ in cells.values())
assert min(v for v, _, _ in cells.values()) > 0
rows_html = ""
for e, eh in EDU:
    tds = ""
    for s, _ in SUBJ:
        v, nc, nn = cells[(e, s)]; bg = ramp(v / vmax); fg = "#fff" if v >= vmax * 0.5 else "#0b0b0b"
        tds += (f'<td style="background:{bg};color:{fg}"><span class="v">+{v:.1f}</span>'
                f'<span class="n">{nc} השלימו · {nn} לא</span></td>')
    rows_html += f'<tr><th scope="row">{eh}<span class="en">{e}</span></th>{tds}</tr>'
heat = (f'<table class="heat"><thead><tr><th scope="col" class="corner">השכלת ההורים ↓</th>'
        + "".join(f'<th scope="col">{h}</th>' for _, h in SUBJ) + f'</tr></thead><tbody>{rows_html}</tbody></table>'
        f'<div class="scale"><span>פער קטן</span><i style="background:linear-gradient(to left,{",".join(RAMP)})"></i><span>פער גדול ({vmax:.1f}+)</span></div>')
html = f"""<!doctype html>
<html lang="he" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>דשבורד קורס הכנה וציונים</title>
<style>
:root{{color-scheme:light;--bg:#f6f6f4;--card:#fff;--ink:#0b0b0b;--mut:#52514e;--line:#e4e3df;--blue:#2a78d6;--orange:#eb6834}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:"Arial Hebrew",Arial,system-ui,sans-serif;line-height:1.5}}
.wrap{{max-width:1180px;margin:0 auto;padding:24px 16px 40px}}
h1{{font-size:26px;margin:0 0 6px}}.q{{color:var(--mut);margin:0 0 14px}}
.answer{{background:var(--card);border-inline-start:5px solid var(--blue);border-radius:8px;padding:14px 18px;font-size:18px;margin-bottom:18px;border:1px solid var(--line);border-inline-start:5px solid var(--blue)}}
.row{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.frame{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}}
.frame h2{{font-size:16px;margin:0 0 2px}}.frame p{{margin:0 0 10px;color:var(--mut);font-size:14px}}
.frame img{{width:100%;height:auto;display:block}}.row>*,.cards>*,.txt>*,.side>*{{min-width:0}}.scroll{{overflow-x:auto}}.side{{display:grid;grid-template-rows:repeat(3,1fr);gap:12px}}.side .card{{display:flex;flex-direction:column;justify-content:center;padding:10px}}.side .card .num{{font-size:36px}}.gap{{height:16px}}
.legend{{display:flex;gap:16px;font-size:14px;color:var(--mut);margin:0 0 8px}}.sw{{display:inline-block;width:12px;height:12px;border-radius:3px;margin-inline-end:6px;vertical-align:-1px}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:16px 0}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;text-align:center}}
.card .num{{font-size:42px;font-weight:700;line-height:1.1}}.card .lbl{{color:var(--mut);font-size:15px}}
.card.hi{{border:2px solid var(--blue)}}.card.hi .num{{color:var(--blue)}}
.txt{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.txt .frame h2{{margin-bottom:6px}}ul{{margin:0;padding-inline-start:20px;font-size:15px}}li{{margin-bottom:6px}}
.heat{{width:100%;border-collapse:separate;border-spacing:4px;table-layout:fixed}}
.heat th{{font-size:16px;font-weight:700;padding:6px 8px}}.heat thead th{{text-align:center}}.heat .corner{{text-align:start;color:var(--mut);font-weight:400;font-size:14px;width:34%}}
.heat tbody th{{text-align:start;font-size:15px}}.heat .en{{display:block;font-weight:400;font-size:12px;color:var(--mut);direction:ltr;text-align:right}}
.heat .v,.card .num{{direction:ltr;unicode-bidi:isolate}}
.heat td{{text-align:center;padding:12px 6px;border-radius:6px}}.heat .v{{display:block;font-size:24px;font-weight:700;line-height:1.2}}.heat .n{{display:block;font-size:12px;opacity:.85}}
.scale{{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--mut);margin-top:10px}}.scale i{{flex:0 1 220px;height:10px;border-radius:5px}}
@media(max-width:820px){{.row,.cards,.txt{{grid-template-columns:1fr}}h1{{font-size:21px}}.scroll img{{min-width:620px}}.heat .corner{{width:30%}}.heat .v{{font-size:19px}}.heat th{{font-size:13px}}.heat tbody th{{font-size:13px}}.heat .n{{font-size:10.5px}}}}
</style></head><body><div class="wrap">
<h1>האם קורס הכנה קשור לציונים גבוהים יותר?</h1>
<p class="q">שאלת המחקר: האם השלמת קורס הכנה קשורה לציונים גבוהים יותר גם כשמתחשבים במלגה ובהשכלת ההורים, ובאיזה מקצוע (מתמטיקה, קריאה או כתיבה) הקשר הזה חזק יותר?</p>
<p class="q">מבוסס על נתוני 1,057 תלמידים</p>
<div class="answer"><b>כן.</b> הממוצע של תלמידים שהשלימו קורס הכנה גבוה יותר בכל קבוצות המלגה ובכל רמות השכלת ההורים. הפער הגדול ביותר הוא בכתיבה.</div>
<div class="legend"><span><i class="sw" style="background:var(--blue)"></i>השלים קורס הכנה</span><span><i class="sw" style="background:var(--orange)"></i>לא השלים</span></div>
<section class="frame"><h2>ממוצע ציון לפי קורס ומלגה</h2><p>גם בקרב תלמידים עם מלגה וגם בקרב תלמידים בלי מלגה, הממוצע של מי שהשלים קורס גבוה יותר, בכל שלושת המקצועות</p>
<div class="scroll"><img alt="גרף עמודות: ממוצע ציונים לפי השלמת קורס הכנה ומלגה, בשלושת המקצועות" src="data:image/png;base64,{b64('04_bars_course_by_tuition.png')}"></div></section>
<div class="gap"></div>
<section class="frame"><h2>הפער לפי השכלת ההורים ומקצוע</h2><p>בכל תא: בכמה נקודות הממוצע של מי שהשלים קורס גבוה מהממוצע של מי שלא השלים. בכל 18 השילובים הפער חיובי, והוא הגדול ביותר בכתיבה.</p>
<div class="scroll">{heat}</div></section>
<div class="cards">
<div class="card"><div class="num">+{gap['Math score']:.1f}</div><div class="lbl">מתמטיקה<br>נקודות יותר בממוצע למי שהשלים קורס</div></div>
<div class="card"><div class="num">+{gap['Reading score']:.1f}</div><div class="lbl">קריאה<br>נקודות יותר בממוצע למי שהשלים קורס</div></div>
<div class="card hi"><div class="num">+{gap['Writing score']:.1f}</div><div class="lbl"><b>כתיבה – הפער הגדול ביותר</b><br>נקודות יותר בממוצע למי שהשלים קורס</div></div>
</div>
<div class="txt">
<section class="frame"><h2>מסקנות</h2><ul>
<li>הקורס קשור לציונים גבוהים יותר בכל קבוצת מלגה ובכל רמת השכלה (בכל 18 השילובים של מקצוע ורמת השכלה).</li>
<li>הקשר חזק יותר בכתיבה, ובעיקר אצל תלמידים שהשכלת הוריהם היא לימודים על־תיכוניים חלקיים או תואר מכללה (כ־11 נקודות).</li></ul></section>
<section class="frame"><h2>מגבלות</h2><ul>
<li>הממצא מראה קשר, לא סיבה ותוצאה: ייתכן שתלמידים שבוחרים לעשות את הקורס שונים מהאחרים בדרכים שלא נמדדו, למשל במוטיבציה.</li>
<li>לא נעשה מבחן מובהקות. בקבוצות קטנות, כמו תלמידים שהשכלת הוריהם היא תואר שני (20 השלימו ו־40 לא), הפער פחות יציב.</li>
<li>בדקנו את המלגה ואת השכלת ההורים כל אחת בנפרד, ולא את שתיהן יחד.</li></ul></section>
</div></div></body></html>"""
out = ROOT / "outputs" / "dashboard.html"; out.write_text(html, encoding="utf-8"); print(out, f"{len(html)/1e3:.0f}KB")
