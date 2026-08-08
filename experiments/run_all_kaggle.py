"""One-shot Kaggle runner: every method x every dataset x every attack, resumable.
Upload the bundle as a Kaggle dataset, add the Edge-IIoTset dataset, enable a T4
GPU + Internet, and run this. It writes one CSV per (dataset, attack, method, f,
seed) under /kaggle/working/results/. Re-run to continue where a 12h session left
off (finished CSVs are skipped).

Methods compared (all under the SAME harness = controlled comparison):
  baselines:  mean, trimmed mean, median, Multi-Krum, Bulyan (ICML'18),
              geometric-median/RFA, FLTrust (NDSS'21), FedGT (TIFS'25)
  ours:       CB-SAFE+ (reputation), CB-SAFE+ ov4, trust-free, hybrid
Each is our own faithful implementation of the published algorithm (cited).
"""

import _bootstrap  # noqa: F401

import csv
import os

import numpy as np
from torch.utils.data import DataLoader, Subset

from src.federated import data, models
from src.federated import kaggle_datasets as kd
from src.federated.data import dirichlet_partition
from src.federated.simulation import Config, run

OUT = os.environ.get("CBSAFE_OUT", "/kaggle/working/results")
DATASETS = ["cifar10", "fmnist", "emnist", "edgeiiot"]
# (aggregator, overlap, needs_root)
METHODS = [
    ("mean", 1, False), ("trimmed", 1, False), ("median", 1, False), ("krum", 1, False),
    ("bulyan", 1, False), ("geomedian", 1, False), ("fltrust", 1, True), ("fedgt", 1, True),
    ("reputation", 1, True), ("reputation", 4, True), ("reputation_tf", 1, False),
    ("hybrid", 4, True),
]
FS = [0.1, 0.2, 0.3]
SF_SEEDS = [0, 1, 2]       # sign-flip: 3 seeds (headline)
OTHER_SEEDS = [0]          # backdoor/label-flip: 1 seed (bound runtime; footnoted)
ROUNDS = 25


def subdir(ds):
    return {"cifar10": "", "fmnist": "fmnist", "emnist": os.path.join("kaggle", "emnist"),
            "edgeiiot": os.path.join("kaggle", "edgeiiot")}[ds]


def load(ds, seed):
    if ds == "edgeiiot":
        csv = kd.find_edgeiiot_csv()
        if not csv:
            return None
        tr, te, lab = kd.load_edgeiiot(csv, seed=seed)
        return tr, te, lab, 128
    tr, te = data.load_dataset(ds)
    return tr, te, np.array(tr.targets), 64


def prep(ds, seed, root_size=200):
    got = load(ds, seed)
    if got is None:
        return None
    tr, te, lab, batch = got
    parts = dirichlet_partition(lab, 30, alpha=0.5, seed=seed)
    rng = np.random.default_rng(seed + 99)
    allidx = np.concatenate(parts)
    root = set(rng.choice(allidx, size=min(root_size, len(allidx) // 4), replace=False).tolist())
    parts = [np.array([i for i in p if i not in root]) for p in parts]
    cdl = [DataLoader(Subset(tr, ix.tolist()), batch_size=batch, shuffle=True) for ix in parts]
    sdl = DataLoader(Subset(tr, sorted(root)), batch_size=64, shuffle=True)
    tdl = DataLoader(te, batch_size=512)
    return cdl, tdl, sdl


def main():
    os.makedirs(OUT, exist_ok=True)
    total = done = 0
    for ds in DATASETS:
        attacks = ["signflip", "labelflip"] + (["backdoor"] if ds != "edgeiiot" else [])
        odir = os.path.join(OUT, subdir(ds))
        os.makedirs(odir, exist_ok=True)
        prepared = {}
        for attack in attacks:
            seeds = SF_SEEDS if attack == "signflip" else OTHER_SEEDS
            for agg, ov, needs_root in METHODS:
                if attack != "signflip" and agg in ("reputation_tf", "hybrid", "fedgt") and ov == 1:
                    pass  # keep detection methods on non-signflip too
                for f in FS:
                    for s in seeds:
                        suf = f"_ov{ov}" if ov != 1 else ""
                        name = f"robust_{attack}_{agg}{suf}_f{int(f*100):02d}_c3_s{s}.csv"
                        path = os.path.join(odir, name)
                        total += 1
                        if os.path.exists(path):
                            done += 1
                            continue
                        if (ds, s) not in prepared:
                            got = prep(ds, s)
                            if got is None:
                                print(f"[skip dataset] {ds}: data not found", flush=True)
                                break
                            prepared[(ds, s)] = got
                        cdl, tdl, sdl = prepared[(ds, s)]
                        cfg = Config(n_clients=30, rounds=ROUNDS, aggregation="cluster",
                                     aggregator=agg, cluster_size=3, attack=attack,
                                     f_malicious=f, seed=s, dataset=ds, overlap=ov,
                                     n_classes=models.n_classes_of(ds))
                        print(f"[run] {ds}/{name}", flush=True)
                        hist = run(cfg, cdl, tdl, server_dl=(sdl if needs_root else None))
                        with open(path, "w", newline="") as fh:
                            w = csv.DictWriter(fh, fieldnames=list(hist[0]))
                            w.writeheader(); w.writerows(hist)
                        done += 1
    print(f"ALL-KAGGLE COMPLETE ({done} present of {total} planned)", flush=True)


if __name__ == "__main__":
    main()
