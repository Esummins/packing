# A116 — the local certificate: a selection tree around a known minimum that kills a neighbourhood of radius ~0.1, not 0.01 (Fable lead, theory + implementation)

Context (2026-09-06, PI). The cost of every search near a solution scales like a power of 1/(s* − s) (docs/budget.md
§E): that is the exponential, and the only way to cut into it is a better bottom-up method — a fast, sound way to
certify a LOCAL domain of phase space starting from a known minimum. The pieces exist and were each found narrow for
a diagnosable reason:

* A63's tube around Trump: rBasin = 3/2000 (Hessian ball; slack → 0 at Trump).
* A106's basin ball around S02: radius 0.035 = √(slack/H̄) (Hessian; no open box contains the shadow).
* A110's chain menu: INSIDE a grain (fixed load path) the side is a closed-form function of the tilts — Λ(θ) =
  2 + 4u/(u² + 1), Y, D, F_T with u = cos θ + sin θ — and every one of those formulas stays ≥ 2 + 4√2/3 > s0 on the
  whole tilt range except the gap chain F_T, which falls to ŝ only inside Trump's grain (boundary at 41.565°). So
  within a grain the kill is total in tilt; the question is only what happens when a load-path contact opens.
* A111's Farkas leaf (attempts/A111-loadpath-branch/notes/leaf_shape.md O1–O4) is the right object and came out with
  radius r < s* − s0 (0.0097) for three diagnosable reasons: (i) AMBIGUOUS pairs in the selection census were dropped
  ("or drop the row") instead of case-split, so the leaf lost exactly the rows that carry the chain when a contact
  is near opening; (ii) the boxes were anchored at the shadow's own coordinates at side s*, and the node sits at s0,
  so a frame slack of s* − s0 had to be absorbed by the radius — anchoring in the node's frame at s0 removes it;
  (iii) O3's affine relaxation uses chord bounds R·Δ over the whole tilt cell, which is loose unless the tilt cells
  are small. None of these is structural.

Read first: leaf_shape.md (all), A111's results/t1_octagon.jsonl and t1_radius.jsonl (what was forced at which
radius), docs/proofs/grain_flood.md §1–§2 (GRAIN-LP: at fixed tilts and fixed selection the side minimum is an LP
whose dual is a balanced force system = the load path; INHERIT; CONT), docs/shadows.md §S02/§S07 with their contact
graphs and Fritz-John multipliers, attempts/A108-s07-certify/results/contacts.json, docs/residue_map/
gen_pinwheel_k7.py + gen_pinwheel_tilt.py, docs/proofs/ A63's tube documents (grep rBasin, InStratum, ThetaT, tube),
lean/PackingCertMathlib/PackingCertMathlib/{CaseSat,Selection,Composition}.lean (the separating-axis and selection
conventions the Lean side already has).

## T1 — Theorem LOCAL (the selection tree around a minimum)
State and prove: let z* be a packing (a local minimum of the side in its class, or any configuration) with
load-bearing squares L, class pins P, and let N = ∏_{n∈L} ([c_n ± r] × [θ_n ± ρ]) in the CLASS's frame at side s0
(anchor at s0, not s*). For each pair of bodies in L ∪ P ∪ walls that can come within contact distance anywhere in N
("near pairs"; far pairs are separated by every axis and need no branch), the eight signed separating-axis
selections partition the disjoint configurations; the selection tree over near pairs has finitely many leaves
(bound it: 8^k with k near pairs, and show most are IMPOSSIBLE by interval arithmetic so the live count is ~2^k);
at each leaf, GRAIN-LP gives min side = the chain length for that selection, a closed-form function of the tilts
(the menu, extended to whatever chains the leaf's selection realises); the leaf is dead iff that minimum over the
leaf's tilt cell exceeds s0. Then: **N is dead iff every live leaf's chain minimum exceeds s0** — with no
dependence on the other squares of the packing (dropping them only weakens the hypothesis). State it n-general.
Prove the two lemmas it needs: LEAF (fixed selection ⇒ side ≥ chain(tilts), the pairwise separating-axis inequalities
summed along the chain) and COVER (the selections cover all disjoint configurations of the near pairs). Say exactly
where the chain formula can dip below s0 inside N: only where a leaf's selection realises the gap chain F_T with a
tilt inside Trump's range — i.e. N must be cut at the Trump boundary, and that cut is a single inequality
(sin θ cos θ = 2 cos θ − 1 at 41.565° for S07's family; give S02's if any).

## T2 — implement and measure the radius
Implement the selection tree (reuse A111's a111lib.IV, iv_gap_axis, w_range; case-split AMBIGUOUS pairs instead of
dropping them; anchor at s0; tilt cells bisected until O3's relaxation is within 10% of the exact chain formula) and
run it on S02 (k5_11 frame) and S07 (trump5 frame, cut at the Trump boundary) at r ∈ {0.02, 0.05, 0.1, 0.2, 0.3},
ρ ∈ {2°, 5°, 10°, 20°, 40°}. Report per (r, ρ): near pairs, leaves (total / IMPOSSIBLE / live), live-leaf chain minima
(smallest), verdict, wall time; the largest certified (r, ρ); and what limits it (a leaf whose chain dips below s0 —
which chain, which selection, is it the Trump boundary — or the leaf count). Dense sampling (≥ 10⁴ configurations in
N) must confirm every certified N: no sampled configuration with all near pairs disjoint has side ≤ s0 (side computed
exactly from the poses). Canaries: Trump itself must be OUTSIDE every certified N for S07 (it is inside the box at
ρ ≥ 4.82°, r ≥ 0.033, so the cut must exclude it); S02's N at r = 0 must be dead with min 3.886746030.

## T3 — the consumer and the price
If the radius reaches ~0.1 in position and ≥ 10° in tilt: (a) the YES leaf of A112's region tree becomes N (state the
sound node cut: hypotheses = class pins + boxes for L; the certificate = the selection tree's leaf list with each
leaf's Farkas/chain certificate; Lean shape against Selection.lean / CaseSat.lean — the leaf is `linarith` on the
summed axis inequalities per tilt cell, and COVER is a finite case split); (b) count how many of A57's/A60's alive
nodes (A107's shadow_nodes.json, A111's t3_logickills.json) have their load-path support inside a certified N and
would die at the YES side; (c) the price of the certificate (seconds per N) against the tree's cost for the same
nodes. If the radius stays small, say which of (i)–(iii) still limits it and what would remove it.

Constraints: theory + ≤ 2 processes, BLAS-pinned, pure geometry/LP over a handful of squares (seconds each), headroom
> 6 GB commit and > 3 GB free physical (A112, A114, A115, A96 arms and A61 are on the box); READ-ONLY on every
campaign and every other attempt; frozen verifiers untouched; NO recursive deletes (rm -r / Remove-Item -Recurse /
shutil.rmtree) — PYTHONDONTWRITEBYTECODE=1, leave scratch files; git = fetch + plain merge + push own paths (no
rebase/autostash/reset). Every geometric count confirmed by ≥ 10⁴ sampled configurations before it is reported.
Writes: attempts/A116-local-selection-tree/{notes,code,results,logs}, docs/proofs/local_certificate.md, depgraph note
on the GRAIN node (owner A116), registry row, LOG.md. Report ONCE: T2's largest certified (r, ρ) per shadow and the
limiter first, Theorem LOCAL and its lemmas second, T3 counts and price third, pointers last. No waiting-state
messages.
