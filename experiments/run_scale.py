"""Client-population scaling sweep: run CB-SAFE+ (hybrid) and FedGT (and mean as
the collapse reference) at N in {100, 500, 1000} on FashionMNIST under sign-flip,
to show accuracy/detection hold as N grows (cost scaling is in plot_scaling.py).

One CSV per (N, method): results/scale/robust_signflip_<agg><suf>_N<N>_f20_c3_s0.csv
Resumable (existing CSVs skipped). Run two workers with --reverse on the 2nd.
"""

import _bootstrap  # noqa: F401

import argparse
import csv
import os

import numpy as np
from torch.utils.data import DataLoader, Subset

from src.federated import data, models
from src.federated.simulation import Config, run

# (aggregator, overlap, needs_root) -- full roster for the scaling comparison
METHODS = [
    ("hybrid", 4, True), ("fedgt", 1, True),          # ours + closest peer
    ("mean", 1, False), ("trimmed", 1, False), ("median", 1, False),
    ("krum", 1, False), ("bulyan", 1, False), ("geomedian", 1, False),
    ("fltrust", 1, True),
]


def prep(ds, n_clients, seed, root_size=200):
    train, test = data.load_dataset(ds)
    parts = data.dirichlet_partition(np.array(train.targets), n_clients, 0.5, seed)
    rng = np.random.default_rng(seed + 99)
    root_idx = set(rng.choice(len(train), size=root_size, replace=False).tolist())
    parts = [np.array([i for i in p if i not in root_idx]) for p in parts]
    client_dls = data.client_loaders(train, parts, 64)
    server_dl = DataLoader(Subset(train, sorted(root_idx)), batch_size=64, shuffle=True)
    test_dl = DataLoader(test, batch_size=512)
    return client_dls, test_dl, server_dl


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ns", default="100,500,1000")
    p.add_argument("--methods", default="")   # empty = all in METHODS
    p.add_argument("--dataset", default="fmnist")
    p.add_argument("--attack", default="signflip")
    p.add_argument("--f", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--rounds", type=int, default=30)
    p.add_argument("--reverse", action="store_true")
    args = p.parse_args()

    ns = [int(x) for x in args.ns.split(",") if x.strip()]
    want = {m.strip() for m in args.methods.split(",") if m.strip()}
    odir = os.path.join(_bootstrap.RESULTS, "scale")
    os.makedirs(odir, exist_ok=True)

    jobs = [(N, agg, ov, nr) for N in ns for (agg, ov, nr) in METHODS
            if not want or agg in want]
    if args.reverse:
        jobs = list(reversed(jobs))

    prepared = {}
    for i, (N, agg, ov, needs_root) in enumerate(jobs):
        suf = f"_ov{ov}" if ov != 1 else ""
        name = f"robust_{args.attack}_{agg}{suf}_N{N}_f{int(args.f*100):02d}_c3_s{args.seed}.csv"
        path = os.path.join(odir, name)
        if os.path.exists(path):
            print(f"[{i+1}/{len(jobs)}] skip {name}", flush=True)
            continue
        if N not in prepared:
            prepared[N] = prep(args.dataset, N, args.seed)
        client_dls, test_dl, server_dl = prepared[N]
        cfg = Config(n_clients=N, rounds=args.rounds, aggregation="cluster", aggregator=agg,
                     cluster_size=3, attack=args.attack, f_malicious=args.f, seed=args.seed,
                     dataset=args.dataset, overlap=ov, n_classes=models.n_classes_of(args.dataset))
        print(f"[{i+1}/{len(jobs)}] run {name}", flush=True)
        hist = run(cfg, client_dls, test_dl, server_dl=(server_dl if needs_root else None))
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(hist[0]))
            w.writeheader(); w.writerows(hist)
    print("SCALE SWEEP COMPLETE", flush=True)


if __name__ == "__main__":
    main()
