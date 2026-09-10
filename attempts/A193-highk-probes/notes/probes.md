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
