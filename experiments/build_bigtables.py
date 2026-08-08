"""Four wide, full-width (table*) manuscript tables packed with real metrics.
Emits LaTeX booktabs to results/tables/*.tex and prints markdown previews."""

import _bootstrap  # noqa: F401

import glob
import os
import re
import collections

import numpy as np
import pandas as pd

R = _bootstrap.RESULTS
TBL = os.path.join(R, "tables")
os.makedirs(TBL, exist_ok=True)
DSROOT = {"CIFAR-10": "", "FashionMNIST": "fmnist",
          "EMNIST": "kaggle/emnist", "Edge-IIoTset": "kaggle/edgeiiot"}
FS = [0.1, 0.2, 0.3]


def runs(dsdir, agg, attack, f):
    root = os.path.join(R, dsdir) if dsdir else R
    out = []
    for p in glob.glob(os.path.join(root, f"robust_{attack}_{agg}_f{int(f*100):02d}_c3_s*.csv")):
        core = re.sub(r"_f\d+_c3_s\d+\.csv$", "", os.path.basename(p)).replace(f"robust_{attack}_", "")
        if core == agg:
            out.append(p)
    return out


def val(paths, asr=False):
    vs = []
    for p in paths:
        d = pd.read_csv(p).tail(5)
        col = "asr" if asr else "acc"
        if col in d.columns:
            vs.append(d[col].mean() * 100)
    if not vs:
        return None
    return (np.mean(vs), np.std(vs), len(vs))


def fmt(v, bold=False):
    if v is None:
        return "--"
    m, s, n = v
    txt = f"{m:.1f}\\,{{\\scriptsize$\\pm${s:.1f}}}" if n > 1 else f"{m:.1f}"
    return f"\\textbf{{{txt}}}" if bold else txt


def ident(dsdir, agg, f):
    root = os.path.join(R, dsdir) if dsdir else R
    tp, fp, nm = [], [], []
    for p in runs(dsdir, agg, "signflip", f):
        d = pd.read_csv(p).iloc[-1]
        if "excluded_malicious" in d:
            tp.append(d["excluded_malicious"]); fp.append(d["excluded_honest"]); nm.append(d["n_malicious"])
    if not tp:
        return "--"
    return f"{np.mean(tp):.0f}/{np.mean(nm):.0f}"


def identfp(dsdir, agg, f):
    root = os.path.join(R, dsdir) if dsdir else R
    fp = []
    for p in runs(dsdir, agg, "signflip", f):
        d = pd.read_csv(p).iloc[-1]
        if "excluded_honest" in d:
            fp.append(d["excluded_honest"])
    return f"{np.mean(fp):.1f}" if fp else "--"


# ============ TABLE I: sign-flip robustness, all datasets x f x methods ============
methods1 = [("mean", "FedAvg (mean)"), ("trimmed", "Trimmed mean"), ("median", "Median"),
            ("krum", "Multi-Krum"), ("reputation", "CB-SAFE+ (ours)"), ("hybrid_ov4", "CB-SAFE+ hybrid (ours)")]
L = [r"\begin{table*}[t]\centering\footnotesize",
     r"\caption{Test accuracy (\%) under the sign-flip (laundering) attack across four datasets and malicious fractions $f$ (mean\,$\pm$\,std over 3 seeds for CIFAR-10/FashionMNIST; single seed for EMNIST/Edge-IIoTset). Higher is better; best per column in bold.}",
     r"\label{tab:signflip}", r"\setlength{\tabcolsep}{4pt}",
     r"\begin{tabular}{@{}l" + "ccc" * 4 + r"@{}}\toprule",
     r"& \multicolumn{3}{c}{CIFAR-10} & \multicolumn{3}{c}{FashionMNIST} & \multicolumn{3}{c}{EMNIST} & \multicolumn{3}{c}{Edge-IIoTset}\\",
     r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}\cmidrule(lr){8-10}\cmidrule(l){11-13}",
     r"Method & " + " & ".join([f"$f{{=}}.{int(f*10)}$" for _ in DSROOT for f in FS]) + r"\\\midrule"]
prev = ["METHOD".ljust(22) + "".join(f"{ds[:8]:>26}" for ds in DSROOT)]
# precompute best per (ds,f)
best = {}
for ds, dsdir in DSROOT.items():
    for f in FS:
        vals = {a: val(runs(dsdir, a, "signflip", f)) for a, _ in methods1}
        best[(ds, f)] = max((v[0], a) for a, v in vals.items() if v)[1] if any(vals.values()) else None
for agg, label in methods1:
    cells = []
    pcells = []
    for ds, dsdir in DSROOT.items():
        for f in FS:
            v = val(runs(dsdir, agg, "signflip", f))
            cells.append(fmt(v, bold=(best.get((ds, f)) == agg)))
            pcells.append(f"{v[0]:.0f}" if v else "--")
    L.append(f"{label} & " + " & ".join(cells) + r"\\")
    prev.append(label.ljust(22) + "".join(f"{c:>9}" for c in pcells))
L += [r"\bottomrule\end{tabular}\end{table*}"]
open(os.path.join(TBL, "table1_signflip.tex"), "w").write("\n".join(L))
print("=== TABLE I: sign-flip robustness (preview, acc%) ===")
print("\n".join(prev))

# ============ TABLE II: FedGT head-to-head + identification + cost (CIFAR + FMNIST) ============
methods2 = [("fedgt", "FedGT [TIFS'25]"), ("reputation", "CB-SAFE+ ov1"),
            ("reputation_ov4", "CB-SAFE+ ov4"), ("reputation_tf", "CB-SAFE+ trust-free"),
            ("hybrid_ov4", "CB-SAFE+ hybrid")]
cost = {"fedgt": "40", "reputation": "10", "reputation_ov4": "40",
        "reputation_tf": "10", "hybrid_ov4": "40"}
rootfree = {"fedgt": "no", "reputation": "no", "reputation_ov4": "no",
            "reputation_tf": "\\textbf{yes}", "hybrid_ov4": "no"}
print("\n=== TABLE II: FedGT head-to-head (CIFAR acc | FMNIST acc | ident caught | FP | cost | root-free) ===")
print("METHOD".ljust(22) + "cifar f.1/.2/.3    fmnist f.1/.2/.3    caught(cifar)   FP        ops  rootfree")
for agg, label in methods2:
    ca = " ".join(f"{(val(runs('',agg,'signflip',f)) or (0,0,0))[0]:.0f}" if val(runs('',agg,'signflip',f)) else "--" for f in FS)
    fa = " ".join(f"{(val(runs('fmnist',agg,'signflip',f)) or (0,0,0))[0]:.0f}" if val(runs('fmnist',agg,'signflip',f)) else "--" for f in FS)
    cg = " ".join(ident('', agg, f) for f in FS)
    fp = " ".join(identfp('', agg, f) for f in FS)
    print(f"{label:22}{ca:12}   {fa:12}   {cg:14}{fp:10}{cost[agg]:5}{rootfree[agg]}")

# ============ TABLE III: crypto + overhead ============
k = pd.read_csv(os.path.join(R, "crypto_kem_bench.csv")).set_index("name")
o = pd.read_csv(os.path.join(R, "overhead.csv"))
o = o[o.cluster_size == 3].set_index("kem")
print("\n=== TABLE III: crypto primitives + per-client overhead (c=3) ===")
print("KEM         fam    lvl   pk    ct   setupUp setupDn wall_s  roundKiB mask_ms unmask_s")
order = ["hqc-128", "hqc-192", "hqc-256", "mlkem-512", "mlkem-768", "mlkem-1024"]
for kem in order:
    kr = k.loc[kem]; orr = o.loc[kem]
    print(f"{kem:11} {kr['family'][:4]:5} {kr['claimed_nist_level']:>3}  {kr['public_key_bytes']:>5} {kr['ciphertext_bytes']:>5}"
          f"  {orr['setup_up_B']:>6} {orr['setup_down_B']:>6} {orr['setup_wall_s']:>6.2f}  {(orr['round_up_B']+orr['round_down_B'])/1024:>7.0f}"
          f"  {orr['round_client_mask_s']*1000:>5.0f}  {orr['round_server_unmask_s']:>6.2f}")

# ============ TABLE IV: backdoor ASR + label-flip acc ============
print("\n=== TABLE IV: backdoor ASR (lower better) + label-flip acc, by dataset/method/f ===")
print("dataset   method       BD-ASR f.1/.2/.3     LF-acc f.1/.2/.3")
for ds, dsdir in DSROOT.items():
    for agg, label in [("mean", "mean"), ("median", "median"), ("krum", "Krum"), ("reputation", "CB-SAFE+")]:
        bd = " ".join(f"{v[0]:.0f}" if (v:=val(runs(dsdir,agg,'backdoor',f),asr=True)) else "--" for f in FS)
        lf = " ".join(f"{v[0]:.0f}" if (v:=val(runs(dsdir,agg,'labelflip',f))) else "--" for f in FS)
        if bd.strip("- ") or lf.strip("- "):
            print(f"{ds[:9]:9} {label:12} {bd:18} {lf}")

print("\nwrote LaTeX table1_signflip.tex (+ others buildable); table*/full-width, packed.")
