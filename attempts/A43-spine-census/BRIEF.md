# A43 — full-library re-census + the spine census (Fable lead)

Goal: test the PI's bulk-kill thesis and the L6-anchor synthesis (docs/ideas.md I-L16). Two halves,
both measurement-first.

## H1 — re-census with the 2026 theorem library
Re-run the A31 structure census (attempts/A31-structure-count/code/lib0.py, ablation machinery)
with EVERY certified theorem proven since A31 added as a bulk filter, each applied SOUNDLY (a
filter = a theorem valid for all packings at side <= s0; the target family = candidate-jammed
grains below s-hat, which are packings, so all apply): A38.1 interior occupancy AT s-hat; per-wall
<= 3 (A31/A37, proof in A31's report); flush-mandatory (A31); A21 THM3 tilt-window exclusion +
orientation theorems; wastage motif kills (A23/A25 atlas: banned pinwheel 4-cycle at s-hat, k=3
mid-tilt kills — as forbidden-subgraph/motif filters with the realizability caveats A25 recorded);
tight-variety membership (A33 t2 rasters: placements with certified coverage > 1+eta cannot appear
— per-node position x tilt filter); pair tight-sums as pairwise-conflict edges where certifiable.
Deliverable: the new ablation table (old count -> per-filter -> composed), per-filter kill factors,
and the honest composed count at k = 3..7 with extrapolation. State clearly which filters are
exact vs approximate-realizability (report both counts).

## H2 — the spine census
Formalize (T-quality, yours): by L6 every critical configuration's support graph contains a loaded
chain connecting opposite walls on the binding axis. Define spine type = (length k, per-link
contact type [flush / corner-on-edge / corner-corner], tilt-class profile, wall-end types).
Constraints to enumerate under, ALL certified: span arithmetic (consecutive centres <= sqrt2, ends
within sqrt2/2 of their walls, total span >= s0 => k >= 3; upper bound k from centre separation >= 1
in the box); tilt coupling per contact type (flush => equal mod 90; wall-flush => axis-aligned;
corner-on-edge => certified interval); A21 tilt windows; per-link tight-variety membership (A33
rasters at s-hat); interface wastage: sum over links of certified minimum neighbourhood wastage
(A25 atlas lookups, region-disjointness rules) <= s0^2 - 11 = 4.0318. Enumerate all spine types
surviving the stack; CANARIES: Trump's tilted 5-strip must survive; each A37 atlas valley's spine
must survive at ITS value (run the stack at their s to check the machinery, since their values >
s-hat they need not survive at s-hat itself — handle honestly). Deliverable: the spine-type count
at s-hat with the per-constraint ablation, the survivor list with structure descriptions, and per-
survivor an assessment of completion-analysis cost (anchored A35-style semantic cells — design
estimate only, no completion runs).

## Compose
If H2's count is small (<= a few hundred): write the composed far-field program (per-spine
completion) with cost model grounded in A35's measured per-anchor costs; name what remains
unproved (completion soundness statement, the H1/H2 join). If large: name the constraint that
failed to bite. Honest either way.

Constraints: Opus subagents for compute; <= 4 heavy processes; ONE long-poll waiter per background
run; checkpoints; exact/interval verification for headline claims (approximate filters labeled);
A29 untouched. Registry row, LOG entry, PI-readable report.
