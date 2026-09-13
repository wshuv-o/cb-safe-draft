"""Re-run the gamma-sweep points plot_gamma_basin.py plots but run_revision_battery.py
never re-ran: geomedian and trimmed. Same 50-round target as the other four rules."""
import os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
DRIVER = os.path.join(HERE, "experiments", "run_robustness.py")
RES = os.path.join(HERE, "results", "gamma_sweep")
LOG = os.path.join(HERE, "results", "battery_logs")
os.makedirs(LOG, exist_ok=True)

JOBS = [(agg, g, s)
        for agg in ("geomedian", "trimmed")
        for g in (2.0, 3.0, 8.0, 15.0)
        for s in (0, 1, 2)]


def rows(p):
    try:
        with open(p, encoding="utf-8") as f:
            return sum(1 for _ in f) - 1
    except OSError:
        return -1


def run(t):
    agg, g, s = t
    name = "robust_signflip_%s_f20_c3_g%03d_s%d.csv" % (agg, int(round(g * 10)), s)
    out = os.path.join(RES, name)
    if rows(out) >= 50:
        return name, "SKIP", 0.0
    cmd = [PY, DRIVER, "--attack", "signflip", "--f", "0.2", "--aggregator", agg,
           "--overlap", "1", "--dataset", "cifar10", "--rounds", "50",
           "--seed", str(s), "--signflip-gamma", str(g), "--cluster-size", "3"]
    t0 = time.time()
    with open(os.path.join(LOG, name.replace(".csv", ".log")), "w", encoding="utf-8") as lf:
        r = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT)
    return name, ("OK" if r.returncode == 0 and rows(out) >= 50 else "FAIL"), (time.time() - t0) / 60


if __name__ == "__main__":
    print("fix_gamma: %d configs (geomedian, trimmed x gamma{2,3,8,15} x 3 seeds)" % len(JOBS), flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(run, j): j for j in JOBS}
        for fu in as_completed(futs):
            n, st, m = fu.result()
            done += 1
            print("[%d/%d] %-4s %5.1fm %s" % (done, len(JOBS), st, m, n), flush=True)
    print("FIX DONE", flush=True)
