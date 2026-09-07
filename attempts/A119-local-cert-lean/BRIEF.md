# A119 — the local certificate as a frozen object: rational Farkas certificates, Lean file, blocking squares as boxes (Opus, engineering + Lean)

Context (2026-09-07). A116 (`74a34f96`, docs/proofs/local_certificate.md) proved Theorem LOCAL and certified
neighbourhoods of the S02 and S07 minima twenty times wider than A111's: S02 (k5_11 frame, L = f1 f2 f3 BR(0,1)) dead
at (r, ρ) = (0.2, 10°) and (0.05, 20°); S07 (trump5 frame, L = f0 f2 f4, cut at F_T(θ) > s0, i.e. θ > θ_T + 6·10⁻⁵°)
dead at (0.1, 40°) and (0.2, 10°); every certified N confirmed by 10⁴ samples with Trump outside. Consumer: 72 of 184
k5_11 and 23 of 68 k5_16 S02-explained alive nodes have their support inside a certified N. What is still open, and
this attempt's job: (1) the leaf certificates are float Farkas multipliers over second-order affine relaxations per
tilt cell — they need RATIONAL Farkas vectors checked exactly and a Lean file (§8 of local_certificate.md: linarith
per cell, finite case split via CaseSat, COVER as a Finset case split); (2) the limiter at r = 0.3 is a genuine
rearrangement of L ∪ P that the DROPPED squares would block (S02: BR(0,1) leaves its slot and f3 climbs onto it at
3.8733; S07: the ladder shears at 3.856) — adding the blocking squares as boxes (with_f0_TR for S02 dead at (0.1, 5°)
in A116's trial, ×10 nodes) extends the radius; (3) for ρ ≥ 20° at r ≥ 0.1 the tilt-cell count hits the 900 s cap — a
census/LP that shares cells across leaves would remove it.

Read first: docs/proofs/local_certificate.md (all; §8 Lean shape), attempts/A116-local-selection-tree/{code/
a116lib.py, run116.py, stability116.py, consumer116.py; notes/{method,t2_table,stability_table}.md; results/
t2_*.jsonl, stability.json, t3_consumer.json}, lean/PackingCertMathlib/PackingCertMathlib/{CaseSat,Selection,
Composition}.lean and lean/gen_crowd_lean.py (the pattern for generating a Lean file from a certificate: A93),
attempts/A117-verifier-v2/ (running in parallel: NO-families in verify_param_v2 and Lemma TC as a leaf — coordinate by
reading its notes; do not edit its files), attempts/A112-dual-branching/code/regiontree.py (the consumer: the YES
leaf of the region tree), attempts/A96-a57-parametric/code/regionopt96.py.

## T1 — exact certificates
For every certified N in A116's t2 tables (S02 at (0.2, 10°), (0.05, 20°), (0.1, 10°); S07 at (0.1, 40°), (0.2, 10°)
with the cut): re-derive each closed leaf's Farkas multipliers as rationals (LP with exact re-check: yᵀA = 0 on the
variable block, yᵀb < 0, all in ℚ, with the relaxation's constants (chord bounds, w_min, h_min) computed as exact
rational lower/upper bounds from interval arithmetic), and write the certificate file: the tilt-cell cover (an
explicit finite list, checked to cover the product of tilt intervals), per cell the selection case split and the
rational Farkas vector per leaf, the cut inequality, and the sha256. A checker `check_local.py` (new file; pure
rational arithmetic, no floats in the decision path) verifies a certificate file independently of the generator.
Report: cells, leaves, checker wall per N.

## T2 — the Lean file
Generate `Local.lean` per the §8 shape: COVER as a finite case split over the selections (each case a `sat_squares`
instance — reuse CaseSat's separation predicate), LEAF as `linarith` from the summed axis rows per tilt cell with
the rational Farkas multipliers as explicit coefficients, the relaxation constants as proved bounds (the
trigonometric chord/V-line inequalities on an interval — state and prove once as lemmas, `nlinarith` after the
quadrant split, or leave [C] with the exact statement if they do not close in a day), and Theorem LOCAL's
composition into a `ClassKilledAt`-shaped clause on the hypothesis "pins + boxes for L (+ blocking boxes) + cut".
`lake build` must be clean; report the axiom count and any sorry with its exact statement.

## T3 — blocking squares and the radius
Add the blocking squares of A116's limiter cases as boxes (S02: TR(0,0) and f0; S07: f1, f3, BL(0,2)) and re-certify at
r ∈ {0.2, 0.3, 0.4}, ρ ∈ {10°, 20°}; report the new largest certified N per shadow, the node count, and the new limiter
(a further rearrangement, or the tilt-cell cap). For the ρ ≥ 20° cap: implement cell sharing across leaves (one tilt
cell census per N, leaves reference cells) or an LP over the cell union, and report the wall at (0.2, 20°) and
(0.2, 40°). Then re-run A116's consumer count: how many S02/S07-explained alive nodes (A57 and A60) have their
support inside the new N.

Constraints: engineering + Lean; ≤ 2 processes, BLAS-pinned, headroom gates (A114, A115, A117, A118, A96 arms, A61 on
the box); READ-ONLY on every campaign and on A116/A117 files (new files only, under this attempt and lean/); frozen
verifiers untouched; NO recursive deletes, PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push own paths (no
rebase/autostash/reset). Writes: attempts/A119-local-cert-lean/{code,results,certs,notes,logs}, lean/PackingCertMathlib/
PackingCertMathlib/Local.lean (+ any lemma file), depgraph note on the GRAIN node (owner A119), registry row, LOG.md.
Report ONCE: T3's largest certified N per shadow and the consumer count first, T2's Lean status (axioms/sorries)
second, T1's certificate sizes third, pointers last. No interim messages.
