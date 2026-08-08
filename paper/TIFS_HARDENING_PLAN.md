# CB-SAFE — TIFS hardening plan (work on this tomorrow)

Captured from the Claude/ChatGPT review debate. Do the **hostile-reviewer audit
first, manuscript surgery second.** Do NOT start by polishing equations/decoration
(notation is already there); the open question is whether each equation/experiment
carries novelty weight.

## Settled novelty hierarchy (restructure the paper around this)
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

## Two claims to harden (empirical)
- **FedGT FP advantage** (hybrid FP 0.0/0.7/0.3 vs FedGT 1.3/3.3/1.3 at equal
  catch 3/3,6/6,9/9): run a PROPER significance test — not a t-test on tiny integer
  counts (paired test or Poisson-rate comparison across the 3 seeds). Same harness
  already controls clients/clustering/partition/seeds/f/rounds/FP-definition; must
  STATE the detection-budget asymmetry rather than pretend it is controlled.
- **Component ablation** (answers "just FedGT renamed" + "which component earns the
  gain"): make explicit the isolation we already largely have —
  reputation(ov1) vs reputation(ov4) vs trust-free vs hybrid = clustering / overlap
  / root-probe / temporal-COMP contributions.

## Prose honesty fix (during surgery)
- Proposition 1 idealization: theorem predicts the boundary **under its model**
  (honest updates ~= h up to noise); the four-dataset collapse is strong
  **validation near** that boundary. Do NOT let prose imply the theorem
  **guarantees** real-world collapse under arbitrary heterogeneous updates.

## Scale (the hardest live criticism)
- Frame larger N as an **extension**, consistent with the direct-comparison
  literature — not missing basic validation. It is deliverable: simulator takes
  `--n-clients`. Run a sweep N = 30 -> 100 -> (300) on sign-flip when time allows.

## Hostile-reviewer audit — attacks to run tomorrow (triage: fatal / serious / cosmetic)
1. CB-SAFE is just HQC substitution.
2. The laundering theorem is trivial/obvious. (Rebuttal: exact quantitative
   prediction, not qualitative; obvious claims do not predict the exact failure point.)
3. The theorem relies on unrealistic identical honest updates. (See prose fix.)
4. CB-SAFE+ is just FedGT renamed. (Rebuttal: re-randomized vs fixed groups,
   trust-free variant FedGT cannot do, + component ablation.)
5. The FP improvement is not statistically meaningful. (Fix: significance test.)
6. 30 clients is not enough. (Fix: scale sweep + extension framing.)
7. The threat model is too weak.
8. The privacy theorem does not establish what the paper claims.
9. Backdoor failure undermines "Byzantine robustness." (Rebuttal: scope to
   untargeted; backdoors defeat non-private defenses too — cite.)
10. Experiments do not isolate which component causes the improvement. (Fix:
    component ablation, #4.)

Likely **fatal-if-unaddressed**: scale (#6), FedGT delta (#4), component isolation
(#10). Rest are rebuttable with existing/cheap material. Rank survivors by
damage-if-unaddressed vs cost-to-fix.

## Order of operations
1. Finish training (all local grids + any scale sweep).
2. Hostile-reviewer audit -> triaged surgery to-do list.
3. Manuscript surgery (restructure to hierarchy, harden the two claims, prose fix).
4. Rebuild PPT + clean repo.
