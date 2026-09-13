"""Build the Edge-IIoT Kaggle package.

Edge-IIoTset data lives on Kaggle, so its runs happen there. This assembles the
code plus a notebook into a zip that can be uploaded as a Kaggle Dataset and run
top to bottom.

    python experiments/build_kaggle_edgeiiot.py --out cbsafe_edgeiiot_kaggle.zip

What the run fills in: label-flip currently has seed 0 only for the FedGT
aggregator, so those cells appear in the paper without error bars while every
other cell carries a standard deviation over three seeds. The notebook runs seeds
1 and 2 at 50 rounds and rebuilds the tables.

Result cells in the notebook are red: they are placeholders for numbers that
exist only once the run has finished.
"""
import argparse
import json
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

DIRS = ["src", "experiments"]
FILES = ["requirements.txt"]
SKIP_SUFFIX = (".pyc", ".pdf", ".png", ".zip", ".pptx", ".ipynb")
SKIP_DIR = ("__pycache__", ".git", ".ipynb_checkpoints", ".venv", "deck_png")

RED = ('<div style="background:#fdecea;border-left:6px solid #c0392b;'
       'padding:10px 14px;border-radius:4px">\n')


def md(t):
    return {"cell_type": "markdown", "metadata": {}, "source": t.splitlines(True)}


def code(t):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": t.splitlines(True)}


def todo(title, body):
    return md(RED + "<b>&#9888; TO FILL IN &mdash; %s</b><br><br>\n%s\n</div>"
              % (title, body))


def notebook():
    cells = [
        md("# CB-SAFE &mdash; Edge-IIoTset top-up run\n\n"
           "Edge-IIoTset data lives on Kaggle, so its experiments run here.\n\n"
           "**What is missing.** Label-flip was run with a single seed to bound "
           "runtime, which the paper footnotes. Every configuration was later "
           "backfilled to three seeds except FedGT, which still has seed 0 only at "
           "$f = 0.1, 0.2, 0.3$. Those three cells therefore appear without error "
           "bars while every neighbouring cell carries a standard deviation.\n\n"
           "**What this notebook does.** Runs FedGT label-flip seeds 1 and 2 at "
           "**50 rounds**, then rebuilds the tables.\n\n"
           "**Red cells are placeholders** for numbers that exist only after the run."),

        md("## 1. Setup\n\n"
           "Attach the Edge-IIoTset data as a Kaggle Dataset, and upload this "
           "package as a second Dataset."),
        code("!pip -q install torch torchvision numpy pandas scikit-learn scipy\n"
             "import os, glob, zipfile, subprocess, sys, time\n"
             "\n"
             "CODE = '/kaggle/working/cbsafe_run'\n"
             "src = glob.glob('/kaggle/input/**/cbsafe_edgeiiot_kaggle.zip', recursive=True)\n"
             "assert src, 'upload cbsafe_edgeiiot_kaggle.zip as a Kaggle Dataset first'\n"
             "os.makedirs(CODE, exist_ok=True)\n"
             "zipfile.ZipFile(src[0]).extractall(CODE)\n"
             "os.chdir(CODE)\n"
             "print(sorted(os.listdir('.')))"),

        md("## 2. Confirm the round count before running\n\n"
           "`run_all_kaggle.py` defaults to **25 rounds**. The published tables use "
           "**50**. Setting `CBSAFE_ROUNDS` is what keeps this run comparable with "
           "the existing results, so check the value printed below before going on."),
        code("os.environ['CBSAFE_OUT']         = '/kaggle/working/results'\n"
             "os.environ['CBSAFE_DATASETS']    = 'edgeiiot'\n"
             "os.environ['CBSAFE_ATTACKS']     = 'labelflip'\n"
             "os.environ['CBSAFE_ROUNDS']      = '50'      # must be 50, not the default 25\n"
             "os.environ['CBSAFE_OTHER_SEEDS'] = '1,2'     # seed 0 already exists\n"
             "\n"
             "for k in ('CBSAFE_OUT','CBSAFE_DATASETS','CBSAFE_ATTACKS',\n"
             "          'CBSAFE_ROUNDS','CBSAFE_OTHER_SEEDS'):\n"
             "    print('%-20s %s' % (k, os.environ[k]))\n"
             "assert os.environ['CBSAFE_ROUNDS'] == '50', 'round count must match the paper'"),

        md("## 3. Time one configuration first\n\n"
           "Kaggle sessions are time limited. Measure one run before committing to "
           "the grid, so the budget is known rather than guessed."),
        code("t0 = time.time()\n"
             "os.environ['CBSAFE_OTHER_SEEDS'] = '1'\n"
             "subprocess.run([sys.executable, 'experiments/run_all_kaggle.py'], check=False)\n"
             "print('elapsed for the seed-1 pass: %.1f min' % ((time.time()-t0)/60))"),
        todo("Runtime",
             "Minutes for the seed-1 pass: <b>________</b><br>\n"
             "Projected total for seeds 1 and 2: <b>________</b><br><br>\n"
             "If this will not fit in the session limit, run seed 1 now, save the "
             "output, and do seed 2 in a second session. The runner skips "
             "configurations whose CSV already exists, so re-running is safe."),

        md("## 4. Run the remaining seed"),
        code("os.environ['CBSAFE_OTHER_SEEDS'] = '2'\n"
             "subprocess.run([sys.executable, 'experiments/run_all_kaggle.py'], check=False)\n"
             "\n"
             "got = sorted(glob.glob('/kaggle/working/results/kaggle/edgeiiot/robust_labelflip_fedgt_*'))\n"
             "print('FedGT label-flip files now present:')\n"
             "for g in got: print('  ', os.path.basename(g))"),
        todo("Coverage after the run",
             "FedGT label-flip files present: <b>____ of 9</b> "
             "(3 values of $f$ &times; 3 seeds)<br>\n"
             "Any configuration that failed: <b>________________</b>"),

        md("## 5. Read off the numbers\n\n"
           "Final-round accuracy per configuration, which is what the table cell "
           "reports."),
        code("import pandas as pd, numpy as np, collections, re\n"
             "rows = collections.defaultdict(list)\n"
             "for p in glob.glob('/kaggle/working/results/kaggle/edgeiiot/robust_labelflip_fedgt_*.csv'):\n"
             "    df = pd.read_csv(p)\n"
             "    f = int(re.search(r'_f(\\d\\d)_', os.path.basename(p)).group(1))\n"
             "    rows[f].append(100*df['acc'].iloc[-1])\n"
             "for f in sorted(rows):\n"
             "    v = np.array(rows[f])\n"
             "    print('f=%.1f  n=%d  acc = %.1f +/- %.1f' %\n"
             "          (f/100, len(v), v.mean(),\n"
             "           v.std(ddof=1) if len(v) > 1 else 0.0))"),
        todo("FedGT label-flip on Edge-IIoTset",
             "f = 0.1: <b>______ &plusmn; ______</b> &nbsp; (paper currently: 62.0, no error bar)<br>\n"
             "f = 0.2: <b>______ &plusmn; ______</b> &nbsp; (paper currently: 62.7, no error bar)<br>\n"
             "f = 0.3: <b>______ &plusmn; ______</b> &nbsp; (paper currently: 62.0, no error bar)<br><br>\n"
             "These replace the three single-seed cells in the Edge-IIoTset row of "
             "the label-flip table, and let the single-seed footnote be dropped."),

        md("## 6. Rebuild the tables"),
        code("subprocess.run([sys.executable, 'experiments/build_tables.py'], check=False)\n"
             "for p in glob.glob('/kaggle/working/results/tables/*.tex'):\n"
             "    print('---', os.path.basename(p))\n"
             "    print(open(p).read()[:600])"),
        todo("Did the numbers move?",
             "Did the mean shift once three seeds were averaged? "
             "<b>yes / no</b><br>\n"
             "If a mean moved by more than about one point, the single-seed value "
             "was not representative, which is worth a sentence in the paper."),

        md("## 7. Save the output\n\n"
           "Kaggle discards `/kaggle/working` when the session ends unless output is "
           "saved. Run this before the session times out, then download "
           "`results/kaggle/edgeiiot/` and drop it into the repository at the same "
           "path."),
        code("!cd /kaggle/working && zip -qr edgeiiot_topup.zip results/kaggle/edgeiiot results/tables\n"
             "!ls -la /kaggle/working/edgeiiot_topup.zip"),
    ]
    return {"cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3",
                                        "language": "python", "name": "python3"},
                         "language_info": {"name": "python", "version": "3.11"}},
            "nbformat": 4, "nbformat_minor": 5}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(REPO, "cbsafe_edgeiiot_kaggle.zip"))
    a = ap.parse_args()

    nb_path = os.path.join(REPO, "cbsafe_edgeiiot.ipynb")
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(notebook(), f, indent=1)

    n = 0
    with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as z:
        for d in DIRS:
            for root, dirs, files in os.walk(os.path.join(REPO, d)):
                dirs[:] = [x for x in dirs if x not in SKIP_DIR]
                for fn in files:
                    if fn.endswith(SKIP_SUFFIX):
                        continue
                    p = os.path.join(root, fn)
                    z.write(p, os.path.relpath(p, REPO).replace("\\", "/"))
                    n += 1
        for rel in FILES:
            p = os.path.join(REPO, rel)
            if os.path.exists(p):
                z.write(p, rel)
                n += 1
        z.write(nb_path, "cbsafe_edgeiiot.ipynb")
        n += 1

    red = sum(1 for c in notebook()["cells"]
              if c["cell_type"] == "markdown" and "TO FILL IN" in "".join(c["source"]))
    print("wrote %s" % a.out)
    print("  %d files, %.2f MB" % (n, os.path.getsize(a.out) / 1e6))
    print("  %d red placeholder cells" % red)


if __name__ == "__main__":
    main()
