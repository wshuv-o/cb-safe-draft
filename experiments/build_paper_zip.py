"""Bundle the TDSC manuscript into a self-contained LaTeX zip.

The repository layout is preserved (paper/ alongside results/tables/) because
cbsafe_tdsc.tex pulls its tables in as ../results/tables/*.tex. Flattening the
tree would break those inputs, so the zip keeps the two directories and the
document compiles from paper/ with no edits:

    unzip cbsafe_tdsc_latex.zip && cd paper && tectonic -X compile cbsafe_tdsc.tex

References are inline (thebibliography), so no bibtex pass and no .bib file.
"""

import argparse
import os
import re
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TEX = os.path.join(REPO, "paper", "cbsafe_tdsc.tex")


def deps():
    """Every file the document needs, discovered from the source rather than
    listed by hand so a new figure or table cannot be silently left out."""
    src = open(TEX, encoding="utf-8").read()
    out = ["paper/cbsafe_tdsc.tex", "paper/IEEEtran.cls"]
    # Figures resolve through \graphicspath, not the document's own directory, so
    # read the path out of the source instead of assuming paper/.
    gp = re.search(r"\\graphicspath\{\{([^}]*)\}\}", src)
    gdir = os.path.normpath(os.path.join("paper", gp.group(1))) if gp else "paper"
    for g in sorted(set(re.findall(r"includegraphics\[[^]]*\]\{([^}]*)\}", src))):
        out.append(os.path.join(gdir, g).replace(os.sep, "/"))
    for i in sorted(set(re.findall(r"\\input\{([^}]*)\}", src))):
        out.append(os.path.normpath(os.path.join("paper", i)).replace(os.sep, "/"))
    return out


def main():
    ap = argparse.ArgumentParser()
    # Written under paper/ so the .gitignore "!paper/*.zip" exception tracks it;
    # a root-level *.zip is ignored and the deliverable would go unpushed.
    ap.add_argument("--out", default=os.path.join(REPO, "paper", "cbsafe_tdsc_latex.zip"))
    a = ap.parse_args()

    files, missing = deps(), []
    with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in files:
            p = os.path.join(REPO, rel)
            if not os.path.exists(p):
                missing.append(rel)
                continue
            z.write(p, rel)
        pdf = os.path.join(REPO, "paper", "cbsafe_tdsc.pdf")
        if os.path.exists(pdf):
            z.write(pdf, "paper/cbsafe_tdsc.pdf")

    print("wrote %s (%.2f MB)" % (a.out, os.path.getsize(a.out) / 1e6))
    for rel in files:
        print("   %s %s" % ("--" if rel in missing else "ok", rel))
    if missing:
        raise SystemExit("MISSING %d dependency file(s); zip will not compile"
                         % len(missing))


if __name__ == "__main__":
    main()
