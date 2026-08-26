# A31 — structure-space counting pilot (Opus)

Goal: measure the size of the PRUNED contact-structure space (the go/no-go number for the
structure-first exclusion campaign). Not a proof; a certified count of an enumeration whose filters
are marked sound/soft per docs/proofs/structure_lemmas.md. Read that file first — the Soundness
ledger at the end says exactly which filters are HARD prunes, which are THIN flagged branches, and
which are SOFT (report-only ablations, never silently applied as prunes).

## Level 0 — coarse graphs
Enumerate simple graphs on k loaded-square nodes + 4 wall nodes (colored; walls in a fixed 4-cycle,
D4 acts on them), for k = 3, 4, 5, 6, (7 if budget allows), up to isomorphism (square relabeling ×
D4 on walls; canonical forms via pynauty if installable, else a careful color-aware canonical
labeling — state which). Hard filters: L1 (square degree ≥ 2), L4 planarity, L5(b) wall-degree ≤ 2
adjacent-only, L5(a)-realizability BROAD-phase (graph distance consistency with centre distances in
[1,√2], wall offsets √2/2, container 3.8771 — an interval/spring feasibility check; mark its
soundness honestly, approximate is OK for counting if labeled), L5(d) degree ≤ 12, L6 (some
component connects two opposite walls — enumerate the λ₀ = 0 / self-stress branches separately per
L3/L6, count them, do not drop them), L7. Thin branches (L2 degree-2) counted separately.
Report an ABLATION TABLE: count with no filters, then cumulatively adding each filter, per k. Also
report the SOFT-filter counts (row count ≥ 3k+1 with flush multiplicity 2; per-wall cap 5; kissing
8) as separate columns, never folded into the hard count.

## Level 1 — decoration fan-out (sample)
For ~20 random Level-0 survivors at k = 5 (and a few at k = 6): count edge-label decorations —
square-square: {corner-of-i on edge-of-j (4×4 choices ×2 owners), flush (4×4 edge pairings)};
square-wall: {corner-on-wall (4), flush (4)} — surviving the tilt-propagation consistency check:
flush ⇒ tilts equal mod 90°; wall-flush ⇒ tilt ≡ 0 mod 90°; corner-on-edge ⇒ tilt difference
constrained to the realizable interval (derive it: the corner must project inside the unit edge —
compute the certified interval in tilt-difference); wall-corner ⇒ free. Propagate intervals around
the graph (constraint propagation to a fixpoint; branch on mod-90 classes). Report the fan-out
factor per edge and per graph (median/max), and how much tilt propagation kills.

## Level 2 — extrapolation
Fit Level-0 survivor growth in k; project k = 7..11; multiply by measured Level-1 fan-out; state the
projected total structure count and the assumption list. Include the rattler-completion note: cores
of size k < 11 also need the 11−k completion branch — count cores, don't model completion.

## Deliverables
results/count_report.json + terse REPORT (findings block in the json if .md blocked): ablation
tables, fan-out stats, projection, gap list (every approximation and every place the enumeration
might miss a structure — completeness of the graph generator matters more than speed).
Constraints: ≤ 6 workers, RAM guard, checkpoint per k, resumable. Pure CPU is cheap here — prefer
exhaustive per k over sampling wherever feasible. Do not touch A29/A30 state. Terse traffic.
