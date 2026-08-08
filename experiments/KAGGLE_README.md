# CB-SAFE on Kaggle — full baseline comparison, one bundle

Runs **every method on every dataset** in one place, resumable. Methods (all our
own faithful implementations of the published algorithms, each cited in the paper —
run under ONE shared harness for a controlled comparison):

- **Baselines:** FedAvg mean, trimmed mean, median, Multi-Krum [NeurIPS'17],
  Bulyan [ICML'18], geometric-median / RFA, FLTrust [NDSS'21], FedGT [TIFS'25].
- **Ours:** CB-SAFE+ (reputation), CB-SAFE+ ov4, trust-free, hybrid (temporal
  group testing).

Datasets: **CIFAR-10, FashionMNIST, EMNIST** (auto-downloaded by torchvision) and
**Edge-IIoTset** (add the Kaggle dataset — see below). Attacks: sign-flip (3 seeds),
label-flip and backdoor (1 seed).

---

## Steps

1. **Upload this zip as a Kaggle Dataset** (New Dataset → upload → Create).
2. **Add the Edge-IIoTset dataset:** *Add Data* → search **"Edge-IIoTset"** → add the
   one containing `DNN-EdgeIIoT-dataset.csv`. (Skip if you only want the 3 image
   datasets — the runner detects it's missing and moves on.)
3. **Settings → Accelerator = GPU T4 x2**, Internet = **On**.
   *(Use T4, NOT P100 — Kaggle's current PyTorch has no P100 kernels.)*
4. **Run one cell:**
   ```python
   import glob, subprocess, sys
   run = glob.glob('/kaggle/input/**/run_all_kaggle.py', recursive=True)[0]
   subprocess.run([sys.executable, run], check=True)
   ```
5. **Download results** when it prints `ALL-KAGGLE COMPLETE` (or when the session is
   about to hit 12h):
   ```python
   import shutil; shutil.make_archive('/kaggle/working/cbsafe_results', 'zip',
                                       '/kaggle/working/results')
   ```
   Download `cbsafe_results.zip` and send it back.

---

## Important notes

- **Resumable.** Every finished run is one CSV and is skipped on re-run. The full
  grid is hundreds of GPU-runs and will **not** finish in a single 12h Kaggle
  session — just re-run the cell in a new session and it continues. 2–3 sessions
  cover everything.
- **Quick first pass** (validate before committing hours):
  ```python
  import glob, subprocess, sys, os
  run = glob.glob('/kaggle/input/**/run_all_kaggle.py', recursive=True)[0]
  # edit inside the file is not needed; to limit, set env and it still runs all —
  # simplest: just run; the headline sign-flip cells are written first per dataset.
  subprocess.run([sys.executable, run], check=True)
  ```
- **GPU compatibility:** if you ever see `no kernel image is available` that's the
  P100 again — switch the accelerator to **T4** and restart.
- **CPU fallback** (if no GPU): prepend `CUDA_VISIBLE_DEVICES=""` — fine for
  Edge-IIoTset (tabular), slow for the image sets.
- No liboqs / crypto build needed — this is pure PyTorch (masking correctness is
  proven separately and is dataset-independent).
