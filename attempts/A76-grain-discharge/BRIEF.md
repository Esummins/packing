# A76 — bottom-up: enumerate + discharge the grains adjacent to Trump on the protected strata (Fable lead)

You are the THEORY lead (Fable). PI direction: the top-down pair-LP stalls with asymptotic
difficulty AT Trump (the ghost-saturation mechanism, A65/A66/A71/A73/A74). Invert it: grow the
certified region OUTWARD from the basin, grain by grain, on the remaining protected strata —
where rigidity-type certificates get EASIER near Trump. Deliver a certified radius R > rBasin
within which no exact-protected-class packing has sigma <= s-hat, and hand R to A74 as an
enlarged basin-exclusion row (Lemma P-B with rBasin -> R). A74 owns corners4 emission — do
NOT collide with its files/slots; you SUPPLY R, it consumes it.

Read first: docs/proofs/{unique_transfer,h10_stuck,pair_kill,closed_disjoint_bridge,
theta_t_transfer,drain_lemma,structure_lemmas}.md; attempts/A65-low-k-closure/results/
crowdfam.json (every feasible family is a Trump-image perturbation — your alive-grain census
seed); attempts/A22-local-rigidity/ + attempts/A70-lean-wave4/code/a22_recheck_exact.py (exact-
rational Krawczyk = your rigid-grain discharge tool); attempts/A30-t3-pilot/t3lib.py + drain
v3 (flexible-grain tools); attempts/A44 (index identity m = 3k+1+sigma-d, rigid => Maxwell:
the rigid/flexible classifier); attempts/A31-structure-count/code/lib0.py (validated contact-
structure filters: tilt propagation, rotation systems — reuse LOCALLY); attempts/A37-cp-atlas
+ A51 (THE ATLAS LESSON: a searched enumeration was incomplete — your completeness must be BY
CONSTRUCTION).

## T1 — local completeness (the lemma that makes this sound)
Lemma G-R: for R below a computable threshold, every packing within distance R (t-coords, mod
G, per E.COORD) of a Trump image g*zhat has contact graph among an explicitly enumerated finite
set G(R) — because only square pairs whose Trump-frame separation is < 2R + contact tolerance
can touch, and container contacts are similarly bounded. Prove it at drain-v3 rigor; the
enumeration is exhaustive by construction, not search. Then intersect with each protected
stratum's pins (k4_08, k4_11, k4_03, corners4 first; then the rest of the k<=4 / k<=3 tier)
and with the EXACT-stratum hypothesis (no 5th simple square — B.EXACT bridge): G_S(R) per
class. Report |G_S(R)| vs R — if it explodes before R is useful, that is the finding.

## T2 — discharge each grain
Classify by A44 index counting: RIGID grains -> exact-rational Krawczyk (A70 rung-(a) style):
either no real solution, or an isolated CP with sigma > s-hat (certified sign), or = a Trump
image (the canary — must appear exactly once per stratum that contains Trump, i.e. NEVER in an
exact-k4 class). FLEXIBLE grains -> drain (drain lemma v3: a slack direction strictly decreasing
sigma or creating a contact, i.e. the grain drains to a neighbour) or FJ/Farkas exclusion
(t3lib, exact duals). Every discharge = an exact certificate in certs/ with a stdlib checker +
corruption gates (new files only; imitate verify_sturm/verify_cidl style). Composition lemma:
G(R) exhaustive + every grain discharged/drains-to-discharged => no exact-protected packing
with sigma <= s-hat within R. Trump canary at every step.

## T3 — hand R to the LP
Write the enlarged Lemma P-B(R) (docs/proofs/pair_kill.md addendum): the basin-exclusion row
with radius R, its exact-stratum scoping, and the shell bound (pin drift + sqrt2-weighted zone
drift must fit R — A66's constraint, now with R instead of 3/2000). Send A74 the certified R
+ row form via the advisor (report it; do not edit A74's files). Measure on k4_08 with your own
<= 2 LP slots if A74 is busy: margin vs R.

## Constraints / deliverables
<= 2 LP/compute slots, BLAS-pinned, headroom > 6 GB; A57/A60/A61/A74 untouched; frozen
verifiers untouched; depgraph shared (pull/merge; add note on C.K4TIER: "A76 bottom-up radius
R = ..."; owner chip stays A74 — you are the complementary front). Deliverables: docs/proofs/
grain_discharge.md (G-R + composition), certs/grain_* + checkers, per-class |G_S(R)| table +
discharge ledger + certified R, P-B(R) addendum, registry row, LOG.md, notes/findings.md.
Honest walls with size laws are successes: if |G_S(R)| explodes or flexible grains resist FJ,
say exactly where and at what R.
