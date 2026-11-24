"""בונה את הדשבורד (HTML עצמאי) מהגרפים ומהמספרים של שלב 7."""
import base64, pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
b64 = lambda n: base64.b64encode((ROOT / "outputs/figures" / n).read_bytes()).decode()
df = pd.read_csv(ROOT / "outputs/Student_tests_results_clean.csv")
c, n = df[df["Test preparation course"] == "completed"], df[df["Test preparation course"] == "none"]
gap = {s: c[s].mean() - n[s].mean() for s in ["Math score", "Reading score", "Writing score"]}
assert round(gap["Math score"], 1) == 5.4 and round(gap["Reading score"], 1) == 7.3 and round(gap["Writing score"], 1) == 9.9
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
@media(max-width:820px){{.row,.cards,.txt{{grid-template-columns:1fr}}h1{{font-size:21px}}.scroll img{{min-width:620px}}}}
</style></head><body><div class="wrap">
<h1>האם קורס הכנה קשור לציונים גבוהים יותר?</h1>
<p class="q">שאלת המחקר: האם השלמת קורס הכנה קשורה לציונים גבוהים יותר גם כשמתחשבים במלגה ובהשכלת ההורים, ובאיזה מקצוע (מתמטיקה, קריאה או כתיבה) הקשר הזה חזק יותר? · 1,057 תלמידים</p>
<div class="answer"><b>כן.</b> תלמידים שהשלימו קורס הכנה קיבלו ציונים גבוהים יותר בכל קבוצת מלגה ובכל רמת השכלת הורים, והקשר חזק במיוחד בכתיבה.</div>
<div class="legend"><span><i class="sw" style="background:var(--blue)"></i>השלים קורס הכנה</span><span><i class="sw" style="background:var(--orange)"></i>לא השלים</span></div>
<section class="frame"><h2>ממוצע ציון לפי קורס ומלגה</h2><p>בכל קבוצת מלגה, מי שהשלים קורס קיבל ציון גבוה יותר, בכל שלושת המקצועות</p>
<div class="scroll"><img alt="גרף עמודות: ממוצע ציונים לפי השלמת קורס הכנה ומלגה, בשלושת המקצועות" src="data:image/png;base64,{b64('04_bars_course_by_tuition.png')}"></div></section>
<div class="gap"></div>
<div class="row">
<section class="frame"><h2>הפער לפי השכלת הורים ומקצוע</h2><p>הפער חיובי בכל 18 התאים, וגדול ביותר בכתיבה</p>
<img alt="מפת חום: הפער בנקודות בין מי שהשלים קורס למי שלא, לפי השכלת ההורים ומקצוע" src="data:image/png;base64,{b64('05_heatmap_gap_by_education.png')}"></section>
<div class="side">
<div class="card"><div class="num">+{gap['Math score']:.1f}</div><div class="lbl">מתמטיקה · פער בנקודות<br>(השלים פחות לא השלים)</div></div>
<div class="card"><div class="num">+{gap['Reading score']:.1f}</div><div class="lbl">קריאה · פער בנקודות</div></div>
<div class="card hi"><div class="num">+{gap['Writing score']:.1f}</div><div class="lbl"><b>כתיבה – הפער הגדול ביותר</b><br>פער בנקודות</div></div>
</div></div>
<div class="gap"></div>
<div class="txt">
<section class="frame"><h2>מסקנות</h2><ul>
<li>הקורס קשור לציונים גבוהים יותר בכל קבוצת מלגה ובכל רמת השכלה (18 מתוך 18 תאים).</li>
<li>הקשר חזק יותר בכתיבה, ובעיקר אצל תלמידים שהוריהם some college או associate's degree (כ־11 נקודות).</li></ul></section>
<section class="frame"><h2>מגבלות</h2><ul>
<li>זה קשר ולא סיבתיות: ייתכן שתלמידים שבוחרים בקורס שונים מאחרים בדרכים שלא נמדדו.</li>
<li>לא נעשה מבחן מובהקות. בקבוצות קטנות, כמו master's degree (20 ו־40 תלמידים), הפער פחות יציב.</li>
<li>מלגה והשכלת הורים נבדקו בנפרד, לא יחד.</li></ul></section>
</div></div></body></html>"""
out = ROOT / "outputs" / "dashboard.html"; out.write_text(html, encoding="utf-8"); print(out, f"{len(html)/1e3:.0f}KB")
