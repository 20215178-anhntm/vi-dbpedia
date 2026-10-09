"""Figures for the slides (PNG, presentation/figs) and the paper (PDF, paper/figures).

Palette follows the HUST/SoICT slide template: red C02034, dark 222222, grey 6B6B6B,
card F7F8FA / E4E7EB, pink FBE9EC.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
PNG = HERE / "figs"
PDF = HERE.parent / "paper" / "figures"
PNG.mkdir(exist_ok=True)
PDF.mkdir(parents=True, exist_ok=True)

RED, DARK, GREY, CARD, BORDER, PINK, DEEP = "#C02034", "#222222", "#6B6B6B", "#F7F8FA", "#E4E7EB", "#FBE9EC", "#8E1626"
BLUE, GREEN = "#3D6DB5", "#2E7D46"
plt.rcParams.update({"font.family": ["Arial", "DejaVu Sans"], "font.size": 11, "axes.edgecolor": "#BBBBBB",
                     "axes.labelcolor": DARK, "xtick.color": GREY, "ytick.color": GREY})
FACTS = json.loads((HERE / "facts.json").read_text(encoding="utf8"))


def save(fig, name):
    fig.savefig(PNG / f"{name}.png", dpi=220, bbox_inches="tight", facecolor="white")
    fig.savefig(PDF / f"{name}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def box(ax, x, y, w, h, title, sub=None, fc=CARD, ec=BORDER, tc=DARK, sc=GREY, fs=11, lw=1.2, title_bold=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec=ec, lw=lw))
    if sub:
        ax.text(x + w / 2, y + h * 0.63, title, ha="center", va="center", fontsize=fs, color=tc,
                fontweight="bold" if title_bold else "normal")
        ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center", fontsize=fs - 2, color=sc)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=fs, color=tc,
                fontweight="bold" if title_bold else "normal")


def arrow(ax, p, q, color=DARK, lw=1.6, style="-|>", ls="-", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=14, color=color, lw=lw,
                                 linestyle=ls, connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))


# ------------------------------------------------------------------ 1. pipeline
def pipeline():
    fig, ax = plt.subplots(figsize=(13, 4.6))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    steps = [("Wikipedia dump", "XML + langlinks\n+ page_props"),
             ("Collection", "44,003 articles\n317k redirects"),
             ("Extraction", "YAML mappings\n1.51M triples"),
             ("Reasoning", "OWL 2 RL + rules\n2.64M inferred"),
             ("Linking", "32,465 → DBpedia\n43,145 → Wikidata"),
             ("Endpoint", "Fuseki TDB2\n4 named graphs")]
    w, h, y = 1.75, 1.35, 1.6
    xs = [0.15 + i * 2.15 for i in range(len(steps))]
    for i, (x, (t, s)) in enumerate(zip(xs, steps)):
        hl = t in ("Reasoning",)
        box(ax, x, y, w, h, t, s, fc=PINK if hl else CARD, ec=RED if hl else BORDER, fs=12.5)
        if i:
            arrow(ax, (xs[i - 1] + w, y + h / 2), (x, y + h / 2))
    # ontology on top
    ox, ow = 3.55, 5.5
    box(ax, ox, 3.55, ow, 0.9, "Ontology vidbo (OWL 2 DL)", "48 classes · 115 properties · 13 defined classes · 10 chains",
        fc=RED, ec=RED, tc="white", sc="#FCE4E8", fs=12.5)
    arrow(ax, (xs[2] + w / 2 + 0.15, 3.6), (xs[2] + w / 2, y + h), color=RED)
    arrow(ax, (xs[3] + w / 2 - 0.15, 3.6), (xs[3] + w / 2, y + h), color=RED)
    # SHACL + users below
    box(ax, xs[3], 0.15, w, 0.85, "SHACL", "data quality", fs=11.5)
    arrow(ax, (xs[3] + w / 2, y), (xs[3] + w / 2, 1.0))
    box(ax, xs[5], 0.15, w, 0.85, "Web · SPARQL · CLI", "Linked Data URIs", fs=11)
    arrow(ax, (xs[5] + w / 2, y), (xs[5] + w / 2, 1.0))
    box(ax, xs[4], 0.15, w, 0.85, "DBpedia endpoint", "verification", fs=11)
    arrow(ax, (xs[4] + w / 2, y), (xs[4] + w / 2, 1.0), style="<|-|>")
    save(fig, "fig_pipeline")


# ------------------------------------------------------------------ 2. class hierarchy
def hierarchy():
    fig, ax = plt.subplots(figsize=(13, 6.3))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6.3)
    ax.axis("off")
    cols = [
        ("Agent", 3.2, [("Person", 0, ""), ("Monarch", 1, "≡"), ("VietnameseMonarch", 2, "≡"), ("MonarchWarrior", 2, "≡"),
                        ("RoyalChild", 1, "≡"), ("RoyalTitleHolder", 1, "≡"), ("OfficeHolder", 1, "≡"),
                        ("RoyalCourtOfficial", 2, "≡"), ("MilitaryPerson", 1, ""), ("MilitaryCommander", 2, "≡"),
                        ("Writer", 1, "⊒"), ("CentenarianPerson", 1, "R"), ("Group", 0, ""), ("Dynasty", 1, ""),
                        ("VietnameseDynasty", 2, "")]),
        ("Place", 3.55, [("PopulatedPlace", 0, ""), ("State", 1, ""), ("FormerState", 2, "⊒"),
                         ("AdministrativeUnit", 1, "≡"), ("FirstLevelUnit", 2, "≡"), ("Province, Municipality", 3, ""),
                         ("SecondLevelUnit", 2, "≡"), ("District", 3, ""), ("ThirdLevelUnit", 2, "≡"),
                         ("Commune, Ward,", 3, ""), ("Township, SpecialZone", 3, ""), ("HistoricalAdminUnit", 2, "⊒"),
                         ("Region", 0, "")]),
        ("Event", 1.95, [("MilitaryConflict", 0, ""), ("War", 1, ""), ("Battle", 1, ""), ("Campaign", 1, ""),
                         ("Uprising", 1, "")]),
        ("Work", 1.45, [("WrittenWork", 0, "")]),
        ("Tenure", 1.95, [("Reign", 0, ""), ("OfficeTenure", 0, ""), ("RoyalTitleTenure", 0, "")]),
    ]
    x = 0.05
    for title, w, items in cols:
        top = 6.2
        hgt = 0.6 + 0.33 * len(items)
        ax.add_patch(FancyBboxPatch((x, top - hgt), w, hgt, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc=CARD, ec=BORDER, lw=1.2))
        ax.text(x + 0.15, top - 0.3, title, fontsize=14, fontweight="bold", color=RED, va="center")
        for i, (name, depth, mark) in enumerate(items):
            yy = top - 0.72 - i * 0.33
            defined = mark in ("≡", "⊒")
            ax.text(x + 0.2 + depth * 0.26, yy, ("└ " if depth else "") + name, fontsize=10.5, va="center",
                    color=RED if defined else (BLUE if mark == "R" else DARK),
                    fontweight="bold" if defined else "normal")
            if mark:
                ax.text(x + w - 0.1, yy, mark, fontsize=10.5, ha="right", va="center",
                        color=RED if defined else BLUE, fontweight="bold")
        x += w + 0.2
    ax.text(0.05, 0.12, "≡ defined class (necessary & sufficient)    ⊒ sufficient condition    R populated by a rule    "
            "Disjoint: Person ⊥ Place ⊥ Event ⊥ Work ⊥ Tenure · War ⊥ Battle · admin levels",
            fontsize=10, color=GREY)
    save(fig, "fig_hierarchy")


# ------------------------------------------------------------------ 3. inference example
def inference():
    fig, ax = plt.subplots(figsize=(13, 5.6))
    ax.set_xlim(0, 13)
    ax.set_ylim(-0.45, 5.6)
    ax.axis("off")
    H = 0.66
    WAR = "Chiến tranh Nguyên Mông\n– Đại Việt"
    N = {  # name: (x, y, w)
        "Trần Thái Tông": (1.3, 4.3, 2.1), "Trần Thánh Tông": (1.3, 2.6, 2.1), "Trần Nhân Tông": (1.3, 0.9, 2.1),
        "Trận Bạch Đằng (1288)": (4.3, 4.3, 2.3), "Kháng chiến lần 3": (7.4, 4.3, 2.0),
        WAR: (10.2, 4.3, 2.75),
        "Reign_0: Hoàng đế, 1278–1293": (4.3, 0.9, 3.3), "Nhà Trần": (8.7, 0.9, 1.4)}
    for name, (x, y, w) in N.items():
        hl = name == "Trần Nhân Tông"
        box(ax, x, y, w, H, name, fc=PINK if hl else CARD, ec=RED if hl else BORDER, fs=11 if len(name) > 20 else 12)

    def c(n, side, dx=0.0):
        x, y, w = N[n]
        return {"r": (x + w, y + H / 2), "l": (x, y + H / 2), "t": (x + w / 2 + dx, y + H),
                "b": (x + w / 2 + dx, y)}[side]

    def edge(a, sa, b, sb, label, inferred=False, rad=0.0, at=None, dxa=0.0, dxb=0.0, rot=0):
        col = RED if inferred else GREY
        p, q = c(a, sa, dxa), c(b, sb, dxb)
        arrow(ax, p, q, color=col, lw=2.2 if inferred else 1.6, ls="--" if inferred else "-", rad=rad)
        lx, ly = at if at else ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        ax.text(lx, ly, label, fontsize=10.5, color=col, ha="center", va="center", rotation=rot,
                fontweight="bold" if inferred else "normal", bbox=dict(fc="white", ec="none", pad=0.8))

    edge("Trần Nhân Tông", "t", "Trần Thánh Tông", "b", "hasFather")
    edge("Trần Thánh Tông", "t", "Trần Thái Tông", "b", "hasFather")
    edge("Trần Nhân Tông", "l", "Trần Thái Tông", "l", "hasPaternalGrandfather", True, rad=-0.55, at=(0.42, 2.93), rot=90)
    edge("Trần Nhân Tông", "r", "Reign_0: Hoàng đế, 1278–1293", "l", "hasReign", at=(3.85, 0.98))
    edge("Reign_0: Hoàng đế, 1278–1293", "r", "Nhà Trần", "l", "tenureDynasty")
    edge("Trần Nhân Tông", "b", "Nhà Trần", "b", "memberOfDynasty", True, rad=0.22, at=(6.2, -0.05))
    edge("Trận Bạch Đằng (1288)", "b", "Trần Nhân Tông", "r", "commander", dxa=-0.6, at=(4.2, 2.95))
    edge("Trận Bạch Đằng (1288)", "r", "Kháng chiến lần 3", "l", "partOf")
    edge("Kháng chiến lần 3", "r", WAR, "l", "partOf")
    edge("Trần Nhân Tông", "t", WAR, "b", "participatedIn", True, rad=0.18,
         dxa=0.75, dxb=0.3, at=(8.4, 2.75))
    # inferred types card
    ax.add_patch(FancyBboxPatch((10.2, 0.55), 2.75, 1.85, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=PINK, ec=RED, lw=1.2))
    ax.text(10.35, 2.15, "Inferred types", fontsize=11, color=DEEP, fontweight="bold", va="center")
    for i, t in enumerate(["VietnameseMonarch", "MonarchWarrior", "MilitaryCommander", "RoyalChild"]):
        ax.text(10.35, 1.8 - i * 0.33, "• " + t, fontsize=10.5, color=RED, fontweight="bold", va="center")
    ax.plot([6.9, 7.4], [5.4, 5.4], color=GREY, lw=1.6)
    ax.text(7.5, 5.4, "asserted (from infoboxes)", fontsize=10.5, color=GREY, va="center")
    ax.plot([10.4, 10.9], [5.4, 5.4], color=RED, lw=2.2, ls="--")
    ax.text(11.0, 5.4, "inferred", fontsize=10.5, color=RED, va="center", fontweight="bold")
    save(fig, "fig_inference")


# ------------------------------------------------------------------ 4. inferred triples by mechanism (paper)
def mechanism():
    m = FACTS["inferred_by_mechanism"]
    labels = {"transitive": "Transitive closure", "alignment": "Alignment (dbo/FOAF/schema)", "class": "Class membership",
              "chain": "Property chains", "rule": "SPARQL rules", "inverse_subproperty": "Inverse / sub-property"}
    items = sorted(m.items(), key=lambda kv: kv[1])
    fig, ax = plt.subplots(figsize=(7, 3.2))
    bars = ax.barh([labels[k] for k, _ in items], [v / 1000 for _, v in items],
                   color=[RED if k in ("chain", "class") else "#C9CED6" for k, _ in items])
    for b, (_, v) in zip(bars, items):
        ax.text(b.get_width() + 15, b.get_y() + b.get_height() / 2, f"{v / 1000:,.0f}k", va="center", fontsize=10, color=DARK)
    ax.set_xlabel("inferred triples (thousands)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, max(m.values()) / 1000 * 1.15)
    save(fig, "fig_mechanism")


# ------------------------------------------------------------------ 5. linking coverage (paper)
def coverage():
    data = [("Person", 58242, 21988), ("Admin. unit", 4173, 1452), ("Conflict", 4048, 2144),
            ("Monarch", 3981, 3358), ("Writer", 1442, 1002), ("State", 1963, 1732)]
    fig, ax = plt.subplots(figsize=(7, 3.0))
    names = [d[0] for d in data]
    pct = [100 * d[2] / d[1] for d in data]
    bars = ax.bar(names, pct, color=[RED if p > 60 else "#C9CED6" for p in pct])
    for b, p in zip(bars, pct):
        ax.text(b.get_x() + b.get_width() / 2, p + 2, f"{p:.0f}%", ha="center", fontsize=10, color=DARK)
    ax.set_ylabel("linked to DBpedia (%)")
    ax.set_ylim(0, 100)
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=15)
    save(fig, "fig_coverage")


if __name__ == "__main__":
    pipeline()
    hierarchy()
    inference()
    mechanism()
    coverage()
    print("figures:", sorted(p.name for p in PNG.glob("*.png")))
