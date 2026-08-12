# CB-SAFE — TIFS hardening plan (SEALED 2026-08-12)

Status ledger for the Claude/ChatGPT hostile-reviewer debate. Everything below is
resolved in the manuscript except the one mechanical item flagged **[IN FLIGHT]**.
Original audit preserved beneath the ledger for provenance.

## Resolution ledger

| # | Item | Status | Where it landed |
|---|------|--------|-----------------|
| Hier. | Novelty hierarchy (laundering boundary → mechanism → temporal GT → FedGT delta → HQC-supports-not-is-the-story) | **DONE** | Intro + framing; HQC scoped as confidentiality layer, not the contribution. |
| 3 | Prop-1 idealization prose (validation *near* the boundary, not a guarantee) | **DONE** | Caveat after `prop:launder`: theorem idealizes honest updates as common $h$; four-dataset collapse read as strong empirical validation near the boundary, not a guarantee under arbitrary heterogeneity. |
| 4 | "CB-SAFE+ is just FedGT renamed" | **DONE** | Faithful FedGT (their **real BCJR decoder** + recall/KMeans test) now in `tab:signflip`, `tab:detect`, dynamics fig. CB-SAFE+ *beats* it by 23.1 pts (paired, $p{=}5.3\times10^{-4}$, n=27). Re-randomized vs fixed groups + trust-free variant FedGT cannot do. |
| 5 | "FP improvement not statistically meaningful" | **DONE / superseded** | The tiny-integer FP t-test is replaced by the accuracy comparison against the real BCJR decoder (`tab:detect` FP 13–16/24 shows FedGT *over-excludes*; the 23.1-pt paired test is the headline stat). |
| 6 | "30 clients is not enough" | **DONE** | N=100/500 scaling sweep; `tab:scale-n500` (upright). FedGT's parity-check matrices + prevalence tables are hardcoded for n≤31 → framed as a concrete scalability ceiling, not an omission. |
| 8 | Privacy theorem scope | **DONE** | Corruption model now stated explicitly: **static** corruption, $|T|\le t-1$, honest-but-curious server; no adaptive-security claim. Proof is simulator + H1/H2 hybrids + Shamir + dropout + composition — left intact. |
| 10 | "Experiments don't isolate the winning component" | **DONE** | `tab:ablation-variants`: reputation(ov1) → reputation(ov4) → trust-free → hybrid isolates clustering / overlap / root-probe / temporal-COMP. Prose fixed: hybrid 50.0% *far above* faithful FedGT (collapses to chance at CIFAR f=.3). |
| — | Label-flip table (`tab:labelflip`) swap to faithful FedGT | **[IN FLIGHT]** | Faithful label-flip sweep running (5/27 CSVs at seal time). On completion: swap FedGT row → faithful, recompile, push. Nothing else blocks. |

### Rebuttal-ready (no manuscript surgery needed — answer in response letter)
- **#1** "just HQC substitution" → the laundering boundary + temporal GT are the contribution; HQC is the confidentiality layer.
- **#2** "theorem is trivial" → it makes an *exact quantitative* prediction ($\gamma^\*=2c/m-1$), not a qualitative one; obvious claims don't predict the exact failure point.
- **#7** "threat model too weak" → scoped, stated adversary; matches the secure-aggregation + Byzantine-robust literature we compare against.
- **#9** "backdoor failure undermines robustness" → scoped to *untargeted* Byzantine; backdoors defeat non-private defenses too (cited).

---

## Original audit (provenance — do not act on; superseded by ledger above)

Captured from the Claude/ChatGPT review debate. Do the **hostile-reviewer audit
first, manuscript surgery second.** Do NOT start by polishing equations/decoration
(notation is already there); the open question is whether each equation/experiment
carries novelty weight.

### Settled novelty hierarchy (restructure the paper around this)
1. Secure aggregation creates a mathematically characterizable **laundering
   boundary** gamma* = 2c/m - 1 (contaminated cluster mean = honest magnitude,
   opposite direction).
2. This **explains why** conventional robust aggregation fails despite operating
   correctly on the revealed aggregates (mechanism FedGT does not provide).
3. **Re-randomized temporal group testing** converts aggregate-level observations
   into individual-level suspicion, at zero extra leakage.
4. A **measurable improvement** over the closest secure-aggregation group-testing
   baseline (FedGT).
5. The confidentiality layer can be **HQC (code-based)** — a genuinely code-based
   PQ alternative to lattice-only FL. HQC supports the story; it is not the story.

### Two claims to harden (empirical)
- **FedGT FP advantage**: run a PROPER significance test — not a t-test on tiny
  integer counts. (Superseded: now an accuracy comparison vs the real BCJR decoder.)
- **Component ablation**: reputation(ov1) vs reputation(ov4) vs trust-free vs
  hybrid = clustering / overlap / root-probe / temporal-COMP contributions.

### Prose honesty fix (during surgery)
- Proposition 1 idealization: theorem predicts the boundary **under its model**;
  the four-dataset collapse is strong **validation near** that boundary. Do NOT let
  prose imply the theorem **guarantees** real-world collapse.

### Scale (the hardest live criticism)
- Frame larger N as an **extension**. Run a sweep N = 30 -> 100 -> (300/500).

### Hostile-reviewer audit — attacks (triage: fatal / serious / cosmetic)
1. CB-SAFE is just HQC substitution.
2. The laundering theorem is trivial/obvious.
3. The theorem relies on unrealistic identical honest updates.
4. CB-SAFE+ is just FedGT renamed.
5. The FP improvement is not statistically meaningful.
6. 30 clients is not enough.
7. The threat model is too weak.
8. The privacy theorem does not establish what the paper claims.
9. Backdoor failure undermines "Byzantine robustness."
10. Experiments do not isolate which component causes the improvement.

Likely **fatal-if-unaddressed**: scale (#6), FedGT delta (#4), component isolation
(#10) — all now resolved (see ledger).

### Order of operations
1. Finish training (all local grids + scale sweep). — done
2. Hostile-reviewer audit -> triaged surgery to-do list. — done
3. Manuscript surgery (restructure to hierarchy, harden the two claims, prose fix). — done
4. Rebuild PPT + clean repo. — pending after label-flip swap
