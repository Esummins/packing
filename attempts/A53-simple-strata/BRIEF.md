# A53 — simple-square stratification pilot (Fable lead)

Goal: pilot I-L20 (docs/ideas.md — read first; PI's idea). Three legs, measurement-first.

(a) SKELETON ENUMERATION (exact, small): define grid-locked ("simple") recursively — doubly-flush
against {walls} u {already-locked squares}, wall-anchored (floating flush pairs are NOT simple —
they go to the non-simple side); enumerate all skeletons at container side s0 = 969271/250000
(grid slots at exact rational offsets; k = 0..~7; D4-reduced). Trump's k = 5 skeleton must appear
(3 corners + one corner's adjacent on-grid pair — verify against his exact coordinates). Report
the census by k.

(b) RESIDUAL-REGION LPs — THE DECISION NUMBER: for Trump's skeleton + a representative sample of
non-Trump skeletons (all k >= 4 skeletons if the census is small, else ~10): pin the skeleton
EXACTLY, delete its area, run the guard LP on the residual region at budget 11 - k (adapt the A07/
A38 row-generation machinery: placements clipped to the residual region — collision rows vs the
pinned squares handled exactly; A39's cheap-cert rule in the loop). Measure tau* and
eta_residual = tau* - (11 - k) per skeleton. Key questions: does the 1/4-ghost survive on the
asymmetric residual regions (compare against A14's full-box corner-pin data: tau = budget exactly)?
Are non-Trump skeletons killable (tau < budget, then EXACT certification)? On Trump's own skeleton
(unkillable by F4): how small is eta_residual, and map the residual tight variety (A33 t2 mapper
pattern) — does the 6-square localization collapse?

(c) THEORY (yours): the K-MAXIMALITY selection lemma — among minimizers, one with no remaining
sigma-neutral flush-closing/grid-sliding move exists (D2-style selection; handle blocking honestly
— the bridge mechanism means blocked near-grid squares exist; state what the lemma does and does
not give for the low-k strata), + the partition-exhaustiveness statement (every packing in exactly
one stratum; edge cases: floating flush clusters, singly-flush chains). Branch-labeled, honest.

Canaries: Trump (his skeleton enumerated, his residual LP >= 6 with his own packing feasible);
A14's corner-pin numbers reproduced in the full-box formulation before trusting the residual one.
Constraints: machine is busy (A50/A51/A52) — <= 2 heavy processes, theory first, stagger LP runs;
ONE long-poll waiter; exact certification the arbiter; checkpoints; A29 untouched. Registry, LOG,
PI-readable report with the eta_residual table as the headline.
