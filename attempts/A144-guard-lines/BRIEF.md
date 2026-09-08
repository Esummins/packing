# A144 — guard-line rows: the "four chords on one line" cut as an LP row, with the pins' exact chords and the hypothesis square's minimum chord over its box (Opus; measurement, spec, Lean statement)

Context (2026-09-07 night). The PI, reading docs/shadows/a57v3/k5_11_interior_Y0147.svg (panel 1, the LP dual
support): "I can draw a horizontal line 0.99 units down from the top. That line crosses opposing sides of four
squares. Any realisation of that packing is at least side 4. We can create a set of guard lines — the orthogonal
lines from each pinned simple square — and use the conditioned hypothesis polygon as a square to check. This matters
where the LP is using the fact that the hypothesis square is shrunk to fit a full square on either side of it, where
the allowed rotations in the window prevent the hypothesis square from rotating out of the way."

The cut (n-general, sound for every packing): for any line ℓ inside the container [0, s]², the chords ℓ ∩ Q_i of
the squares of a packing are pairwise interior-disjoint sub-intervals of a segment of length ≤ s, so
Σ_i |ℓ ∩ Q_i| ≤ s. A chord through OPPOSITE sides of a unit square has length ≥ 1 (= 1/cos φ for tilt φ ≤ 45°); a
chord through adjacent sides can be shorter. As an LP row over placements p with weights x_p:
Σ_p |ℓ ∩ Q_p| · x_p ≤ s0 − Σ_pins |ℓ ∩ P| − minchord(H, ℓ), where the pins' chords are exactly 1 when ℓ runs through
the pin core's height range (at every pin position within tolerance; else the exact minimum over the pin's box), and
minchord(H, ℓ) = the minimum over the box of the hypothesis square's chord on ℓ (≥ the chord of K′(B) on ℓ, A132's
polygon core; exact in t = tan(θ/2)). The LP today has no such row: it treats H as its axis-aligned core (0.93 wide on
Y0147's window) and packs three unit chords beside it, and the frozen verifier's placement-exclusion test cannot see
a line either. Related: A121 validated the PI's `st4` readings (a stack of four ⇒ side ≥ 4) as re-solve kills; SLOT-
CROWD rows (A94/A109) are the other counting-row family (they charge slot occupancy; this charges length).

Read first: attempts/A57-shadow-trees/code/{caselp.py, lpbox.py} (how rows are generated and added: the covering
rows on grid cells, the K0/crowd row hooks — find where a NEW linear row over placements can be injected without
editing the drivers: a wrapper as A131/A135 did), A135's verify_case_v3.py + notes/spec.md (the extension pattern
that composes with the frozen verifier: what a certificate row must carry for the verifier to re-check it exactly),
A132's polycore.py (K′ vertices in t), A133's a133lib (exact cos/sin in t), A142's gallery142 data for Y0147 (the
support placements and the box), docs/shadows/a57v3/README.md's population (448 survivors), docs/budget.md §B.

## T1 — the row generator (exact)
`guardline.py`: for a node (pins with boxes, conditioned box B, side s0): the line family = horizontal and vertical
lines through each pin's edge heights/abscissae (the pin core's y0, y1, x0, x1), through K′(B)'s extreme y and x, and
through the midlines of both, plus the container-parallel lines at k·(1/8)·s0 (≤ 40 lines). For each line: the
pins' exact chord (interval over the pin box, take the minimum), minchord(H, ℓ) over B computed exactly (the chord of
a unit square at pose (c, θ) on a horizontal line at height y is piecewise-rational in t and y; minimise over the box
by the same corner/critical-point analysis A131 used for the four sinusoids; report it, and also the cheap lower
bound |ℓ ∩ K′(B)|, and which the row uses), and the placement coefficients |ℓ ∩ Q_p| for every column in the pool
(exact rationals). Sampled confirmation per node: 10⁴ poses of H in B → the true chord ≥ minchord in every draw
(drawn → tested → hits), and 10⁴ random packings' chord sums ≤ s0 is trivial but state it.

## T2 — the measurement
(a) Y0147 first: which line(s) the PI's reading corresponds to (0.99 below the top), the row's RHS, and the dual
support's chord sum on it (the violation); then the in-vitro re-solve with the guard-line rows added (240 s, 2
processes BelowNormal, exact cores per A135) → τ/η vs the stored record; certify if converged (frozen verifier: it
will FAIL because it cannot see the rows — record as "LP-dead under guard lines, certificate pending v3"; if the
exact-core + K′-pruned re-solve already kills without the rows, say so — A135's route). (b) Then 20 of the 448
survivors chosen by A142's ranking (top subtree cost) plus every node whose support violates some guard-line row
offline (compute the violation for all 448 first — that is minutes — and report the count and the distribution of
violation depth; the LP runs go to the deepest violations). Table: node × (max violation offline, τ before/after,
η, converged, kill). ≤ 4 CPU-h.

## T3 — verifier and Lean spec (write)
notes/spec.md: the certificate field `guardlines` (line: orientation + rational offset; RHS; per-column chord
coefficients recomputed by the verifier, never trusted), the v3 clause (the row is a valid inequality for every
packing consistent with the hypothesis, so the verifier's coverage check may subtract it — say exactly how it
composes with the existing rows and with A135's polycores clause), and the Lean statement: `chord_sum_le_side`
(disjoint interiors ⇒ chords are interior-disjoint intervals in [0, s] ⇒ Σ ≤ s) and `minchord_of_box` (the chord
lower bound over B from the vertex checks in t — A135's `checkVertexInPBox_sound` pattern), with the roster expected.
One paragraph on the n-general form (lines through every simple square's edges in every class; the same row family
kills "stack of ⌈√n⌉" configurations for every n).

Constraints: ≤ 2 processes, BLAS-pinned, BelowNormal, cap 4 CPU-h (A136/A140/A141 running; the PI is using the
machine; ≤ 16 python processes on the box); READ-ONLY on every campaign and attempt (new files only under attempts/
A144-guard-lines/); frozen verifiers byte-identical; honour A57's PAUSE via pausegate's scoped base; NO recursive
deletes; PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push own paths with explicit pathspecs. Drawing: Y0147's
page with the guard line drawn and the four chords labelled with their lengths (A142's format). Writes: the attempt
dir, docs/budget.md §D one row, attempts/A57-shadow-trees/notes/lemmas.md one section (LINE rows), registry row,
LOG.md. Report ONCE: T2's Y0147 result and the offline violation count first, the 20-node table second, T3 third,
pointers last. No interim messages.
