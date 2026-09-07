# A116 — method (what the code does and what was measured)

## Discipline

* ≤ 2 processes, BLAS-pinned (`code/blas1.py` copied from A111, imported before numpy through `a116lib`);
  the stability table ran alone first (2 min), then the two grid jobs (`run116.py S02`, `run116.py S07`),
  then `run116.py extras` and `consumer116.py`.  `PYTHONDONTWRITEBYTECODE=1`, no deletes.
* READ-ONLY on every campaign: A111's `a111lib` is imported (its IV / iv_cos / iv_sin / w_range and the
  shadow poses; its module-level `makedirs` hit existing directories only); A107's `shadow_nodes.json`
  and `extract.json` and A03's `trump11_float.json` are read; nothing outside this attempt, `docs/proofs/
  local_certificate.md`, `lean/depgraph.json` (one note), `LOG.md`, `attempts/REGISTRY.md` is written.
* Every verdict is checked by measurement (the A111 standing rule): a DEAD N is followed by ≥ 10⁴ uniform
  samples in N (each tested for being a packing of L ∪ P at 30 sides in [3.82, s0]; a hit would be a
  counterexample), by the box-constrained SLSQP minimum over N from 30 starts + the anchor (the measured
  chain minimum, an upper bound on the true minimum), and by the Trump canary (`a116lib.trump_in_N`:
  no D4 image of Trump's packing satisfies N's hypothesis — pins in their slack cores at ŝ AND one
  Trump square in every box).

## Objects (`code/a116lib.py`)

* **Bodies.** FREE body = a load-bearing square with a centre box [c ± r]² and a tilt interval
  [θ ± ρ] (cut by the Trump boundary where stated); PIN = a class pin with centre α + β s + (u, v),
  |u|, |v| ≤ h = δ/√2 (A57's slack cores, δ = 10⁻²), tilt exactly 0.  Walls are rows.  The anchor c is the
  shadow's pose DILATED to side s0 (c · s0/s*) for the tilted squares and the slot position at s0 for a
  load-bearing slot square that is not a pin (S02's BR(0,1) in the k5_11 frame); with anchor s* and r → 0
  the LP reproduces s* (the canaries: S02 3.886745, S07 3.885617 at r = 10⁻⁶).
* **Selections.** For a pair, the eight signed separating axes (owner, axis k, sign ε) with row
  ε (c_other − c_owner)·a_k(θ_owner) ≥ 1/2 + w(θ_owner − θ_other)/2, w = |cos| + |sin|.  Interval enclosure
  of the row over a cell (a111lib.IV, iv_cos, the exact w_range); a pair is FAR in a cell when one
  selection's gap is ≥ 0 on the whole cell (no row, no branch), NEAR otherwise, IMPOSSIBLE when no
  selection's gap reaches 0.
* **The relaxed LP over a tilt cell** (`Rows`): variables s, (x, y) per free body, (u, v) per pin, AND
  a tilt variable t per free body bounded by its cell.  Rows: walls x ≥ h(t), s − x ≥ h(t) with h relaxed
  to an affine LOWER bound over the cell (the chord of the concave piece; at an interior kink k·90° the
  two V-lines h ≥ (cos h′ ± (sin h′/h′)(t − k))/2, second-order loss); selection rows with p = ε d·a*,
  q = ε d·a*⊥ (a* the owner's axis at the cell midpoint, both affine in the LP variables): the exact
  ε d·a(θ) = p cos φ + q sin φ (φ = t_owner − θ*) is bounded above by (A) p + |q| sin(hw) with |q| by its
  chord over the q-range (tilt-free, exact for the worst φ), and (B) the two McCormick planes of q·φ on
  [q_lo, q_hi] × [−hw, hw] (+ hw³/6 for sin φ − φ), both with the correction max(0, −p_lo)(1 − cos hw);
  the support term w(t_owner − t_other) by its chord / V-lines.  Every relaxed row is IMPLIED by the true
  row for every configuration of the cell (Lemma RELAX in `docs/proofs/local_certificate.md`), so an
  infeasible / > s0 LP kills the cell.  Loss: second order in the cell width except the McCormick term,
  (q_hi − q_lo)·hw/2, which the tree halves by q-RANGE splits (an LP-level case split, sound).
* **The tree** (`Tree`): nodes = (tilt cell, partial selection, q-range splits).  Census → drop rows of
  far pairs, auto-fix pairs with one possible selection → relaxed LP → if value > s0 (or infeasible)
  the node is closed DEAD (its Farkas multipliers = the leaf certificate, re-derived as a float dual
  bound); else branch on a near pair (contact pairs first, fewest options) → at full selection: exact
  LPs at three common-offset tilt points (a witness if ≤ s0: the LP point is turned into poses and
  checked as a packing of L ∪ P — LIVE-LOW), else refine (bisect the weighted-widest tilt cell, or halve
  the q-range of the row with the dominant McCormick loss once cells are ≤ 1°) down to 0.05° (UNRESOLVED
  below that).  Verdict DEAD iff no LIVE-LOW and no UNRESOLVED.  Phase 2 re-opens closed leaves with
  value < s0 + 0.9 (s* − s0) and refines them (4 000-node budget) so the certified minimum over the final
  cover is within 10 % of the measured chain minimum.
* **Stability radii** (`stability116.py`): at the exact minimum, every pair of L ∪ P: contact type
  (vertex-on-edge / flush), the riding vertex's tangential coordinate τ on the owner's edge, its slack
  1/2 − |τ| to the nearer end (flush: the overlap length), the relative-tilt margin to a multiple of
  90°, the first-order estimate slack/drift, and the RIGOROUS forced radius: the largest δ (ρ = κδ,
  κ = 100°/unit or κ = 0) at which interval bisection over the pair's 6-D pose box proves "every
  interior-disjoint configuration satisfies the minimum's selection" (a sub-box is cleared when the
  selection holds throughout, or when every other selection is impossible on it); for non-contact
  pairs the far radius.  Tables in `notes/stability_table.md`, data in `results/stability.json`.
* **The consumer** (`consumer116.py`): A107's alive-node supports (11-square representatives at s0,
  canonicalised into the shadow frame by A107's struct_op) tested for an injection of N's boxes into
  distinct support squares; counts per certified N and the distance census.

## Grid

r ∈ {0.02, 0.05, 0.1, 0.2, 0.3} × ρ ∈ {2°, 5°, 10°, 20°, 40°}; S02 in the k5_11 frame with L = {f1, f2,
f3, BR(0,1)}; S07 in the trump5 frame with L = {f0, f2, f4} (the x-chain; f1 is not needed because
Λ ≥ s* on every tilt) and the tilt boxes of f0, f2, f4 cut at 41.565° (A110's grain boundary) — plus the
uncut runs (Trump inside from ρ ≥ 4.82°) and the cut at θ_T + 0.02° (F_T = s0 at θ_T + 6·10⁻⁵ °).
Extras: exact pins (h = 0), the k5_16 frame, S07 with f1, the PI-route N (δ = min forced radius),
S02 with the upper cut at 49.80° (D = s0 at 49.818° = 90° − θ_T).  Time cap 900 s per run.
