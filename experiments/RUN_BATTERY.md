# Running the revision experiment battery (5080 box)

The battery is the set of reviewer-requested runs that the existing driver can
produce today: **clean f=0 rows**, the **cluster-size dial re-run at 50 rounds**,
and the **gamma-sweep re-run at 50 rounds**. It is resumable and parallel.

## What it needs (and does NOT need)
- **Needs:** Python 3.10+, PyTorch (Blackwell/sm_120 build), torchvision, numpy, pandas.
- **Does NOT need liboqs / HQC.** The accuracy/robustness runs only cluster + train;
  `liboqs` is imported lazily and is used only by the crypto-overhead runs (already
  measured). So skip the liboqs build entirely on this machine.
- CIFAR-10, FashionMNIST, EMNIST auto-download via torchvision on first run.
  **Edge-IIoTset is not part of this battery** (it runs through the separate Kaggle
  pipeline); its f=0 rows are handled there.

## One-time setup on the 5080 machine
```powershell
git clone <repo-url> cbsafe && cd cbsafe
python -m venv .venv
.\.venv\Scripts\Activate.ps1            # (Linux: source .venv/bin/activate)

# Blackwell (RTX 5080, sm_120) PyTorch — CUDA 12.8 wheels:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
pip install numpy pandas

# sanity: GPU + sm_120 visible
python -c "import torch;print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```
If `torch.cuda.is_available()` is True and the device prints as the 5080, you're set.

## Run it
```powershell
# see what's pending (no training):
python experiments/run_revision_battery.py --dry-run

# run everything, 12 workers (tune to VRAM/CPU; 5080 16GB + i9 handles ~10-16):
python experiments/run_revision_battery.py --workers 12

# or one phase at a time:
python experiments/run_revision_battery.py --only f0     --workers 12
python experiments/run_revision_battery.py --only dial50 --workers 12
python experiments/run_revision_battery.py --only gamma50 --workers 12
```
- **Resumable:** a config counts as done only if its CSV exists *and* already has
  >= the target rounds, so interrupted or shorter (30-round) runs are re-run. Just
  re-launch the same command to continue.
- **Logs:** per-run stdout in `results/battery_logs/`. Failures are reported at the end.
- **Determinism check (recommended once):** re-run one existing config and confirm the
  number matches within noise, so the three-seed / deterministic claim survives the
  hardware change, e.g.:
  `python experiments/run_robustness.py --attack signflip --f 0.2 --aggregator hybrid --overlap 4 --dataset cifar10 --rounds 50 --seed 0`

## Getting results back
The battery writes into `results/` on the 5080 box. Copy the new/updated CSVs back
into the main repo's `results/` (same relative paths) so the table/figure scripts pick
them up. Fastest: zip `results/` (or just `results/*.csv`, `results/fmnist`,
`results/kaggle/emnist`, `results/gamma_sweep`, `results/battery_logs`) and transfer.
Alternatively set `CBSAFE_OUT` to a shared/synced folder before running.

## Scope / counts (at time of writing)
- f0 clean rows: 81 configs (9 rules x {cifar10,fmnist,emnist} x 3 seeds)
- dial50: 36 configs (median, c in {1,3,5}, f in {.05,.1,.2,.3}, 3 seeds)
- gamma50: 48 configs (hybrid/median/bulyan/krum x gamma in {2,3,8,15}, f=0.2, 3 seeds)

## Not in this battery (need code first, handled separately)
- Optimized/adaptive attack (Fang / ALIE / gamma-adaptive vs the loss probe)
- delta / suspicion-gap sensitivity sweep (needs CLI knobs added)
- Gradient-inversion measurement on the revealed cluster sums
- FLTrust / FedGT baseline re-validation
