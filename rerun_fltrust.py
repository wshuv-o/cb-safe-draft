"""Re-run every FLTrust config on the three local datasets after the root-update
iteration fix. Staggered launch: 12 workers OOM'd previously because CUDA contexts
were created simultaneously, not because steady-state memory was short (~700 MiB/run)."""
import os, re, glob, subprocess, sys, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
PY_ = sys.executable
DRIVER = os.path.join(HERE, "experiments", "run_robustness.py")
RES = os.path.join(HERE, "results")
LOG = os.path.join(RES, "battery_logs")
os.makedirs(LOG, exist_ok=True)
WORKERS = int(os.environ.get("W", 12))
STAGGER = float(os.environ.get("STAGGER", 12))

SUB = {"cifar10": "", "fmnist": "fmnist", "emnist": os.path.join("kaggle", "emnist")}
pat = re.compile(r"robust_(\w+?)_fltrust_f(\d+)_c(\d+)_s(\d+)\.csv")

jobs = []
for ds, sub in SUB.items():
    for p in glob.glob(os.path.join(RES, sub, "robust_*_fltrust_*.csv")):
        m = pat.match(os.path.basename(p))
        if not m:
            continue
        atk, f, c, s = m.groups()
        jobs.append((ds, atk, int(f) / 100, int(c), int(s), p))
jobs.sort()

_lock = threading.Lock()
_launched = [0]


def run(j):
    ds, atk, f, c, s, out = j
    # Stagger only the FIRST wave: CUDA-context creation is what OOM'd at 12
    # workers. Staggering every job throttles the whole queue instead.
    with _lock:
        idx = _launched[0]
        _launched[0] += 1
    if idx < WORKERS:
        time.sleep(idx * STAGGER)
    name = os.path.basename(out)
    cmd = [PY_, DRIVER, "--attack", atk, "--f", str(f), "--aggregator", "fltrust",
           "--overlap", "1", "--dataset", ds, "--rounds", "50", "--seed", str(s),
           "--cluster-size", str(c)]
    t0 = time.time()
    with open(os.path.join(LOG, "fix_" + name.replace(".csv", ".log")), "w", encoding="utf-8") as lf:
        r = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT)
    try:
        with open(out, encoding="utf-8") as fh:
            n = sum(1 for _ in fh) - 1
    except OSError:
        n = -1
    ok = r.returncode == 0 and n >= 50
    return ds, name, ("OK" if ok else "FAIL"), (time.time() - t0) / 60


if __name__ == "__main__":
    print("rerun_fltrust: %d configs | workers=%d | stagger=%.0fs" % (len(jobs), WORKERS, STAGGER), flush=True)
    done = fail = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(run, j) for j in jobs]
        for fu in as_completed(futs):
            ds, n, st, m = fu.result()
            done += 1
            fail += (st == "FAIL")
            print("[%d/%d] %-4s %5.1fm %-8s %s" % (done, len(jobs), st, m, ds, n), flush=True)
    print("RERUN DONE: %d ok, %d failed" % (done - fail, fail), flush=True)
