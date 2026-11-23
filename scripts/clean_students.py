"""ניקוי Student_tests_results.xlsx לפי הפרומפט שאושר (שלב 4 בפרויקט).
המקור לא משתנה; הפלט נשמר ב-outputs/."""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Student_tests_results.xlsx"
OUT = ROOT / "outputs" / "Student_tests_results_clean.csv"
SCORES = ["Math score", "Reading score", "Writing score"]

df = pd.read_excel(SRC)
print("== לפני הניקוי ==")
print("שורות:", len(df), "| עמודות:", list(df.columns))
print("חוסרים לפי עמודה:\n", df.isna().sum().to_string())
print("שורות עם חוסר אחד לפחות:", df.isna().any(axis=1).sum())
print("שורות כפולות (זהות לגמרי):", df.duplicated().sum())

# 1. אחידות טקסט: הסרת רווחי קצה; בדיקה אם יש אותו ערך בכתיב/אותיות שונות
text_cols = [c for c in df.columns if c not in SCORES]
changed = {}
for c in text_cols:
    before = df[c].copy()
    df[c] = df[c].str.strip()
    changed[c] = int(((before != df[c]) & before.notna()).sum())
    vals = df[c].dropna().unique()
    if len({v.lower() for v in vals}) < len(vals):
        print(f"  שים לב: ב-{c} יש ערכים שנבדלים רק באותיות גדולות/קטנות")
print("\nתאי טקסט ששונו (רווחים מיותרים):", changed)
for c in text_cols:
    print(f"  {c}: {sorted(df[c].dropna().unique())}")

# 2. מחיקת שורות עם מידע חסר
rows_before = len(df)
df = df.dropna()
print("\nנמחקו בגלל חוסרים:", rows_before - len(df))

# 3. כפילויות: נשארות (אין מזהה תלמיד)
print("כפילויות שנשארו בכוונה:", df.duplicated().sum())

# 4. טווח ציונים 0-100
out_of_range = {c: int(((df[c] < 0) | (df[c] > 100)).sum()) for c in SCORES}
print("ציונים מחוץ לטווח 0-100:", out_of_range)
df[SCORES] = df[SCORES].clip(0, 100)
non_int = {c: int((df[c] % 1 != 0).sum()) for c in SCORES}
print("ציונים לא שלמים:", non_int)
df[SCORES] = df[SCORES].astype(int)

print("\n== אחרי הניקוי ==")
print("שורות:", len(df), "| חוסרים:", int(df.isna().sum().sum()))
print(df[SCORES].describe().round(1).to_string())
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print("\nנשמר:", OUT)
