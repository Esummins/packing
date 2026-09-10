# A198 -- FASTPROP: cheap exact propagation over a page node before any bisection/LP (Fable lead, 2026-09-10 ~11:40)

Restated from the PI's instruction.  Agent messaging is broken: everything is in this brief and on disk.
Short responses; files in pieces; no interim messages; commit after each milestone.

## The PI's design (2026-09-10 ~11:30, on k5_16_interior_Y0054)

> "we need two meeters for BL(1,0); the lonely-corner logic means only one from each relative quadrant; both top
> quadrants are dead by collision with H; the bottom chord row doesn't allow one in each of the bottom quadrants;
> so H MUST be one of the meeters; pull H down to touch the corner of BL(1,0) and start checking from there after
> ~100 microseconds."

i.e. propagate with CHEAP tests (quadrant-level exact dead tests against the cores, chord rows, forced clips)
before any bisection/LP, and only call the expensive pair test / assignment search where the cheap tests leave a
genuine ambiguity.  The PI's diagnosis: the theory covers the nodes; the limitation is checking all eliminations
efficiently.

## The prototype (coordinator, scratchpad; copied to code/quadprop_y0054.py and code/hclip_y0054.py)

(1) per forced slot, four quadrant cells of the meeter window around the slot box's centre; each cell bisected
coarsely (depth 7, 4 tilt sub-bins) against every role's K' with multibox's exact dead test -> surviving volume
fraction (3 s for four quadrants); (2) the bottom chord row (open chords; A190's guardlines_v5.minchord over the
surviving pieces; pins' chords) forbidding both bottom quadrants; (3) the count of distinct free meeters possible;
(4) if <= 1, H must be a meeter: keep only H's pieces not provably missing the widened slot box (A161's
chordlane.box_misses_cell_exact, bisected to depth 8 -- 46 pieces keep 0.18 of H's box on Y0054), renormalise
(multibox), and re-test every forced slot against the pinned-down H (30 s for the whole pass).  Measured on Y0054
after the clip: H provably misses 4 of 6 slots; several slots keep two or three viable quadrants at 0.2-0.5
volume; the decisive step is the JOINT count with adjacency.

## Build: code/fastprop.py -- a propagation engine over a page node (pins + H + instantiated meeters), n-general

Sound at every step; each pruning is one of: the exact dead test on a cell (multibox), an open-chord row (A144/A190
minchord, OPEN chords), A161's exact miss test, Lemma A1's l-inf separation (cells of side < 1/sqrt2 hold at most
one centre), Theorem FC's two-distinct-meeters requirement, Theorem B's lonely region at CORNER slots only.

(a) cell-level viability per forced slot with the tests above, cached by cell (a global grid of side < 1/sqrt2
    over the centre range, grouped into the slot's four quadrants for the page);
(b) forced clips: when a slot has <= 1 viable free-meeter cell, H (or the unique instantiated role that can reach)
    is clipped to the poses meeting the slot; when H is the only possible second meeter of two different slots that
    H cannot meet simultaneously (exact test), DEAD;
(c) the JOINT count: a cover check -- each free square meets a set of slots it can reach jointly (cells whose union
    a single unit square can meet, decided by the exact reach test on the intersection of the cells' meeter windows
    and A1 between meeters of one slot); the free squares must cover the remaining incidences; an exact small search
    -- the counting bound with adjacency, cheap; chord rows prune the search;
(d) only where the joint count leaves options: the pair test (A178's geo178b.slot_pair_test, fine setting) on the
    ambiguous slot, and the assignment search (A182's assign182) seeded with the pruned option table;
(e) every step timed, every pruning recorded with its test and result (the certificate is the list of exact
    tests); a step page docs/residue_map/fastprop_<page>.svg in the drawing rules (gen_a57_lp.py style:
    hypothesis squares only at admissible poses; the slot quadrants coloured by viability; H's pulled-down box; the
    joint-count table printed; times printed).

## Run

Y0054 to a verdict first (the PI expects DEAD; if ALIVE say exactly which slots' pairs survive and draw a realised
pair if the sampler finds one); then every alive a57v4 page (docs/shadows/STATUS.md; skip Y0491 -- A196 is on it;
A197's slot-pair results in attempts/A197-slot-pair-pass/results may retire some -- read them) with a per-page wall
of 600 s; results/fastprop198.jsonl; a status-collector block in docs/shadows/status_gallery.py in the style of
(7b)/(7c) for pages dead by fastprop (certificate = the exact-test list; label [C: geometry, fastprop]); rerun it;
report pages retired and the time per page; docs/residue_ledger.md section 4 paragraph; docs/budget.md section D
item; registry row; LOG entry; commit with `git commit -- <pathspecs>` after fetch + plain merge; push.

## Rules

<= 2 python processes BelowNormal affinity 0xFFFF; lab ceiling 12 EXCLUDING "Claude Extensions" command lines
(count and WAIT); read-only on every other attempt; no recursive deletes; PYTHONDONTWRITEBYTECODE=1.  Every claim
[T]/[S]/[M]/[F]/[C].  Report ONCE, tersely (under 800 words): Y0054's verdict with the propagation trace first, the
pass table second, pointers last.
