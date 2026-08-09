# -*- coding: utf-8 -*-
"""CB-SAFE combined deck (reflects the user's edited structure + 2 new sections).
Order: Intro, Background, Related Work (survey), Related Work: FedGT, Methodology
(Base), Limitations, Research Question & Objective, Proposed Method, System
Architecture(Ours), Methodology (Ours) x3, Integration, Comparison, Contributions,
Summary, then full-paper results. One classic title per slide, no author footer,
page number only, Calibri, in-text [n] + full-form footnote refs, larger text."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from PIL import Image

BLUE = RGBColor(0x2A, 0x78, 0xD6)
INK  = RGBColor(0x0B, 0x0B, 0x0B)
INK2 = RGBColor(0x26, 0x25, 0x1F)
MUT  = RGBColor(0x89, 0x87, 0x81)
BODY = "Calibri"
FIG  = r"d:/ISM_Quantum/results/figs/"

# larger type sizes (user: "make text bigger")
SZ_TITLE, SZ_LEAD, SZ_BULLET, SZ_CITE, SZ_PAGE, SZ_REF = 34, 16, 18, 9, 12, 13

P = Presentation()
P.slide_width = Inches(13.333)
P.slide_height = Inches(7.5)
BLANK = P.slide_layouts[6]
TOTAL = 24
_PG = [0]

REF = {
 1: '[1] M. Xhemrishi, J. \u00d6stman, A. Wachter-Zeh, and A. Graell i Amat, "FedGT: Identification of '
    'malicious clients in federated learning with secure aggregation," IEEE Trans. Inf. Forensics '
    'Security, vol. 20, pp. 2577\u20132592, 2025.',
 2: '[2] K. Bonawitz, V. Ivanov, B. Kreuter, A. Marcedone, H. B. McMahan, S. Patel, D. Ramage, A. Segal, '
    'and K. Seth, "Practical secure aggregation for privacy-preserving machine learning," in Proc. ACM '
    'CCS, 2017, pp. 1175\u20131191.',
 3: '[3] National Institute of Standards and Technology, "Status report on the fourth round of the NIST '
    'post-quantum cryptography standardization process," NIST IR 8545, Mar. 2025.',
 4: '[4] P. W. Shor, "Polynomial-time algorithms for prime factorization and discrete logarithms on a '
    'quantum computer," SIAM J. Comput., vol. 26, no. 5, pp. 1484\u20131509, 1997.',
 5: '[5] X. Cao, M. Fang, J. Liu, and N. Z. Gong, "FLTrust: Byzantine-robust federated learning via trust '
    'bootstrapping," in Proc. NDSS, 2021.',
 6: '[6] D. Yin, Y. Chen, R. Kannan, and P. Bartlett, "Byzantine-robust distributed learning: Towards '
    'optimal statistical rates," in Proc. ICML, 2018, pp. 5650\u20135659.',
 7: '[7] P. Blanchard, E. M. El Mhamdi, R. Guerraoui, and J. Stainer, "Machine learning with adversaries: '
    'Byzantine tolerant gradient descent," in Proc. NeurIPS, 2017, pp. 119\u2013129.',
 8: '[8] K. Pillutla, S. M. Kakade, and Z. Harchaoui, "Robust aggregation for federated learning," IEEE '
    'Trans. Signal Process., vol. 70, pp. 1142\u20131154, 2022.',
 9: '[9] National Institute of Standards and Technology, "Module-lattice-based key-encapsulation mechanism '
    'standard," FIPS 203, Aug. 2024.',
}


def tb(s, l, t, w, h):
    b = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    b.text_frame.word_wrap = True
    return b


def run(p, text, size, color, bold=False, italic=False):
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.name = BODY; r.font.bold = bold
    r.font.italic = italic; r.font.color.rgb = color
    return r


def run_md(p, text, size, color):
    for i, seg in enumerate(text.split("**")):
        if seg == "":
            continue
        run(p, seg, size, INK if i % 2 else color, bold=(i % 2 == 1))


def footer(s, page):
    if page:
        pn = tb(s, 11.95, 7.02, 1.1, 0.32); pp = pn.text_frame.paragraphs[0]
        pp.alignment = PP_ALIGN.RIGHT; run(pp, page, SZ_PAGE, MUT)


def cites(s, keys):
    if not keys:
        return
    bx = tb(s, 0.75, 6.44, 11.9, 0.6).text_frame
    for i, k in enumerate(keys):
        p = bx.paragraphs[0] if i == 0 else bx.add_paragraph()
        p.space_after = Pt(1); run(p, REF[k], SZ_CITE, INK2, italic=True)


def img_ar(name):
    w, h = Image.open(FIG + name).size
    return w / h


def content(title, bullets, cite=None, lead=None,
            fig=None, fig_center=None, bullet_w=None, bold=False):
    s = P.slides.add_slide(BLANK)
    run(tb(s, 0.75, 0.42, 11.9, 0.95).text_frame.paragraphs[0], title, SZ_TITLE, INK, bold=True)
    top = 1.55
    if lead:
        run(tb(s, 0.75, top, 11.9, 0.6).text_frame.paragraphs[0], lead, SZ_LEAD, INK2, italic=True)
        top += 0.58
    bw = bullet_w if bullet_w else (7.0 if fig else 11.9)
    if bullets:
        body = tb(s, 0.75, top, bw, 4.4).text_frame
        for i, b in enumerate(bullets):
            p = body.paragraphs[0] if i == 0 else body.add_paragraph()
            p.space_after = Pt(9)
            r0 = p.add_run(); r0.text = "\u25aa  "
            r0.font.size = Pt(SZ_BULLET); r0.font.name = BODY; r0.font.color.rgb = BLUE
            (run_md if bold else run)(p, b, SZ_BULLET, INK2)
    if fig:
        s.shapes.add_picture(FIG + fig, Inches(8.05), Inches(top + 0.1), width=Inches(4.85))
    if fig_center:
        name, ftop, fh = fig_center
        W = fh * img_ar(name)
        if W > 12.4:
            W = 12.4; fh = W / img_ar(name)
        s.shapes.add_picture(FIG + name, Inches((13.333 - W) / 2), Inches(ftop), height=Inches(fh))
    cites(s, cite or [])
    _PG[0] += 1
    footer(s, f"{_PG[0]} / {TOTAL}")
    return s


# ===================== TITLE =====================
s = P.slides.add_slide(BLANK)
run(tb(s, 0.75, 1.9, 11.9, 0.4).text_frame.paragraphs[0],
    "POST-QUANTUM CRYPTOGRAPHY \u00d7 FEDERATED LEARNING", 14, BLUE, bold=True)
run(tb(s, 0.75, 2.45, 11.7, 2.0).text_frame.paragraphs[0],
    "CB-SAFE: Code-Based Post-Quantum Secure Aggregation for Byzantine-Robust Federated Learning",
    38, INK, bold=True)
run(tb(s, 0.75, 4.95, 11.7, 0.5).text_frame.paragraphs[0],
    "Md Wahiduzzaman Suva (26-94088-2)   \u00b7   Esm-e Moula Chowdhury Abha (26-94089-2)", 18, INK2)
run(tb(s, 0.75, 5.45, 11.7, 0.4).text_frame.paragraphs[0],
    "Department of Computer Science, American International University\u2013Bangladesh", 15, MUT)

# ===================== PART I =====================
content("Introduction", [
    "Federated learning shares model updates, not raw data, yet **those updates still leak private training data**.",
    "Secure aggregation [2] hides updates behind masks, but its key exchange **breaks under a quantum computer** (harvest-now, decrypt-later).",
    "Every post-quantum fix today is **lattice-only, a monoculture**; and hiding updates also blinds the server to poisoned ones.",
    "Goal: one protocol that is **private, post-quantum with crypto diversity, and Byzantine-robust**.",
], cite=[2], bold=True)

content("Background and Motivation", [
    "Secure aggregation = pairwise masks that cancel in the sum; the server sees only the aggregate, never an individual.",
    "Quantum threat: Shor's algorithm [4] breaks classical key exchange, and traffic recorded today is decryptable later.",
    "Crypto diversity: NIST selected the code-based KEM HQC in 2025 [3] to hedge a lattice break; that diversity has not reached FL.",
    "Robustness tension: privacy hides exactly the per-client signal that poisoning defenses need.",
], cite=[3, 4])

# NEW: broad related-work survey
content("Related Work", [
    "Secure aggregation lets the server learn only the sum, hiding each client's update [2]; later designs cut its overhead.",
    "Byzantine-robust aggregation resists poisoning but ignores privacy: coordinate-wise median [6] and Multi-Krum [7].",
    "Group testing identifies a few malicious clients from pooled tests; FedGT [1] brings this idea to secure-aggregation FL.",
    "Gap: no prior work delivers code-based post-quantum confidentiality and Byzantine robustness together.",
], cite=[1, 2, 6, 7])

# existing FedGT-focused slide, retitled to disambiguate from the survey above
content("Related Work: Closest Peer (FedGT)", [
    "FedGT [1] (IEEE TIFS, 2025) is the closest peer to our robustness mechanism.",
    "Idea: group clients into overlapping test groups; the server sees only group aggregates, so privacy is preserved.",
    "A statistical test flags groups that contain malicious clients; a decoder then identifies and removes the culprits.",
    "Borrowed from group testing: find a few defectives with far fewer pooled tests than testing everyone.",
], cite=[1])

content("Methodology (Base Paper)", [
    "In FedGT [1], an assignment matrix groups n clients into m overlapping groups (the parity-check structure of a code).",
    "Each group is securely aggregated; a test on the group aggregate is positive if any member is malicious.",
    "A COMP / Neyman-Pearson decoder infers which clients are malicious from the group test results.",
    "Flagged clients are excluded; the remaining clean clients are aggregated into the global model.",
], cite=[1])

content("Limitations", [
    "Crypto: FedGT [1] treats secure aggregation as a black box, with **no post-quantum layer**, in a lattice-only field.",
    "Cost: it needs a **server validation set** and per-round group testing over fixed overlapping groups.",
    "Single-round decode: it identifies attackers from **one round's tests**, using no information across rounds.",
    "Unexplained failure: it does not characterize **why ordinary robust aggregation breaks** once updates are hidden.",
], cite=[1], bold=True)

# NEW: research question and objective
content("Research Question and Objective", [
    "**RQ1** Can code-based (non-lattice) cryptography secure FL aggregation at a practical cost?",
    "**RQ2** Why do robust aggregation rules fail once updates are hidden inside secure cluster sums?",
    "**RQ3** Can malicious clients be identified from group-level observations alone, without a validation set?",
    "**Objective** Design CB-SAFE(+) to answer all three, and validate it on four datasets against eight baselines.",
], lead="Can one protocol be private, post-quantum, and Byzantine-robust at the same time?", bold=True)

content("Proposed Method", [
    "Hide updates within clusters using a code-based (HQC) masking protocol [2]: the server sees only cluster sums.",
    "Run group testing [1] across re-randomized clusters over rounds to identify attackers (CB-SAFE+).",
    "Confidentiality lives below the cluster boundary; robustness operates above it; post-quantum by construction.",
], lead="One framework that is private, post-quantum, and Byzantine-robust at the same time.",
    cite=[1, 2])

# System Architecture moved here (right after Proposed Method), per the user's edit
content("System Architecture (Ours)", [],
    lead="One training round: confidentiality within clusters [2], temporal group testing over re-randomized clusters [1], robust aggregation.",
    cite=[1, 2], fig_center=("fig_architecture.png", 2.0, 4.35))

content("Methodology (Ours): Masking", [
    "We adopt Bonawitz-style double masking [2]: pairwise masks cancel in the cluster sum, so individuals stay hidden.",
    "Dropout resilience via Shamir secret sharing of the self-masks.",
    "Our change: masks are seeded from a KEM, so per-round traffic carries no cryptographic bytes at all.",
], cite=[2], fig="fig_masking.png")

content("Methodology (Ours): Detection", [
    "We adopt the core idea from FedGT [1]: identify malicious clients from group-level observations, never from individual updates.",
    "The groups are the privacy-preserving cluster sums (the pools); a probe flags contaminated pools.",
    "Our change: tests repeat over re-randomized clusters and accumulate across rounds (temporal group testing).",
], cite=[1])

content("Methodology (Ours): Cryptography", [
    "We adopt HQC, the code-based KEM NIST selected in 2025 [3], for post-quantum confidentiality.",
    "Its security rests on syndrome decoding of quasi-cyclic codes, not lattices: genuine cryptographic diversity.",
    "Our change: HQC sits behind a KEM-agnostic interface, so ML-KEM [9] swaps in with one configuration line.",
], cite=[3, 9])

content("Methodology (Ours): Integration", [
    "HQC-seeded masking [2], [3] hides updates inside clusters, so the server sees only cluster sums.",
    "Group testing [1] then runs across those cluster sums, over re-randomized rounds, to name the attackers.",
    "Net design: privacy below the cluster boundary, robustness above it, code-based crypto throughout.",
    "On top we add our own pieces: the laundering theorem and a server root-loss probe.",
], lead="Masking + group testing + a code-based KEM become one coherent framework.",
    cite=[1, 2, 3])

content("Comparison", [
    "Crypto: FedGT [1] is crypto-agnostic \u2192 **CB-SAFE is code-based post-quantum**.",
    "Detection: FedGT uses single-round COMP + a validation set \u2192 **CB-SAFE uses temporal accumulation + a root-loss probe**.",
    "Theory: FedGT gives no failure model \u2192 **CB-SAFE proves the laundering boundary**.",
    "Results: accuracy ties FedGT with **fewer false exclusions and ~4\u00d7 lower cost**.",
], cite=[1], fig="fig_signflip_acc_slide.png", bold=True)

content("Contributions", [
    "**First code-based post-quantum secure aggregation** for FL: cryptographic diversity beyond lattices.",
    "The **laundering theorem**: at \u03b3*=2c/m\u22121 a poisoned cluster mean is magnitude-invisible, explaining why robust rules fail.",
    "**Temporal group testing** over re-randomized clusters (extending FedGT [1]) with a root-loss probe [5]: identifies attackers the server never sees.",
    "A **trust-free variant** that needs no root dataset, a capability FedGT does not offer.",
], cite=[1, 5], fig="fig_launder_geo.png", bold=True)

content("Summary", [
    "Took: masking [2], group testing [1], and a code-based KEM [3].",
    "Changed: temporal group testing over re-randomized clusters; HQC-seeded, KEM-agnostic masking.",
    "New: the laundering theorem, the first code-based PQ secure aggregation, and trust-free detection.",
    "Payoff: private, post-quantum, and Byzantine-robust FL that ties the state of the art at lower cost.",
], lead="End of the method presentation; the full-paper results and figures follow.",
    cite=[1, 2, 3])

# ===================== PART II: RESULTS =====================
content("Experimental Setup", [
    "Images: CIFAR-10, FashionMNIST, EMNIST-balanced (47 classes). Tabular: Edge-IIoTset (IoT intrusion).",
    "Non-IID split via a Dirichlet(0.5) partition; 30 communication rounds; clusters of size c = 3.",
    "Attacks: sign-flip (laundering), label-flip, backdoor. Baselines: mean, trimmed, median [6], Krum, Bulyan, RFA, FLTrust, FedGT [1].",
], cite=[1, 6], bullet_w=7.6, fig="shot_dirichlet_fig.png")

content("Results: Robustness", [
    "Under sign-flip at f \u2265 0.2 every coordinate-wise rule collapses to chance; CB-SAFE+ holds and ties FedGT [1].",
], lead="Sign-flip test accuracy across four datasets (from the paper, Table V).",
    cite=[1], fig_center=("shot_signflip_table.png", 2.7, 3.45))

content("Results: Training Dynamics", [],
    lead="Accuracy vs. round for eight rules incl. FedGT [1], over three datasets and three malicious fractions; "
         "CB-SAFE+ tracks the clean baseline while the others diverge (paper, Fig. 7).",
    cite=[1], fig_center=("shot_dynamics_fig.png", 2.45, 3.9))

content("Results: Detection", [
    "Malicious and honest suspicion separate within a few rounds; attackers are named from group-level observations alone, following the group-testing idea of FedGT [1].",
], lead="Temporal suspicion separation (from the paper, Fig. 8).",
    cite=[1], fig_center=("shot_suspicion_fig.png", 2.95, 3.25))

content("Results: Generalization", [
    "Label-flip is milder: no coordinate-wise rule collapses, which isolates laundering as the cause of the sign-flip failures.",
], lead="Label-flip test accuracy (from the paper, Table VI); CB-SAFE+ matches FedGT [1] and leads at the hardest setting (f=0.3).",
    cite=[1], fig_center=("shot_labelflip_table.png", 2.7, 3.4))

content("Results: Efficiency", [
    "Code-based (HQC [3]) confidentiality gives crypto diversity beyond lattices; ML-KEM [9] swaps in unchanged.",
    "One-time setup is paid once and stays under 0.03% of total traffic; per-round bytes are KEM-independent.",
], lead="Measured per-client overhead (from the paper, Table II).",
    cite=[3, 9], bullet_w=11.9, fig_center=("shot_overhead_table.png", 3.45, 3.05))

content("Results: Scalability", [
    "CB-SAFE masks only within clusters of c=3, so each client keeps c−1 partners: per-client cost is flat in N, unlike all-pairs secure aggregation [2] which grows O(N).",
    "At N=1000, one-time setup is 15.2 KiB (HQC) vs 7.4 MiB for all-pairs — a 500× reduction; the privacy law (1−f)^c and the laundering bound are per-cluster, so guarantees are N-independent.",
], lead="Per-client cost vs client population (from the paper).",
    cite=[2], fig_center=("fig_scaling_cost.png", 3.55, 2.75))

content("Conclusion", [
    "CB-SAFE unifies code-based PQ secure aggregation [2], [3] with temporal group-testing robustness [1] in one protocol.",
    "It ties the state of the art (FedGT [1]) on robustness and detection, at lower cost, and adds crypto diversity plus a failure theory.",
    "Limitations: update authentication is out of the code-based scope; EMNIST detection uses a single seed.",
    "Future work: code-based signatures for authentication, larger client populations, and adaptive attackers.",
], cite=[1, 2, 3])

# ===================== REFERENCES =====================
rs = P.slides.add_slide(BLANK)
run(tb(rs, 0.75, 0.42, 11.9, 0.95).text_frame.paragraphs[0], "References", SZ_TITLE, INK, bold=True)
tf = tb(rs, 0.75, 1.55, 11.9, 5.3).text_frame
for i in range(1, 10):
    p = tf.paragraphs[0] if i == 1 else tf.add_paragraph()
    p.space_after = Pt(7); run(p, REF[i], SZ_REF, INK2)

out = r"d:/ISM_Quantum/paper/cbsafe_deck.pptx"
P.save(out)
print("saved", out, "| total slide objects:", len(P.slides._sldIdLst))
