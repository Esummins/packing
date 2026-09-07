# A131 — pin-clip: shrink each node's centre box to the pin-feasible region per tilt sub-bin before the LP (Opus, measurement first, live second)

Context (2026-09-07). The PI, reading A107's drawings of `k5_11_interior_Y0036` (docs/shadows/S02.svg panel 1,
docs/residue_map/a57_lp_support.svg), noticed that most of the drawn tilt range cannot be realised at most centres
of the box without the conditioned square colliding with the pin bl10. Checked exactly (coordinator, 2026-09-07,
pins at their slots shrunk by pin_delta = 0.01, separating-axis test on a 41×41 centre grid × 11 tilts per bin): the
level-1 box x ∈ [1.7988, 1.9385], y ∈ [1.3795, 1.5193], θ ∈ [82.37°, 90°] has its lower half (y < 1.4494) blocked by
bl10 at every tilt (the tree killed those four children by "core meets pin core"); in the upper half, the tree's
θ ∈ [82.37, 90] (a slight CW lean, since θ = 90 is upright) is feasible only in a sliver at the TOP of the box — the
bottom-right vertex dips into the gap between bl10 and the BR pin and the bottom edge must clear bl10's corner
(2, 1): centre above y = 1.491 upright, above 1.505 at 82.37° on the right of the box, above 1.521 (outside the box)
on the left — while the mirror lean is impossible for the whole D02/D06 bin. So the alive children D02/D03/D06/D07 run
their LP on a box of which well under half is realisable; T5″ (trim57's octagon test: kill a tilt sub-interval iff
the WHOLE centre box is inside one pin's octagon) cannot empty such a bin because the box's top-right corner survives —
which is exactly A123's live finding (trims bite at the tilt extremes, 15 of 16 trimmed bins still ALIVE).

The lever: PIN-CLIP. For each node and each tilt sub-bin, replace the centre box by the (axis-aligned bounding box of
the) set of centres at which the conditioned square, at SOME tilt in the sub-bin, is interior-disjoint from every pin
(at every pin placement within pin_delta) and inside the container — sound because discarded centres admit no packing
in the node's hypothesis (the pins are fixed by the class; the tolerance is honoured by shrinking the pins). Exact:
the forbidden region for one pin at one tilt is the Minkowski sum of the pin rectangle and the reflected tilted
square (an octagon); over a tilt sub-interval, take the INTERSECTION over tilts of the forbidden octagons (a centre is
discardable only if forbidden at EVERY tilt in the sub-bin) — or, simpler and still sound, sub-divide the tilt bin
finely, clip per sub-bin using the octagon at each sub-bin's worst case (the octagon's support function is monotone
in |cos|+|sin| — reuse trim57's bounds), and union the per-sub-bin clipped boxes back if the tree wants one child.
The child then carries (clipped box, tilt sub-bin) — the same object as T5″'s "trimmed child" with the centre box
narrowed too, so the frozen verifiers see an ordinary (smaller) box and nothing changes in the certificate format.

Read first: attempts/A57-shadow-trees/notes/lemmas.md (T5/T5′/T5″, the emission-nondeterminism and survivor-count
notes), attempts/A96-a57-parametric/code/trim57.py (octagon test; how trims are attached to children), attempts/A57-
shadow-trees/code/{pinguard.py (tight core; the domain assertions), tree57.py (emission: where boxes are formed; DO
NOT edit — read only), deepen.py}, attempts/A96-a57-parametric/notes/ (the offline 2,222-box corpus and how the
159/70/89 were counted — `155a3c5b`/`e68d8dbc`), attempts/A124-recheck-day/ (T2's touched-vs-emptied control, if
landed), attempts/A57-shadow-trees/PAUSED.md v2 (the resume block; the lever table), docs/budget.md §B–D.

## T1 — the clipper (offline, exact)
`pinclip.py`: input a node record (class → pin slots, pin_delta, box, tilt bin); output per tilt sub-bin (start with
the node's own bin, then 2/4/8 sub-bins) the clipped centre rectangle (or EMPTY), computed exactly in rational
arithmetic from the octagon intersections (or the conservative sub-bin worst case), plus a sampled confirmation per
node reported as drawn → tested → hits (≥ 10⁴ centre–tilt draws inside the discarded region must all collide; ≥ 10⁴
draws inside the kept region are reported for the feasible fraction). Positive control: every box the tree killed by
"core meets pin core" must clip to EMPTY at every tilt; every ALIVE node's stored LP support atoms (the conditioned
square's columns in the jsonl/certs, if stored) must lie inside the clipped box.

## T2 — the measurement on the corpus
Over the same 2,222-box corpus A96 used (the open boxes at the pause, both classes, levels 1–4): per box, the kept
area fraction at 1/2/4/8 sub-bins, the number of boxes whose clipped box is EMPTY at every sub-bin (a full kill,
beyond T5′/T5″ — report the overlap with the 70/89/159), and the distribution of "free levels" (log₂ of the area
ratio, halved: how many bisections the clip saves). By level and by class. Compare the free-levels figure against the
schedule in docs/budget.md §A (the A57 row) and say what it does to the 11–13 wall-days IF the LP's kill rate on a
clipped box equals the tree's measured kill rate at the corresponding smaller level (state that assumption; it is the
survivor-count rule's caveat).

## T3 — the LP effect, in vitro (bounded, ≤ 6 CPU-h, 2 processes BelowNormal, honour A57's PAUSE sentinel: this is
not a shard launch — run the node LP through the same path A124's recheck96 uses)
Take Y0036's four alive D2 children and six more ALIVE boxes with kept fraction < 0.5 (from T2, mixed levels); re-run
each node's LP once on the clipped box (same budget, same rows, 240 s then certify on η ≤ −1e-3 per the two-stage
protocol; 900 s only for a knife edge) and once on the original box as the control from the stored record. Report
τ/η/minmass before vs after, and any certified kill (replay by certificate; never re-emit). This is the honest test of
whether narrowing the box moves the LP or only the columns.

## T4 — deployment shape (no deployment)
One page in notes/deploy.md: where in emission the clip would apply (after T5′/T5″, before the LP), the record fields
(clip_from, kept fraction — PERSISTED, unlike trim_excluded which A123 found is never persisted), the verifier
implications (none — smaller ordinary boxes), the Lean shape (the discarded region is a union of octagon
intersections: a T5-type logic leaf with a tilt range and a centre sub-box), the n-general statement (pin-clip is the
class-pin analogue of the container clip and applies to every conditioning tree in the protected tier), and the
resume-block line for PAUSED.md.

Constraints: ≤ 2 processes, BLAS-pinned, BelowNormal (A124/A125/A126/A129/A130 are running; the PI is using the
machine); READ-ONLY on every campaign and on A57/A96 drivers (new files only under attempts/A131-pin-clip/); frozen
verifiers byte-identical; never launch a shard; NO recursive deletes; never delete a pidfile; PYTHONDONTWRITEBYTECODE=1;
git = fetch + plain merge + push own paths (no rebase/autostash/reset). Writes: attempts/A131-pin-clip/{code,notes,
results,logs}, docs/budget.md §D one row, attempts/A57-shadow-trees/notes/lemmas.md one section (T5‴ pin-clip, as
A96 did for T5″), registry row, LOG.md. Report ONCE: T2's table (kept fraction, empties, free levels by level) first,
T3's before/after second, T4's deployment shape third, pointers last. No interim messages.
