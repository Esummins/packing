# A88 — price H1 by CONTACT STRUCTURE: the k0 FJ-supporting census (Fable lead, pricing attempt)

Context: A87 proved DF-K0 — k0_00 is killed iff H1: no k0 Fritz-John point with sigma <= s-hat. H1 by
configuration-space cover is DEAD (Gordan never fires). PI direction: H1 by CONTACT GRAPH — an FJ point
must carry enough active contacts to support its multipliers, so H1 is a statement about the finite set
of FJ-SUPPORTING contact structures with no simple square, each excluded by Krawczyk (rigid, cheap per A76)
or Farkas (flexible). The unknown is the census SIZE. A31 counted ~1e30 structures globally (containment
filters only); A44 derived the FJ counting bounds (m = 3k+1+sigma-d, rigid => Maxwell; C*/C-rep) but the
FJ-restricted census was never run. Measure it.

Read first: docs/proofs/drain_flow_k0.md (DF-K0, H1's exact statement — at sigma <= s-hat, algebraic,
not s0), attempts/A44 (index identity, C*/C-rep bounds — the FJ contact-count floor for 11 squares with
d degrees of freedom), attempts/A31-structure-count/code/lib0.py + results/count_report.json (validated
filters: tilt propagation, rotation systems, planarity, per-wall <= 3; exact Burnside counting), attempts/
A59-trump-residual/results/a59_report.md (the 4.4e10 Level-0 census method + the "every filter is a
containment filter" diagnosis), attempts/A76-grain-discharge (Lemma G-R local completeness; rigid-grain
Krawczyk discharge cost; hinge grains), attempts/A87-drain-flow/results (FJ-multiplier feasibility of the
262 landings; the polished re-run results/cp87_fj_polished.json when it lands), docs/proofs/
structure_lemmas.md (L1-L7: degree >= 2, wall-to-wall chain, caps).

## T1 — the FJ contact-count floor for k0 (theorem)
State exactly: for an 11-square FJ point of the enclosing-side function with active contact set of size m
and d residual degrees of freedom (flat directions), m >= m_min(d) from A44; a k0 FJ point below s-hat has
d = ? (argue: flat directions at a minimiser keep sigma constant, so a positive-dimensional critical
manifold is allowed — bound d by the wall-to-wall chain + L1 degree >= 2 + the rattler count; give the
worst case). Also the k0-specific constraints that are STRUCTURAL (usable as census filters, unlike
"not simple"): no square flush in a corner; L6 wall-to-wall chain; per-wall <= 3; A58 crowding (every
corner box met by >= 2 squares) in its contact-graph form; A50 near-flush exclusion (a spanning chain
needs a member with theta = 0 or theta >= 1.73 deg) and flush-ruler length <= 5.

## T2 — the census (Opus chore under your filter list; exact Burnside + MC bracket as A59 did)
Count contact structures on 11 squares + 4 walls with m >= m_min, passing A31's validated filters + T1's
k0 structural filters, mod D4 x S11. Report the count with a rigorous bracket, the dominant filter, and
the per-structure classification: rigid (d = 0) vs flexible (d >= 1). Report separately the count if the
A58 crowding filter and the A50 tilt filters are dropped (so we know what each buys). Canary: Trump's
contact structure must appear (it has 3 simple squares, so it is NOT k0 — assert it is EXCLUDED by the
k0 filter and INCLUDED when that filter is dropped).

## T3 — price and verdict
Per-structure exclusion cost: rigid -> exact Krawczyk non-existence over the structure's tilt menu (A76
measured cost; A50's tilt pinning gives finite algebraic menus); flexible -> Farkas/FJ exclusion on the
d-dimensional family (A30 t3lib; A87 measured per-cell 0.81 s but that was configuration cells — measure
per-STRUCTURE). Total = count x cost; compare with A85's tree (3,200-7,000 CPU-h). If the FJ-restricted
k0 census is <= ~1e6 structures, H1-by-structure wins and becomes k0_00's route; if it is >= 1e12, say so
with the dominant multiplier named — that is a full success too. Do NOT run the exclusions beyond a
20-structure pilot to calibrate cost.

Constraints: <= 2 processes, BLAS-pinned, headroom > 6 GB; A57/A60/A61/A86 untouched; frozen verifiers
untouched; writes in attempts/A88-fj-census/, docs/proofs/fj_census_k0.md, depgraph C.K4TIER note (chip
-> A88), registry, LOG. Deliverable = the count with its bracket and the price comparison.
