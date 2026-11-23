"""חקר ראשוני (שלב 5) של הקובץ הנקי – קריאה בלבד, הקובץ לא משתנה."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "outputs" / "Student_tests_results_clean.csv")
FIG = ROOT / "outputs" / "figures"; FIG.mkdir(parents=True, exist_ok=True)
SCORES = ["Math score", "Reading score", "Writing score"]
FACTORS = ["Tuition", "Parental level of education", "Test preparation course", "Gender", "Race/Ethnicity"]
EDU_ORDER = ["some high school", "high school", "some college", "associate's degree", "bachelor's degree", "master's degree"]
ORDER = {"Parental level of education": EDU_ORDER, "Race/Ethnicity": sorted(df["Race/Ethnicity"].unique())}
dedup = df.drop_duplicates()

print("== 1. הבנת הנתונים ==")
print("שורות:", len(df), "| עמודות:", df.shape[1], "| חוסרים:", int(df.isna().sum().sum()))
print("ללא כפילויות:", len(dedup))
for f in FACTORS:
    vc = df[f].value_counts().reindex(ORDER.get(f, df[f].value_counts().index))
    print(f"\n{f}:\n" + (pd.DataFrame({"n": vc, "%": (vc / len(df) * 100).round(1)})).to_string())

print("\n== 2. ממוצעי ציונים לפי גורם ==")
gaps = []
for f in FACTORS:
    m = df.groupby(f)[SCORES].mean().reindex(ORDER.get(f, None)).round(1)
    md = dedup.groupby(f)[SCORES].mean().reindex(m.index).round(1)
    print(f"\n{f}:\n{m.to_string()}")
    for s in SCORES:
        gaps.append({"factor": f, "subject": s, "gap": round(m[s].max() - m[s].min(), 1),
                     "gap_no_dups": round(md[s].max() - md[s].min(), 1),
                     "high": m[s].idxmax(), "low": m[s].idxmin()})
gaps = pd.DataFrame(gaps)
print("\nפער בין הקבוצה הגבוהה לנמוכה (עם/בלי כפילויות):\n", gaps.to_string(index=False))
print("\nהפרש מקסימלי בממוצע כללי בגלל כפילויות:",
      (df[SCORES].mean() - dedup[SCORES].mean()).abs().round(2).to_dict())
print("\nמתאם בין המקצועות:\n", df[SCORES].corr().round(2).to_string())

print("\n== 3. חריגים (IQR) ==")
for s in SCORES:
    q1, q3 = df[s].quantile([.25, .75]); iqr = q3 - q1; lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    out = df[(df[s] < lo) | (df[s] > hi)]
    print(f"{s}: טווח {df[s].min()}–{df[s].max()}, גבול תחתון {lo}, עליון {hi}, חריגים {len(out)}: {sorted(out[s].tolist())}")
low = df[(df[SCORES] < 40).any(axis=1)]
print("\nתלמידים עם ציון מתחת ל-40 במקצוע אחד לפחות:", len(low))
for f in ["Tuition", "Test preparation course"]:
    print(f"  {f}:", (low[f].value_counts(normalize=True) * 100).round(0).to_dict(),
          "| בכלל התלמידים:", (df[f].value_counts(normalize=True) * 100).round(0).to_dict())

# ---------- גרפים ----------
C = {"Math score": "#2a78d6", "Reading score": "#eb6834", "Writing score": "#1baf7a"}
HEB = {"Math score": "Math", "Reading score": "Reading", "Writing score": "Writing"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#8a8984", "axes.labelcolor": "#52514e",
                     "xtick.color": "#52514e", "ytick.color": "#52514e"})

fig, axes = plt.subplots(5, 1, figsize=(9, 17))
for ax, f in zip(axes, FACTORS):
    m = df.groupby(f)[SCORES].mean().reindex(ORDER.get(f, None))
    n = df[f].value_counts()
    x = range(len(m)); w = 0.26
    for i, s in enumerate(SCORES):
        ax.bar([xi + (i - 1) * (w + 0.02) for xi in x], m[s], w, color=C[s], label=HEB[s])
    ax.set_xticks(list(x)); ax.set_xticklabels([f"{c}\n(n={n[c]})" for c in m.index], fontsize=9)
    ax.set_ylim(0, 85); ax.set_ylabel("Mean score"); ax.set_title(f, loc="left", fontsize=12, color="#0b0b0b")
    ax.grid(axis="y", color="#e4e3df"); ax.set_axisbelow(True)
axes[0].legend(ncol=3, frameon=False, loc="lower right", bbox_to_anchor=(1, 1.0))
fig.suptitle("Mean score by factor and subject", x=0.02, ha="left", fontsize=14)
fig.tight_layout(rect=(0, 0, 1, 0.975)); fig.savefig(FIG / "01_mean_by_factor.png", dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 4.5))
piv = gaps.pivot(index="factor", columns="subject", values="gap").reindex(FACTORS)
y = range(len(piv)); h = 0.26
for i, s in enumerate(SCORES):
    bars = ax.barh([yi + (i - 1) * (h + 0.02) for yi in y], piv[s], h, color=C[s], label=HEB[s])
    ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=8, color="#52514e")
ax.set_yticks(list(y)); ax.set_yticklabels(piv.index); ax.invert_yaxis()
ax.set_xlabel("Points between highest and lowest group"); ax.grid(axis="x", color="#e4e3df"); ax.set_axisbelow(True)
ax.legend(ncol=3, frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0))
ax.set_title("Gap in mean score between groups", loc="left", fontsize=13, pad=28)
fig.tight_layout(); fig.savefig(FIG / "02_gap_by_factor.png", dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4.5))
bp = ax.boxplot([df[s] for s in SCORES], tick_labels=[HEB[s] for s in SCORES], patch_artist=True, widths=0.5,
                flierprops=dict(marker="o", markersize=6, markerfacecolor="#e34948", markeredgecolor="white"),
                medianprops=dict(color="#0b0b0b", linewidth=2))
for patch, s in zip(bp["boxes"], SCORES):
    patch.set_facecolor(C[s]); patch.set_alpha(0.55); patch.set_edgecolor(C[s])
ax.set_ylabel("Score"); ax.grid(axis="y", color="#e4e3df"); ax.set_axisbelow(True)
ax.set_title("Score distribution per subject (red dots = IQR outliers)", loc="left", fontsize=13)
fig.tight_layout(); fig.savefig(FIG / "03_outliers_boxplot.png", dpi=130); plt.close(fig)
print("\nגרפים נשמרו ב-", FIG)
