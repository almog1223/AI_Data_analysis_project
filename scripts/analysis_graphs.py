"""שלב 7: גרפים וסטטיסטיקה תיאורית לשאלת המחקר.
האם השלמת קורס הכנה קשורה לציונים גבוהים יותר גם כשמתחשבים במלגה ובהשכלת ההורים,
ובאיזה מקצוע הקשר חזק יותר?"""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "outputs" / "Student_tests_results_clean.csv")
FIG = ROOT / "outputs" / "figures"; FIG.mkdir(parents=True, exist_ok=True)
SUBJ = {"Math score": "מתמטיקה", "Reading score": "קריאה", "Writing score": "כתיבה"}
EDU = ["some high school", "high school", "some college", "associate's degree", "bachelor's degree", "master's degree"]
BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"
H = lambda s: s  # matplotlib מטפל בעברית RTL בעצמו
plt.rcParams.update({"font.family": ["Arial Hebrew", "Arial", "DejaVu Sans"], "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": "#8a8984", "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "font.size": 11})

def gap_table(sub):
    c = sub[sub["Test preparation course"] == "completed"]; n = sub[sub["Test preparation course"] == "none"]
    return {s: (c[s].mean() - n[s].mean(), c[s].median() - n[s].median(), len(c), len(n)) for s in SUBJ}

# ---- טבלאות ----
print("== פער כללי (ממוצע / חציון), לכל מקצוע ==")
for s, (gm, gd, nc, nn) in gap_table(df).items():
    print(f"{s}: פער ממוצע {gm:.1f} | פער חציון {gd:.1f} | n={nc}/{nn}")
print("\n== לפי מלגה ==")
rows = []
for t, sub in df.groupby("Tuition"):
    for s, (gm, gd, nc, nn) in gap_table(sub).items():
        rows.append((t, s, round(gm, 1), round(gd, 1), nc, nn))
print(pd.DataFrame(rows, columns=["tuition", "subject", "mean_gap", "median_gap", "n_completed", "n_none"]).to_string(index=False))
print("\n== לפי השכלת הורים (פער ממוצע, n=שהשלימו/שלא) ==")
G = pd.DataFrame(index=EDU, columns=list(SUBJ), dtype=float); N = {}
for e in EDU:
    for s, (gm, gd, nc, nn) in gap_table(df[df["Parental level of education"] == e]).items():
        G.loc[e, s] = gm; N[(e, s)] = (nc, nn)
print(G.round(1).to_string())
print({e: N[(e, "Math score")] for e in EDU})
print("\nפער ממוצע ממוצע לפי מקצוע (על 6 רמות השכלה):", G.mean().round(1).to_dict())

# ---- גרף 1: עמודות ----
fig, axes = plt.subplots(1, 3, figsize=(13, 5.2), sharey=True)
groups = [("free/reduced", "עם מלגה"), ("standard", "בלי מלגה")]
for ax, (s, heb) in zip(axes, SUBJ.items()):
    for gi, (tk, tl) in enumerate(groups):
        sub = df[df["Tuition"] == tk]
        for ci, (ck, col) in enumerate([("completed", BLUE), ("none", ORANGE)]):
            v = sub[sub["Test preparation course"] == ck][s].mean()
            x = gi + (ci - 0.5) * 0.38
            ax.bar(x, v, 0.36, color=col, label=H("השלים קורס הכנה") if ck == "completed" else H("לא השלים"))
            ax.text(x, v + 1.2, f"{v:.1f}", ha="center", fontsize=10, color=INK)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([H(f"{tl}\n(n={len(df[(df['Tuition']==tk)&(df['Test preparation course']=='completed')])}/"
                          f"{len(df[(df['Tuition']==tk)&(df['Test preparation course']=='none')])})") for tk, tl in groups], fontsize=10)
    ax.set_title(H(heb), fontsize=13, color=INK); ax.set_ylim(0, 100); ax.grid(axis="y", color=GRID); ax.set_axisbelow(True)
axes[0].set_ylabel(H("ממוצע ציון (0–100)"))
h, l = axes[0].get_legend_handles_labels(); u = dict(zip(l, h))
fig.legend(u.values(), u.keys(), loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.93))
fig.suptitle(H("ממוצע ציונים לפי השלמת קורס הכנה ומלגה, בשלושת המקצועות"), fontsize=15, y=0.99)
fig.text(0.5, 0.01, H("סוג תלמיד (בסוגריים: מספר תלמידים שהשלימו קורס / שלא השלימו)"), ha="center", color=MUTED, fontsize=10)
fig.tight_layout(rect=(0, 0.03, 1, 0.9)); fig.savefig(FIG / "04_bars_course_by_tuition.png", dpi=130); plt.close(fig)

# ---- גרף 2: מפת חום ----
cmap = LinearSegmentedColormap.from_list("b", ["#e8f0fb", "#9cc0ef", BLUE, "#14407a"])
vmax = max(np.nanmax(G.values), 1)
fig, ax = plt.subplots(figsize=(9, 6.4))
for i, e in enumerate(EDU):
    for j, s in enumerate(SUBJ):
        v = G.loc[e, s]; nc, nn = N[(e, s)]
        col = ORANGE if v < 0 else cmap(max(v, 0) / vmax)
        small = min(nc, nn) < 15
        ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=col, edgecolor="white", linewidth=3))
        if small: ax.add_patch(plt.Rectangle((j + .04, i + .04), .92, .92, fill=False, edgecolor=INK, linewidth=1.5, linestyle="--"))
        lum = 0.2126 * col[0] + 0.7152 * col[1] + 0.0722 * col[2] if not isinstance(col, str) else 0.5
        tc = "white" if (v >= vmax * 0.5 or v < 0) else INK
        ax.text(j + .5, i + .42, f"{v:+.1f}", ha="center", va="center", fontsize=15, fontweight="bold", color=tc)
        ax.text(j + .5, i + .72, f"n={nc}/{nn}" + (" ⚠" if small else ""), ha="center", va="center", fontsize=9, color=tc)
ax.set_xlim(0, 3); ax.set_ylim(6, 0)
ax.set_xticks([.5, 1.5, 2.5]); ax.set_xticklabels([H(v) for v in SUBJ.values()], fontsize=12); ax.xaxis.tick_top()
ax.set_yticks([i + .5 for i in range(6)]); ax.set_yticklabels(EDU, fontsize=11)
ax.set_ylabel(H("השכלת ההורים (מהנמוכה לגבוהה)"))
for sp in ax.spines.values(): sp.set_visible(False)
ax.tick_params(length=0)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, vmax)); cb = fig.colorbar(sm, ax=ax, fraction=0.04, pad=0.03)
cb.set_label(H("הפער בנקודות (השלים קורס פחות לא השלים)"), color=MUTED); cb.outline.set_visible(False)
fig.suptitle(H("פער בציון בין מי שהשלים קורס הכנה למבחן למי שלא, לפי השכלת ההורים ומקצוע"), fontsize=13, x=0.5, y=0.99)
fig.text(0.5, 0.01, H("מסגרת מקווקווה ⚠ = פחות מ־15 תלמידים באחת הקבוצות, הפער פחות אמין"), ha="center", color=MUTED, fontsize=9.5)
fig.tight_layout(rect=(0, 0.03, 1, 0.96)); fig.savefig(FIG / "05_heatmap_gap_by_education.png", dpi=130); plt.close(fig)
