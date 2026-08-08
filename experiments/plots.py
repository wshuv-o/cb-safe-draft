"""Paper figures from results CSVs (IEEE single-column PDFs).

Follows the dataviz method: one axis per chart, categorical hues in fixed slot
order (never cycled), direct labels where series <= 4, thin marks, recessive
grid/axis chrome, values labeled where contrast is low.
"""

import _bootstrap  # noqa: F401

import glob
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

R = _bootstrap.RESULTS
FIGS = os.path.join(R, "figs")
os.makedirs(FIGS, exist_ok=True)

# Reference categorical palette (validated, fixed slot order)
C = {
    "blue": "#2a78d6", "aqua": "#1baf7a", "yellow": "#eda100", "green": "#008300",
    "violet": "#4a3aa7", "red": "#e34948",
    "ink": "#0b0b0b", "ink2": "#52514e", "muted": "#898781",
    "grid": "#e1e0d9", "axis": "#c3c2b7", "surface": "#fcfcfb",
}
C["black"] = "#0b0b0b"
C["magenta"] = "#b0228c"
AGG_COLOR = {"mean": C["blue"], "trimmed": C["aqua"], "median": C["yellow"],
             "krum": C["green"], "bulyan": C["red"], "geomedian": C["violet"],
             "fedgt": C["black"], "reputation": C["violet"], "hybrid_ov4": C["magenta"]}
AGG_LABEL = {"mean": "Mean (no robustness)", "trimmed": "Trimmed mean",
             "median": "Median", "krum": "Multi-Krum", "bulyan": "Bulyan",
             "geomedian": "Geo-median/RFA", "fedgt": "FedGT [TIFS'25]",
             "reputation": "CB-SAFE+ (ours)", "hybrid_ov4": "CB-SAFE+ hybrid (ours)"}
# per-(attack,metric) series order; only methods with complete data are drawn
ACC_METHODS = ["mean", "trimmed", "median", "krum", "bulyan", "geomedian",
               "fedgt", "hybrid_ov4"]
ASR_METHODS = ["mean", "trimmed", "median", "krum", "reputation"]

plt.rcParams.update({
    "font.size": 8, "font.family": "sans-serif",
    "axes.edgecolor": C["axis"], "axes.labelcolor": C["ink2"],
    "xtick.color": C["muted"], "ytick.color": C["muted"],
    "axes.grid": True, "grid.color": C["grid"], "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": C["surface"],
    "savefig.bbox": "tight", "savefig.dpi": 300,
})

FIG_W = 3.45  # IEEE column width in inches


def fig_utility() -> None:
    upath = os.path.join(R, "utility_acc.csv")
    if not os.path.exists(upath):
        return
    acc = pd.read_csv(upath)
    fig, ax = plt.subplots(figsize=(FIG_W, 2.2))
    ax.plot(acc["round"] + 1, acc["acc"] * 100, color=C["blue"], lw=2)
    eq = os.path.join(R, "secure_equivalence.csv")
    if os.path.exists(eq):
        e = pd.read_csv(eq)
        ax.set_title(
            f"FedAvg on CIFAR-10 (30 clients, Dirichlet $\\alpha$=0.5) — CB-SAFE secure\n"
            f"aggregates (HQC & ML-KEM) match to $\\leq${e['max_abs_err'].max():.0e} per coord.",
            fontsize=7.5, color=C["ink"], loc="left")
    ax.set_xlabel("Round")
    ax.set_ylabel("Test accuracy (%)")
    fig.savefig(os.path.join(FIGS, "fig_utility.pdf"))
    plt.close(fig)


def fig_amortization() -> None:
    """Dot plot, log x: one-time setup traffic per KEM vs ONE round of masked
    updates. The point is that even HQC-256's setup is a fraction of a single
    round, so the code-based premium amortizes to noise."""
    opath = os.path.join(R, "overhead.csv")
    if not os.path.exists(opath):
        return
    df = pd.read_csv(opath)
    df = df[df.cluster_size == 3].set_index("kem")
    order = ["mlkem-512", "hqc-128", "mlkem-768", "hqc-192", "mlkem-1024", "hqc-256"]
    names = {"mlkem-512": "ML-KEM-512", "hqc-128": "HQC-128", "mlkem-768": "ML-KEM-768",
             "hqc-192": "HQC-192", "mlkem-1024": "ML-KEM-1024", "hqc-256": "HQC-256"}
    fig, ax = plt.subplots(figsize=(FIG_W, 2.4))
    one_round = (df["round_up_B"].iloc[0] + df["round_down_B"].iloc[0]) / 1024
    for yi, kem in enumerate(order):
        row = df.loc[kem]
        kib = (row.setup_up_B + row.setup_down_B) / 1024
        color = C["blue"] if kem.startswith("hqc") else C["aqua"]
        ax.plot([kib], [yi], "o", ms=6, color=color)
        ax.hlines(yi, 0.9, kib, color=color, lw=1, alpha=0.35)
        ax.annotate(f"{kib:,.1f} KiB", (kib, yi), textcoords="offset points",
                    xytext=(6, -2.5), fontsize=6.5, color=C["ink2"])
    ax.axvline(one_round, color=C["muted"], lw=1, ls=(0, (4, 3)))
    ax.annotate(f"one round of masked updates\n({one_round:,.0f} KiB, identical for all KEMs)",
                (one_round, 0.35), fontsize=6.5, color=C["muted"], ha="right",
                textcoords="offset points", xytext=(-6, 0))
    ax.set_yticks(range(len(order)), [names[k] for k in order], fontsize=7)
    ax.set_xscale("log")
    ax.set_xlim(0.9, one_round * 4)
    ax.set_title("One-time setup traffic per client (N=30, c=3) vs a single\n"
                 "round: the code-based premium is a setup-only cost",
                 fontsize=7.5, color=C["ink"], loc="left")
    ax.set_xlabel("Traffic per client (KiB, log scale)")
    ax.grid(axis="y", visible=False)
    fig.savefig(os.path.join(FIGS, "fig_amortization.pdf"))
    plt.close(fig)


def _robust_runs() -> pd.DataFrame:
    rows = []
    for path in glob.glob(os.path.join(R, "robust_*.csv")):
        m = re.match(r"robust_(signflip|labelflip|backdoor|none)_(.+)_f(\d+)_c(\d+)_s(\d+)\.csv",
                     os.path.basename(path))
        if not m:
            continue
        if int(m[4]) != 3:  # c != 3 belongs to the c-dial figure, not these
            continue
        df = pd.read_csv(path).tail(5)
        rows.append({"attack": m[1], "agg": m[2], "f": int(m[3]) / 100,
                     "acc": df["acc"].mean() * 100,
                     "asr": df["asr"].mean() * 100 if "asr" in df.columns else np.nan})
    return pd.DataFrame(rows)


def fig_robustness() -> None:
    data = _robust_runs()
    if data.empty:
        return
    base = None
    upath = os.path.join(R, "utility_acc.csv")
    if os.path.exists(upath):
        base = pd.read_csv(upath).tail(5)["acc"].mean() * 100
    for attack in data["attack"].unique():
        for metric, ylabel, suffix in [("acc", "Test accuracy (%)", "acc"),
                                       ("asr", "Attack success rate (%)", "asr")]:
            sub = data[(data.attack == attack) & data[metric].notna()]
            if sub.empty:
                continue
            # average over seeds: one point per (agg, f)
            sub = sub.groupby(["agg", "f"], as_index=False)[metric].mean()
            fig, ax = plt.subplots(figsize=(FIG_W, 2.3))
            methods = ACC_METHODS if metric == "acc" else ASR_METHODS
            for agg in methods:
                s = sub[sub["agg"] == agg].sort_values("f")
                if len(s) < 3:  # only draw methods with a complete f-sweep
                    continue
                ax.plot(s["f"] * 100, s[metric], color=AGG_COLOR[agg], lw=2,
                        marker="o", ms=4, label=AGG_LABEL[agg])
            ax.legend(fontsize=5.5, frameon=False, loc="best", ncol=2)
            if metric == "acc" and base is not None:
                ax.axhline(base, color=C["muted"], lw=1, ls=(0, (4, 3)))
                ax.annotate("no-attack baseline", (2, base), textcoords="offset points",
                            xytext=(0, 4), fontsize=6.5, color=C["muted"])
            ax.set_title(f"CIFAR-10 {attack} attack: robust rules across k=10 cluster sums (c=3)",
                         fontsize=7.5, color=C["ink"], loc="left")
            ax.set_xlabel("Malicious fraction f (%)")
            ax.set_ylabel(ylabel)
            ax.set_xlim(left=0)
            fig.savefig(os.path.join(FIGS, f"fig_{attack}_{suffix}.pdf"))
            plt.close(fig)


def fig_tradeoff() -> None:
    """Clean-cluster probability (1-f)^c: the privacy-robustness tension curve."""
    f = np.linspace(0, 0.4, 200)
    fig, ax = plt.subplots(figsize=(FIG_W, 2.3))
    for c, color in [(1, C["muted"]), (3, C["blue"]), (5, C["aqua"]), (10, C["yellow"])]:
        ax.plot(f * 100, (1 - f) ** c * 100, lw=2, color=color)
        ax.annotate(f"c={c}" + (" (no privacy)" if c == 1 else ""),
                    (f[-1] * 100, ((1 - f[-1]) ** c) * 100),
                    textcoords="offset points", xytext=(4, 0), fontsize=6.5,
                    color=color, va="center")
    ax.set_title("Privacy–robustness tension: larger anonymity sets (c)\n"
                 "leave fewer clean cluster sums for the robust rule",
                 fontsize=7.5, color=C["ink"], loc="left")
    ax.set_xlabel("Malicious fraction f (%)")
    ax.set_ylabel("P(cluster sum clean) (%)")
    ax.set_xlim(0, 46)
    fig.savefig(os.path.join(FIGS, "fig_tradeoff.pdf"))
    plt.close(fig)


def fig_cdial() -> None:
    """Empirical privacy-robustness dial: median-rule accuracy vs f for c in
    {1,3,5} under sign-flip. The breakdown frontier shifts left as c grows,
    tracking (1-f)^c."""
    rows = []
    for path in glob.glob(os.path.join(R, "robust_signflip_median_f*_c*_s0.csv")):
        m = re.match(r"robust_signflip_median_f(\d+)_c(\d+)_s0\.csv", os.path.basename(path))
        if not m:
            continue
        tail = pd.read_csv(path).tail(5)
        rows.append({"f": int(m[1]) / 100, "c": int(m[2]), "acc": tail["acc"].mean() * 100})
    if not rows:
        return
    data = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(FIG_W, 2.4))
    upath = os.path.join(R, "utility_acc.csv")
    if os.path.exists(upath):
        base = pd.read_csv(upath).tail(5)["acc"].mean() * 100
        ax.axhline(base, color=C["muted"], lw=1, ls=(0, (4, 3)))
        ax.annotate("no-attack baseline", (6, base), textcoords="offset points",
                    xytext=(0, 3), fontsize=6.5, color=C["muted"])
    for c, color, label in [(1, C["muted"], "c=1 (no privacy)"),
                            (3, C["blue"], "c=3"), (5, C["aqua"], "c=5")]:
        s = data[data["c"] == c].sort_values("f")
        if s.empty:
            continue
        ax.plot(s["f"] * 100, s["acc"], color=color, lw=2, marker="o", ms=4, label=label)
    ax.legend(fontsize=6.5, frameon=False, loc="upper right")
    ax.set_title("The privacy dial, measured: median rule under sign-flip.\n"
                 "Larger anonymity sets move the breakdown frontier left",
                 fontsize=7.5, color=C["ink"], loc="left")
    ax.set_xlabel("Malicious fraction f (%)")
    ax.set_ylabel("Test accuracy (%)")
    ax.set_xlim(left=0)
    fig.savefig(os.path.join(FIGS, "fig_cdial.pdf"))
    plt.close(fig)


if __name__ == "__main__":
    fig_utility()
    fig_amortization()
    fig_robustness()
    fig_tradeoff()
    print("figures written to", FIGS)
