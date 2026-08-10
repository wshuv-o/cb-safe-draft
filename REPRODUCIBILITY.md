# Reproducibility guide — CB-SAFE

Everything needed to reproduce every table and figure in the paper. All runs are
seeded (numpy + torch + CUDA are fixed in `src/federated/simulation.py`), so a
given `(dataset, attack, method, f, seed)` reproduces bit-for-bit on the same
hardware/driver stack.

---

## 1. Environment

| Component | Value |
|---|---|
| OS (runs of record) | Windows 11, single NVIDIA RTX 2060 (6 GB) |
| Python | 3.12 |
| Key packages | torch 2.5.0 (cu124), torchvision 0.20.0, numpy 2.2.4, pandas 2.2.3, scikit-learn 1.6.1, matplotlib 3.10.0 |
| PQC | liboqs 0.15.0 + liboqs-python 0.15.0 (HQC enabled) |

```bash
pip install -r requirements.txt          # pinned versions
# liboqs native library: see SETUP.md (Windows: clang+ninja from source, HQC on)
```

Two environment variables are required on the run-of-record machine:

```bash
export OQS_INSTALL_PATH=~/_oqs           # where liboqs.dll/so was installed (see SETUP.md)
export KMP_DUPLICATE_LIB_OK=TRUE         # tolerate duplicate OpenMP runtime on this box
```

Optional overrides honored by the runners: `CBSAFE_DATA_ROOT` (dataset cache),
`CBSAFE_OUT` (results dir), and on Kaggle `CBSAFE_DATASETS / CBSAFE_ATTACKS /
CBSAFE_ROUNDS`.

---

## 2. Datasets and partitioning

| Dataset | Classes | Model | Source |
|---|---|---|---|
| CIFAR-10 | 10 | small CNN | torchvision |
| FashionMNIST | 10 | small CNN (1 channel) | torchvision |
| EMNIST-balanced | 47 | small CNN (1 channel) | torchvision / Kaggle mirror |
| Edge-IIoTset | 15 | MLP | Kaggle |

Non-IID split: **Dirichlet(α = 0.5)** over `n_clients`, seeded by the run seed
(`src/federated/data.py::dirichlet_partition`). The server root set (for the
loss probe / FLTrust / FedGT) is `root_size = 200` samples drawn disjoint from
the client partitions. Model definitions: `src/federated/models.py`.

---

## 3. Hyperparameters (ground truth: `Config` in `src/federated/simulation.py`)

| Parameter | Value |
|---|---|
| clients `n_clients` | 30 (main); 100/500/1000 (scaling study) |
| communication rounds | 30 |
| local epochs | 1 |
| optimizer | SGD, lr = 0.01, momentum = 0.9 |
| batch size | 64 |
| Dirichlet α | 0.5 |
| cluster size `c` | 3 |
| server root size | 200 |
| overlap `o` | 1 (reputation) · 4 (hybrid / `ov4`) |
| sign-flip amplification γ | 5.0 (= γ\* for c=3, m=1) |
| seeds | sign-flip: 0,1,2 (CIFAR/FMNIST/Edge, and CB-SAFE+/FedGT on EMNIST); label-flip: 0 (all), plus 0,1,2 for CB-SAFE+/FedGT on EMNIST |

**CB-SAFE+ detector** (`src/aggregation/reputation.py`): warmup `W = 5`,
adaptive gap exclusion (`min_gap = 0.20`, `min_floor = 0.35`), probe margin
`0.25`. **Scale-adaptive rules activate only for `n_clients > 50`** (so N=30
results are identical to the base rules): robust median+MAD thresholds with
`PROBE_K_MAD = 1.0`, `EXCL_K_MAD = 2.5`.

KEMs benchmarked: HQC-128/192/256 and ML-KEM-512/768/1024 (`src/crypto/`).

---

## 4. Reproduce each result

Runs write one CSV per `(dataset, attack, method, f, seed)`; all runners are
resumable (existing CSVs are skipped). Prefix every command with the two env
vars from §1.

### 4.1 Robustness / accuracy CSVs
```bash
# CIFAR-10 + FashionMNIST, all attacks, sign-flip 3 seeds (2 workers: add --reverse to the 2nd)
python experiments/run_local_fill.py --datasets cifar10,fmnist --attacks signflip,labelflip,backdoor
# EMNIST (local): sign-flip + label-flip
python experiments/run_local_fill.py --datasets emnist --attacks signflip,labelflip
# Edge-IIoTset + any Kaggle-side runs (env-scoped)
CBSAFE_DATASETS=edgeiiot python experiments/run_all_kaggle.py
```

### 4.2 Client-population scaling (N ∈ {100,500,1000}), full roster
```bash
python experiments/run_scale.py --ns 100,500,1000 --dataset fmnist --attack signflip --f 0.2
# 2 workers: run the same command again with --reverse
```

### 4.3 Crypto / communication overhead
```bash
python experiments/run_overhead.py         # -> results/overhead.csv, results/crypto_kem_bench.csv
```

### 4.4 Tables (LaTeX, from the CSVs above)
```bash
python experiments/build_bigtables.py
#   -> results/tables/table1_signflip.tex   (Table V, sign-flip accuracy)
#   -> results/tables/table3_labelflip.tex  (Table VI, label-flip accuracy)
#   -> results/tables/table2_ablation.tex   (Table VII, CB-SAFE+ ablation)
#   + prints the overhead + detection (P_MD/P_FA) previews
```

### 4.5 Figures
```bash
python experiments/plot_dirichlet.py   # Non-IID partition (Fig.)
python experiments/plots.py            # utility, sign-flip acc, backdoor ASR, c-dial
python experiments/plot_dynamics.py    # training dynamics (3x3)
python experiments/plot_suspicion.py   # temporal suspicion separation
python experiments/plot_scaling.py     # cost-vs-N (per-client cost, log-log)
```

### 4.6 Paper
```bash
cd paper && latexmk -pdf cbsafe.tex     # inline bibliography; two passes
```

---

## 5. Result → artifact map

| Paper item | Script | Output |
|---|---|---|
| Table V (sign-flip) | run_local_fill / run_all_kaggle → build_bigtables | table1_signflip.tex |
| Table VI (label-flip) | same → build_bigtables | table3_labelflip.tex |
| Table VII (ablation) | same → build_bigtables | table2_ablation.tex |
| Table II (overhead) | run_overhead → build_bigtables | overhead.csv |
| Fig. cost-vs-N | plot_scaling | fig_scaling_cost.pdf |
| Fig. training dynamics | plot_dynamics | fig_dynamics_signflip.pdf |
| Fig. suspicion | plot_suspicion | fig_suspicion.pdf |
| Fig. non-IID partition | plot_dirichlet | fig_dirichlet.pdf |
| Architecture (Fig. 1) | `cbsafe.drawio` (draw.io source) | fig_architecture.pdf |

---

## 6. Notes on determinism

`simulation.py::run` calls `np.random.seed(seed)`, `torch.manual_seed(seed)`,
`torch.cuda.manual_seed_all(seed)` at the start of every run; data partitions and
malicious selection use seeded `np.random.default_rng`. Results are deterministic
per seed on a fixed CUDA/driver stack; tiny cross-hardware differences in
floating-point reductions are possible but do not change the reported trends.
