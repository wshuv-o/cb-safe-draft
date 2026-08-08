"""CB-SAFE+ defense: temporal group testing over privacy-preserving cluster sums.

Why coordinate-wise robust rules fail under secure aggregation (the "laundering"
effect): with cluster size c and one gamma-amplified sign-flipper per cluster, the
cluster mean is approximately -((gamma - (c-1))/c) times an honest mean --- similar
magnitude, inverted direction. Poisoned cluster sums are not magnitude outliers, so
trimmed mean and median see a near-symmetric +/- cloud whose center is ~0 and
learning stalls. The same signature, however, is directionally conspicuous.

The defense (per round r):
  1. RE-RANDOMIZE the cluster partition (fresh seeded permutation each round).
  2. Aggregate securely within clusters; the server sees only cluster means.
  3. Build a Krum reference from the cluster means (vector selection resists
     laundering) and FLAG clusters whose mean opposes it (cosine < 0).
  4. Every member of a flagged cluster gets +1 suspicion; suspicion_i is the
     flagged fraction over rounds. A malicious client is flagged whenever its
     cluster is caught (~always); an honest client only when randomly co-clustered
     with a malicious one (prob. 1-(1-f)^{c-1} < 1). The scores separate.
  5. After a warmup, clients with suspicion above tau are EXCLUDED from
     aggregation (they may keep submitting; their clusters are ignored).

Privacy cost is explicit and bounded: beyond cluster sums, the server learns one
bit per cluster per round (flagged or not) --- never an individual update. Key
material supports re-clustering at zero per-round KEM cost by establishing all
pairwise secrets once at setup (O(N) encapsulations per client).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import robust

# flag a cluster when its root-loss increase exceeds the best cluster's by this
# margin (cross-entropy units); poisoned ascent directions overshoot it by far
PROBE_MARGIN = 0.25


@dataclass
class ReputationState:
    warmup: int = 5          # rounds before exclusion starts
    tau: float = 0.85        # (legacy) fixed exclusion threshold; unused when adaptive
    adaptive: bool = True    # gap-based adaptive exclusion instead of fixed tau
    min_gap: float = 0.20    # smallest suspicion gap that counts as a real separation
    min_floor: float = 0.35  # a flagged group must sit above this to be excluded
    n_byzantine: int = 2     # Krum parameter for the reference
    flags: dict = field(default_factory=dict)     # client -> times in flagged cluster
    rounds: dict = field(default_factory=dict)    # client -> rounds participated
    excluded: set = field(default_factory=set)
    last_info: dict = field(default_factory=dict)  # diagnostics from the last round

    def suspicion(self, i: int) -> float:
        r = self.rounds.get(i, 0)
        return self.flags.get(i, 0) / r if r else 0.0

    def exclude_now(self) -> set:
        """Decide who to exclude from accumulated suspicion. Adaptive rule: find the
        largest gap in the sorted suspicion scores; if it exceeds min_gap and the
        high side is a MINORITY sitting above min_floor, exclude the high side.
        The guards make it exclude NOBODY when there is no real separation (no
        attack) -- fixing the fixed-tau failure where attackers plateaued at 0.73
        below tau=0.85 and were never caught."""
        cand = [(i, self.suspicion(i)) for i in self.rounds
                if self.rounds[i] >= self.warmup and i not in self.excluded]
        if len(cand) < 3:
            return set()
        if not self.adaptive:
            return {i for i, s in cand if s > self.tau}
        vals = np.sort(np.array([s for _, s in cand]))
        gaps = np.diff(vals)
        if gaps.size == 0 or gaps.max() < self.min_gap:
            return set()                       # no clear separation -> exclude none
        split = vals[int(np.argmax(gaps))] + gaps.max() / 2.0
        if split < self.min_floor:
            return set()                       # separation too low to be attackers
        high = {i for i, s in cand if s > split}
        if len(high) > len(cand) // 2:         # attackers are a minority; refuse if not
            return set()
        return high


def defend_round(
    state: ReputationState,
    cluster_means: np.ndarray,
    clusters: list[list[int]],
    round_idx: int,
    ref: np.ndarray | None = None,
    probe=None,
    comp: bool = False,
) -> np.ndarray:
    """Score clusters, update suspicion, exclude, and return the round aggregate.
    `cluster_means` rows align with `clusters` (only non-excluded clusters passed).

    Flag test, in order of preference:
    - `probe`: server-side loss probe (Zeno-style) on its root dataset --- flag
      cluster j if applying its mean INCREASES root loss. Robust to non-IID
      decorrelation: a gamma-amplified ascent direction spikes the loss no matter
      whose data dominates the cluster sum, whereas the binary cosine test loses
      specificity when skewed honest clusters decorrelate from the anchor (we
      measured cosine flags at f=0.2 hitting clean clusters as often as dirty).
    - `ref`: trust-anchor direction (server root update); cosine < 0 flags.
      Without an anchor, direction flags are sign-ambiguous (a Krum reference
      locks onto the poisoned cloud in a large fraction of rounds).
    """
    scores: list[float] = []
    if probe is not None:
        for mean_j in cluster_means:
            scores.append(float(probe(mean_j)))          # delta root loss
        # relative-to-best rule: honest non-IID deltas can slightly raise loss on a
        # small balanced root set, so an absolute >0 test over-flags; poisoned
        # clusters spike loss far above the cleanest cluster instead
        best = min(scores)
        flagged = [j for j, s in enumerate(scores) if s > best + PROBE_MARGIN]
    else:
        if ref is None:
            # C3 TRUST-FREE reference (no root data): seed with the coordinate-wise
            # median of cluster means (robust to <50% contamination, so it points
            # the honest way whenever clean clusters are the majority), then refine
            # to the average of the means that AGREE with it in direction. This
            # beats a Krum reference, which locks onto the poisoned -h cloud.
            med = np.median(cluster_means, axis=0)
            nmed = med / (np.linalg.norm(med) + 1e-12)
            agree_cos = cluster_means @ nmed / (
                np.linalg.norm(cluster_means, axis=1) + 1e-12)
            agree = cluster_means[agree_cos > 0]
            ref = agree.mean(axis=0) if len(agree) else med
        norm_ref = np.linalg.norm(ref) + 1e-12
        for mean_j in cluster_means:
            cos = float(mean_j @ ref) / ((np.linalg.norm(mean_j) + 1e-12) * norm_ref)
            scores.append(cos)
        flagged = [j for j, s in enumerate(scores) if s < 0.0]
    state.last_info = {"flagged": list(flagged), "scores": scores}
    flagset = set(flagged)
    if comp:
        # HYBRID: per-round COMP decode over the overlapping groups. A client is
        # "suspected this round" iff EVERY group it belongs to is flagged (i.e. it
        # is in NO clean group) -- FedGT's one-shot elimination -- and we accumulate
        # that binary verdict across re-randomized rounds. One test per client per
        # round, but each test already fuses all `overlap` groups structurally.
        member_groups: dict[int, list[int]] = {}
        for j, cl in enumerate(clusters):
            for i in cl:
                member_groups.setdefault(i, []).append(j)
        for i, gs in member_groups.items():
            state.rounds[i] = state.rounds.get(i, 0) + 1
            if all(g in flagset for g in gs):
                state.flags[i] = state.flags.get(i, 0) + 1
    else:
        for j, cl in enumerate(clusters):
            for i in cl:
                state.rounds[i] = state.rounds.get(i, 0) + 1
                if j in flagset:
                    state.flags[i] = state.flags.get(i, 0) + 1
    if round_idx + 1 >= state.warmup:
        state.excluded |= state.exclude_now()
    keep = [j for j in range(len(clusters)) if j not in flagged]
    if not keep:  # pathological round: take the best-scored single cluster
        best_j = int(np.argmin(scores)) if scores else 0
        return cluster_means[best_j]
    return cluster_means[keep].mean(axis=0)
