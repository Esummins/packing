# A193 — probes on corners4 (k4_13) and k4_05 under the k0 toolkit (2026-09-10 night)

Labels: [T] proved, [S] specified/argued, [M] measured exact, [F] float evidence, [C] certified by a checker.
Everything measured tonight is in `results/probe193_<cls>.jsonl` (one JSON line per probe: `frame`, `root_lp`,
`noroom`, `leaf_lp`, `search`), `results/lpres_*.json` (the LP results with the roles' pieces), `results/tree_*.json`
(the assignment trees + every multibox step), `results/journal/` (A182's journals), `certs/` (v5 certificates).

## 1. The frames, and where Theorem FC applies [T]

Pins are A57's slack pins: centre within δ of the slot centre, tilt exactly 0 (the dilate F = Δ_λ P of a window
packing moves a corner pin's centre by ≤ (λ_max − 1)/2 = 0.0075 < δ = 0.01 and BL(0,1)'s by ≤ 0.0224 < δ = 0.025).
A cell of the class is FORCED (two distinct non-pin squares meet its widened box, `forced_corners.md` Theorem FC)
when it is completable, unclipped, not a pin, and its extension class S ∪ {p} is dead on the closed window.
`classes178.forced_cells` against the A56/A114/A146 scoreboard, with the two k4 pin sets supplied at run time
(`k4_lattice.json`; the census table `name_to_slots.json` carries `corners4` but no other k4 name):

**corners4 = k4_13** — pins BL(0,0), BR(0,0), TL(0,0), TR(0,0). Completable unclipped cells: the eight slots
BL(1,0), BL(0,1), BR(1,0), BR(0,1), TL(1,0), TL(0,1), TR(1,0), TR(0,1). **Every one of the eight extends to
k5_16** (all one-cell completions are D4 images of k5_16 = corners4 + BL(0,1), `k4_lattice.json sup_k5`).
k5_16 is NOT on the window scoreboard: it is one of A57's two shadow-tree classes, closed at the fixed side s0
by A57's s0 tree (ledger frozen fact: every k ≥ 5 class is dead at s0) and OPEN on the window (A57 G1, ~400
nodes owing, `budget.md` §A). Hence: **on the window corners4 has NO forced cell — Theorem FC gives nothing; at
s0 all eight slots are forced** (this is Lemma CC4 of `protected_trees.md` §7.1, which cites the same s0 kill).
The window form of every s0 statement below is therefore conditional on A57 G1 for k5_16 — the same [P] the
A57 row already carries, no new obligation.

**k4_05** — pins BL(0,0), BL(0,1), TL(0,0), BR(0,0) (the left column's bottom two, the top-left and bottom-right
corners; TR clear). Completable unclipped cells and their extensions:

| cell | extension | scoreboard | forced |
|---|---|---|---|
| BR(0,1) | k5_15 | FULL [191/50, s0] | on the window |
| BR(1,0) | k5_13 | FULL (A146) | on the window |
| TL(1,0) | k5_12 | FULL (A114) | on the window |
| BL(1,0) | k5_11 | A57 shadow tree: s0 only | at s0 only |
| TR(0,0) | k5_16 | A57 shadow tree: s0 only | at s0 only (a corner: lonely clip applies, FC-corner) |

BL(0,2) is clipped by the TL pin (|3.377 − 2.5| < 1), TL(0,1) by the BL(0,1) pin, BL(1,1) is not completable
(BL(1,0) is not a pin). So k4_05 has **three window-forced cells** (six meeter incidences) and two more at s0.

## 2. The obstruction at the root, before any probe [T]/[M]

A55's Lemma K1 (aliveness descends containment: if S′ = S + {p} has τ*(S′) ≥ 11 − |S′| then τ*(S) ≥ 11 − |S|,
by adjoining p to the witness family) is stated for the exact-pin LP; with slack pins it holds up to the δ-band
[S]. Its content here: **the pins-only root LP of either class cannot kill while k5_11 / k5_16's roots are
LP-alive** (they are: that is why A57 needed trees). corners4 ⊂ k5_16; k4_05 ⊂ k5_11 and k5_16. Guard lines do
not change this: a guard-line column is a valid dual constraint for every packing containing the pins, and the
k5 witness family plus the pin p uses exactly chord_p(l) of the line's budget rhs_S(l) − rhs_{S′}(l).

Nor does Theorem FC change the ROOT LP. With anonymous meeter roles (window = the cell's meeter window, empty
K′) the windows clause's rows are a SUBSET of the free rows whenever free squares remain (f = 11 − #roles > 0:
a window row is exempt only against another window's attached core, which the free rows are exempt against
too), and the budget b4 = 11 − m + r_c is the free budget shifted by the attached pins. **So the FC hypothesis
buys the LP nothing until either (i) every square is boxed (f = 0: A182's complete assignments, where the free
rows drop and only the windows remain), or (ii) a meeter's pieces shrink enough for K′ ≠ ∅ (a core that exempts
and a chord that reduces the line budgets).** That is exactly A182/A185's mechanism on c0_Y1033 (9 of 12
complete assignments dead under v4), and it is what the probes below test on the two classes.

## 3. The probes (measured)

### 3.1 The pins-only root LP with guard lines (budget 7, A190's ExactHyp + guardlp, 10 lines: pin midlines / core
edges, the slot lines x, y ∈ {1, 3/2, 2, s−2, s−3/2, s−1}, the container sixteenths; cap 300 s) [M]

| class | τ | converged | active lines | support | axis-aligned mass | tilted mass | LP s |
|---|---|---|---|---|---|---|---|
| corners4 | **7.1952** (> 7) | no | 0 of 10 | 209 placements | 2.36 (at the slot poses: (0.5, 1.65), (3.38, 1.5), (2.38, 0.51), (2.38, 3.38)) | 4.84 (centre block, 28°–58°) | 526 |
| k4_05 | **6.9648** (< 7) | no | 0 of 10 | 277 placements | 2.05 (0.75 at the TR corner = k5_16's pin; 0.55 within 0.08 of BL(1,0)'s slot pose = k5_11's pin) | 4.92 | 337 |

corners4 reproduces A65's wall (τ(0) = 7.2545 after long column generation; A55's canary 7.200): the root is
LP-alive, no guard line is active (chords of tilted centre squares on the pin lines are < 1, the lines cost s − 2
and buy nothing), and the support is the fractional cloud of `corners4_empty.md` §4 — near-axis arm squares at the
slot poses plus tilted centre squares. **k4_05's 6.965 is the same number A55 measured twice (6.982 at 1,024 s,
6.973 at 3,885 s, both `FAIL(rc=3)`) and it is NOT a kill [C-FAIL]:** the v5 certificate (total 6.99978, 20,639
boxes, 9,467 core-exempt) fails with 58 holes at depth 56 — 8 witnesses AT the BL(1,0) slot pose (1.49, 0.50, 0°)
= k5_11's fifth pin, 40 in the centre block just above it ((1.489, 1.038), 1.3°: a square stacked on the BL column
at the k5_11 image), 16 in the top arm — and A190's witness re-solve lands at **τ = 7.189 > 7** ("re-solve lost
the kill", `certs/root_k4_05.*`). That is Lemma K1 measured: the LP's slow creep toward 7 is the k5_11 / k5_16
images being pushed one row at a time, and the limit is above the budget. Root LPs are useless for both classes,
guard lines included; anyone re-running A55's k4_05 root and reading 6.97 as a kill candidate should read this line.

### 3.2 corners4 at s0: the assignment search from the root (8 forced slots, 16 meeter incidences) [M]

Root = 4 pins + nothing else; A182's search (nsub 4 / refine 2, chord rows at every tree node, lane prune 30 s,
`MAXF = 7`) instantiates anonymous meeters cell by cell. Pass 1 (150 nodes, 674 s: **4.5 s per multibox node**)
reached depth 1: unit propagation forced BL(0,1) ← F1+F2 and BR(0,1) ← F3+F4 (the far cells have ONE option:
two new squares, by the √2 rule), then the first branch TR(0,1) had 4 options and the option tests (81 pair
nodes, 65 single, 23 pair-splits) ate the budget. Pass 2 (journal replay + 900 nodes / 3,000 s) went down the
first branch of each level — TR(0,1) ← F3+F4, TL(0,1) ← F1+F2, BL(1,0) ← F1+F2 (10 options), TL(1,0) ← F3+F5 (3),
BR(1,0) ← F1+F4 (6), TR(1,0) ← F3+F5 (4) — and reached its **first complete assignment at ≈ 520 nodes**: nine
roles, F1 ↦ {BL(0,1), TL(0,1), BL(1,0), BR(1,0)} (four slots: legal for the WIDENED boxes — the pose (1.425, 1.425,
0°) meets all four 0.088 deep through the middle-strip overlap and the pads; CC4's "≤ 3" is for the unwidened
boxes), F2 ↦ three left/bottom slots, F3 ↦ four top/right slots, F4 ↦ three, F5 ↦ two; two free squares.

At that leaf (`results/probe193_corners4.jsonl`, `lpres_corners4_root_forced-BL01-…`):
* the roles are LOCALISED — hulls F1 0.31 × 0.60, F2 0.43 × 0.23, F3 0.61 × 0.61, F4 1.15 × 0.60, F5 1.29 × 1.24,
  all at tilt [0, 90°]; **three meeters have grown cores** (F1 a = 0.117, F2 0.185, F3 0.063), F4/F5 none;
* **no-room leaf: UNDECIDED** in 161 s — the bisection against the 7 cores drops 85.8 % of the free square's
  (centre × tilt) volume but the residue pockets have area 5.90 (F4/F5 have no core, the centre block is open);
* **windows + guard-line LP (b4 = 11, 7 cores attached, 2 free): τ = 11.000000 exactly, NOT converged
  (minmass 1.5·10⁻⁸ — uncovered rows remain, so the converged value is ≥ 11), 0 of 10 lines active, 417 s.**
  The support is the pins at weight 1 plus **fourteen placements at weight exactly 1/2** (a half-integral
  support; the largest near-disjoint sub-family among the fourteen has 5 members, worst gap +0.10 — so it is NOT
  two near-packings averaged, it is a genuinely fractional odd-cycle support): near-axis squares at (0.5, 1.65),
  (3.38, 1.65), (1.60, 0.51), (2.38, 0.58), (2.30, 3.35), (2.23, 2.23) and tilted ones at (2.54, 1.41, 25°),
  (1.43, 1.28, 41°), (1.52, 1.61, 86°). This is the "fractional tilted" phantom — the same object as the root's
  cloud, concentrated by the windows onto 14 poses, and no chord row sees it (every tilted square's chord on
  every pin/slot line is < 1).

Pass 2 in full (stopped by hand at 02:55 once the LP quota was spent — the remaining enumeration was repeating the
verdict): **318 multibox nodes, 1,884 s of geometry (median 5.0 s, max 17.7 s per node), depth 8, 6 complete
assignments reached, no-room 6/6 UNDECIDED (identical residue 5.903 at every leaf: the pockets are set by the four
pin cores; the cored meeters are too small to close the centre block), 3/3 windows + guard-line LPs ALIVE at
τ = 11.000 exactly (417 / 344 / 358 s), 0 of 10 guard lines active at every leaf, 13 option-test nodes dead by
the pair leaf (`EmptyBox` on F1 / F3: a meeter restricted to a slot window that another meeter's K′ fills), no tree
node dead by a chord row (min rhs 1.877 = s − 2: the pins' four unit chords leave s − 2 > 0 on every pin line, and
the meeters' min-chords are 0).** So for corners4 the toolkit's every leaf returned the SAME answer: the geometry
localises the meeters (a real gain over the root — hulls of 0.1–0.7 area, three of five with cores), and the
measure LP at that localisation sits at exactly the budget with a half-integral support.
