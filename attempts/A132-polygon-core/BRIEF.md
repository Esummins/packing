# A132 — the polygon core: replace the axis-aligned inscribed core by the exact intersection of the hypothesis square over its box (Opus; measurement, in-vitro LP, verifier/Lean spec)

Context (2026-09-07). The PI, reading docs/residue_map/a57_lp_support.svg (k5_11_interior_Y0186_D00_D00), noticed the
LP's top-wall support column "intrudes deeply into all hypothesis squares". Checked exactly by the coordinator on the
four alive level-3 nodes of A57 (Y0186_D00_D00, Y0036_D07_D00/D04/D05; results/tree/*/<id>.json, field `packing` =
the dual-support placements with weight y; `hyp.cores[-1]` = the conditioned square: box + axis-aligned core of
half-side a ≈ 0.46 from pinguard's tight core): in EVERY one of the four nodes, two of the 5–8 support columns
(weights 0.5–1.0) overlap the hypothesis square at EVERY pose (centre in the box × tilt in the bin; 9³ pose grid,
SAT gap max over poses −0.005 to −0.029) while clearing the AXIS-ALIGNED core by +0.003 to +0.045. The reason is
geometric: the core lemma (T5 / `core_meet_same_square`, Lean) says a square at any pose in the box CONTAINS the
axis-aligned square K(a); for a bin centred at 75° (or 87°, 49°) the tilted square protrudes up to ~0.21 beyond K(a)
along each diagonal, and the LP's column pool is pruned only against K(a). The support of every alive node examined
sums to exactly the budget on columns that cannot exist under the node's own hypothesis.

The lever — POLYGON CORE. For a box B = [x0,x1]×[y0,y1]×[θ0,θ1], let K′(B) = ⋂ over poses (c, θ) ∈ B of the unit
square Q(c, θ): a convex polygon (intersection of convex sets), for narrow bins nearly the whole tilted square. Every
pose in B contains K′(B) — the same statement as the core lemma with K(a) replaced by K′ (K(a) ⊆ K′ always). Uses:
(1) COLUMN PRUNING: any placement whose square meets the interior of K′ is impossible under the hypothesis; (2) the
CERTIFICATE hypothesis: the verifier may exclude such placements from the coverage rows (the frozen verify_case /
verify_param know only K(a): this needs a v2-style extension, as verify_param_v2 did for NO-families); (3) the T5
LOGIC KILL: "K′ meets a pin core" kills the node outright (stronger than "K(a) meets pin core"; should reproduce A96's
T5″ empties, e.g. the 57 queued ALIVE nodes with surviving 0.0 in attempts/A96-a57-parametric/results/trim96.json,
and more). Certification of K′: it suffices that each VERTEX v of a candidate polygon lies in Q(c, θ) for all (c, θ)
∈ B — i.e. |R(−θ)(v − c)|_∞ ≤ 1/2 over the box, an interval computation (pinguard.py's tight_a formula is this check
for the four vertices of K(a)); so K′ may be computed numerically (clip the square over a pose grid), shrunk by a
hair, and then certified vertex by vertex exactly in rationals. The Lean lemma is the core lemma with a polygon:
`polycore_meet_same_square`, hypotheses = the vertex checks. n-general: applies to every conditioning tree
(A57, the protected tier's trees, k0's tree) — everywhere a box hypothesis is used.

Related, running: A131 (pin-clip: shrink the CENTRE BOX to the pin-feasible region — the dual move: pins vs the box;
read its brief; coordinate by reading, never by writing into its files). Read first: attempts/A57-shadow-trees/code/
{pinguard.py, caselp.py, lpbox.py (where the column pool is pruned against the cores — find the exact test), tree57.py
(read-only)}, docs/proofs (the core lemma: search known_results.md for T5 / core_meet_same_square and the Lean file
lean/PackingCertMathlib/PackingCertMathlib/ that proves it), attempts/A96-a57-parametric/code/verify_param_v2.py and
notes (the extension pattern + how it was Lean-proved), attempts/A96-a57-parametric/results/trim96.json (T5″ table),
attempts/A124-recheck-day/ (recheck96's node path — reuse it for T2), docs/budget.md §B–D.

## T1 — measurement over every alive node (offline, minutes to an hour)
`polycore.py`: for a box, compute K′(B) (clip Q over a fine pose grid, then shrink by 1e-6 and certify each vertex
exactly with the interval formula; report area(K′) vs area(K(a)) = (2a)²). Over ALL alive nodes of A57 (the 383 in the
re-check queue; both classes; every level) and A60's alive nodes if the record format allows: (i) how many DUAL-
SUPPORT columns (`packing`) meet K′ but not K(a), and the weight they carry vs the node's τ − (budget − 1) slack (a
crude "would it die" indicator: if removing them takes the support's weight below budget); (ii) how many columns of the
FULL pool (`atoms_all`, if stored) meet K′ but not K(a); (iii) the T5-polygon logic test: K′ meets some pin core →
node dead by logic (list them; compare with trim96's surviving = 0.0 set). Table by class × level, and the fraction of
nodes where (i) removes weight ≥ the slack.

## T2 — in-vitro LP (≤ 6 CPU-h, 2 processes BelowNormal, honour A57's PAUSE sentinel; recheck96's node path; no
shard launch)
Ten alive nodes (the four L3 above + six with the largest (i) weight at L1/L2, both classes): re-solve the node LP
with the column pool pruned by K′ instead of K(a) (same budget, same rows, 240 s; then the 900 s continuation only if
η is within 1e-3 of zero) and report τ/η/minmass against the stored record. This is the honest test; the LP kill is
NOT a certificate until T3's verifier exists — record it as "LP-dead under polygon core, certificate pending".

## T3 — the verifier and Lean spec (write, do not deploy)
notes/spec.md: the certificate field (`polycore`: list of rational vertices per conditioned core, with the interval
checks as the verifier's first step), the verifier change (rational polygon–square SAT in the placement-exclusion
test; everything else unchanged; how verify_param_v2's NO-family clause composed with the frozen core and how this
composes the same way), the Lean lemma statement (`polycore_meet_same_square`: from the vertex checks, every pose in
B contains K′; from disjoint interiors, no other square meets int K′) and where it slots in the roster (docs/
known_results.md T5 line; lean/…/Composition.lean). Size the implementation (lines, days) and the re-verification
cost of the existing tree (none: old certificates stay valid; new ones are strictly stronger).

## T4 — verdict for the budget
One paragraph for docs/budget.md §D: measured column-kill fraction, T2's kill count out of ten, the projected effect on
the A57 row IF the T2 rate holds across the 383 (state the assumption), the same for the protected tier (same box/pin
geometry), and the verifier/Lean cost. Also one line on how the polygon core interacts with A131's pin-clip (they
compose: clip the box, then take K′ of the clipped box).

Constraints: ≤ 2 processes, BLAS-pinned, BelowNormal (A124/A125/A126/A129/A130/A131 running; the PI is using the
machine); READ-ONLY on every campaign and driver (new files only under attempts/A132-polygon-core/); frozen verifiers
byte-identical (the spec describes a v3, it does not touch v1/v2); never launch a shard; NO recursive deletes; never
delete a pidfile; PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push own paths (no rebase/autostash/reset).
Every geometric count confirmed by sampling reported as drawn → tested → hits (e.g. 10⁴ poses in B all contain each K′
vertex). Drawings (if any): hypothesis square at the box centre and mid-tilt, cyan H; K′ drawn as a polygon inside it;
the offending columns hatched. Writes: attempts/A132-polygon-core/{code,notes,results,logs}, docs/budget.md §D one row,
attempts/A57-shadow-trees/notes/lemmas.md one section (T5-poly), registry row, LOG.md. Report ONCE: T1's table first,
T2's ten nodes second, T3/T4 third, pointers last. No interim messages.
