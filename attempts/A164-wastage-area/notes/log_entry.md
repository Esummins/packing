## 2026-09-08 — A164-wastage-area (Opus engineer) — done-negative

**The leaf.** The PI's wastage argument on the k0 cell `l1_104` (H at x 2.4626–2.5674, y 2.1482–2.2530,
tilt 30–45°) made into a general, LP-free leaf. For a node whose hypothesis boxes carry cores
K_j ⊆ every pose of the box (A135 exact for a pin, A132 polycore K′ for a conditioned square), let

  U(node) = { p ∈ [0, m]² : NO admissible square contains p },

admissible for a FREE square = inside the container and interior-disjoint from every core; a
hypothesis square's own cover is the union of its poses over its box. **Leaf WASTE [T]:
|U| ≤ m² − 11, so |U| > m² − 11 kills the node with no LP** — each of the eleven squares lies in its
own coverable set and the interiors are disjoint, so 11 = |⋃ Q_i| ≤ m² − |U|. That is A89's Lemma ID
(`docs/proofs/tilt_floor_k0.md` §7) with the corner box removed: Lemma ID is the case where the
charged region is certified by a HYPOTHESIS (shallowness) rather than by GEOMETRY, and the region no
longer has to be a corner box or even connected. Budget B₀ = s₀² − 11 = 4.031780343056, the largest
E(m) on the window slab; the window is covered by inflating only the COVER square to
λ_max = s₀/3.81794 while admissibility stays at side 1 (a λ-admissible square contains the concentric
admissible unit square), so one s₀-frame raster kills the whole slab.

**Verdict: sound, cheap, and it fires on nothing.** 0 kills over all 71 alive gallery nodes (the 11
converged-alive pin-free k0v4 cells and the 60 `docs/shadows/a57v4/` pages), pitch 0.01 × 36 tilt
bins, 8–18 s per node for the whole certificate. |U|/B₀: min 0.00 %, q1 11.75 %, **median 18.56 %**,
q3 23.48 %, **max 42.18 %**; means 3.18 % (k0, 0 pins, budget 10), 19.47 % (A57, 5 pins), 21.20 %
(A60). Refined at pitch 0.005 × 90 bins on the extremes: `f1_L10_0003` (7 boxes) |U| = **1.8969 =
47.05 % of B₀** (window-sound at λ_max 1.8084 = 44.85 %), `k5_11_interior_Y0738` 1.4261 = 35.37 %
(window 1.3271), `l1_104` 0.1290 = 3.20 % (window 0.1152). The best node in the population is short
of the leaf by a factor of 2.1.

**The sharpest measurement: the corner column is ZERO on all 71 nodes.** No corner unit box is ever
certified unreachable, so **Lemma ID's charged region is empty on the whole alive population — not
small, empty** — and 64–100 % of the certified waste is in the four WALL STRIPS, the rest in the
interior. The shallow-corner route of §7 has no consumer at this frontier.

**l1_104: the PI's location is right, the count is not.** All 0.129 units of certified waste sit in
the EAST wall strip — the wedge between K′(H) and x = s₀ that A148's page already flags as the node's
one sub-unit pocket (H → wall x = s, 0.828); the figure shows it as a triangular sliver pointing at
the core. What fails is "only one square's centre can sit near the right wall": unconditionally the
outer admissible-centre mask admits **seven** 1-separated centres in x ≥ s₀ − ½ and **eight** in
x ≥ s₀ − 1 (disk bound and a 0.7-cell cover bound agree to within one). The counting hypothesis that
would give the "one" — K0-FREE′, every corner box doubly met, so eight squares corner-committed — was
measured too and is **vacuous as an area row**: a corner-committed square's centre is within √2/2 of
its box and covers √2/2 further, so the four corner reach-envelopes leave only **0.0166** of the
container uncovered on `l1_104` (max 0.248 over the eleven cells) against the 2 + B₀ = 6.03 the row
needs. Wastage is a LOCATION diagnostic, not a kill; the counted version needs A141's lane counts /
A153's cover number, because B₀ = 4.03 of 15.03 is too large a fraction of the container for a 1–2
unit sliver to reach.

**Soundness and controls.** A raster cell is counted only when NO admissible pose MEETS the CLOSED
cell — never "the centre is not covered" — so the mask is an INNER approximation of U and the area is
a LOWER bound. Two Lipschitz facts do all the work (the same two A148's pages rely on): clearance is
1-Lipschitz in the centre and (√2/2)-Lipschitz in the tilt. Per tilt bin the admissible-centre set is
over-approximated on a grid in the bin's own ROTATED frame (where the square is axis-aligned) and the
cover is a separable binary dilation by a box of half-width λ/2 + λ(√2/2)(dθ/2) + q/2 + p√2/2; each
hypothesis box's own cover is an exact rect-vs-rotated-square SAT gap against a margin. Controls:
7.1 M poses drawn over the population, **1 223 887 certified admissible by an independent SAT pass,
976 134 carried through the containment test, 0 hits**; and an independent checker (`verify164.py` —
its own separating-axis test, its own dense sweep over the region a meeting square's centre can
occupy, no code shared with the dilation or with A132's `poly_square_depth`) confirmed five masks
cell by cell — `l1_104`, `l1_158`, `l2_p114_001`, `k5_11_interior_Y0738`, `f1_L10_0003` — with
4.6–7.1 M meeting poses tested per node and **0 admissible meeters**.

**Two bugs found and fixed mid-attempt, both in the diagnostics, neither touching |U|.** (i) The
conditional crowd row computed n_loose = 11 − 4·n_per_corner − n_boxes without checking the sign and
so flagged spurious CROWD-KILLs on pinned nodes (n_loose = −3 on `k5_16_interior_Y1117`): the
hypothesis K0-FREE′ is only stated for a pin-free node and is now refused elsewhere. (ii) The outer
admissible-centre mask was read at the nearest rotated node with NO dilation, where the chain
cell-centre → cell → nearest node needs radius 2; fixed, and the k0 and A57 populations were re-run
so every stored row comes from the same code.

**Lean shape.** `waste_kill (N) (m) (R : Finset Cell) (hR : ∀ C ∈ R, RasterCert N m C)
(hgt : R.card * pitch² > m² − 11) : ∀ P : Packing 11 m, ¬ P.Consistent N`, with four named
obligations: **W1** measure (eleven pairwise interior-disjoint unit squares cover exactly 11), **W2**
core transfer (K_j ⊆ Q_j and disjoint interiors ⇒ a free square is disjoint from the core — where
A132/A135's certified cores enter, one line), **W3** raster soundness (the two Lipschitz lemmas plus
the window/dilation bookkeeping — the only analytic content, and the only place the pitch, the tilt
count and the margins appear; **not written**), **W4** window transport (same bookkeeping as
K0-WIDEN / Lemma B). Zero new axioms if W1–W4 are proved; one (W3) if the Lipschitz reduction is
assumed, which is the axiom A148's pages already lean on informally — so writing W3 pays for both.

**Reading.** An area budget cannot carry a packing argument at this side. E(m) = m² − 11 is 27 % of
the container, and the single-square uncoverable set is the wrong object to charge against it: with
at most seven small cores in a 3.877-side box almost every point lies inside SOME admissible unit
square. What the leaf is good for is telling you WHERE the slack is (wall strips, never corners) and
at what depth an area argument could start to bite — |U| scales with the box count (0.128 at 1 box,
0.793 at 6, 1.701 at 7), so the first fire is at 9–10 boxes, i.e. 1–2 free squares left, where the
LP is already cheap. That is the honest reason the leaf has no consumer.

**Files.** `attempts/A164-wastage-area/` (`BRIEF.md`; `code/{geo164,run164,fig164,verify164,
replot164,summarise164}.py`; `results/{summary164.txt,summary164.csv,u164_*.jsonl,mask_*.npz,
verify164_*.json}`; `figs/{l1_104_U.svg,f1_L10_0003_U.svg}`; `notes/{leaf.md,doc_lines.md,
log_entry.md,registry_row.md}`; `logs/`), plus the registry row, this entry,
`docs/residue_ledger.md` §6.3 and one paragraph in `docs/budget.md` §D item 1. Two BelowNormal
processes at affinity `0xFFFF`, the 16-process box ceiling polled before every launch (the box ran
7–19 other lab pythons throughout, so the sweeps were serialised); **3 212 s of measured run164 time plus ~1 000 s of independent checking and ~600 s in a first, too-slow checker that was killed = ≈ 1.35 CPU-h of the 3 CPU-h cap.**
READ-ONLY on every campaign and on A89/A115/A132/A135/A140/A141/A148 — `geo148.obstacles_of` is
imported, not copied, so the two attempts cannot drift apart.
