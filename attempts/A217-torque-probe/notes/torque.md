# A217 -- the torque probe: Fritz-John stress at jammed k0 configurations, signed corner torques, and the hunt for
# an invariant that forbids four unsettled corners (Fable, 2026-09-14; the question and the convex/non-convex
# reading are the PI's, BRIEF.md 17:40 / 17:45)

Tags: [T] proved here, [M] measured, [F] false, [C] conjecture / obligation.  Results table: `results/torque217.md`;
witnesses `results/witnesses217.jsonl`, stresses `results/torque217.jsonl`, pages
`docs/residue_map/campaigns/A217-torque/` (forces as arrows, corner torques annotated, gallery).

## 0. Verdict

> **There is no torque INVARIANT of the sign-rule kind (a signed quantity that vanishes or has a fixed sign at every
> FJ point with a settled corner and the other sign at every all-open one): every such candidate is either an
> IDENTITY that holds at every Fritz-John point whatever the corners do (C2, C3), or fails already at the settled
> optima (C1: Trump's open TL corner carries T = +0.035, other settled optima both signs).  What the stress DOES say,
> and what survives on every witness, is the PI's statement in packing terms: NO Fritz-John point found has four
> doubly-met open corners (0 of 883 genuine FJ points; the 185 configurations FORCED to have four 2-crowds all need an
> external pull at >= 1 corner, along the meeter's wall toward the corner, and that pull's torque about the meeter's
> centre is the anti-aligning torque of sign chi in 532 of 551 tilted cases).  Stated below as Lemma TORQUE
> (conjecture, any n) with a proof route that is a COUNT, not a torque identity, and is specific to n = 11.  The PI's
> remark is confirmed exactly: the sign constraint lives on wall-touching squares (an identity, s.2), interior
> tilted grains in non-convex pockets receive holder torques of both signs (254 of 254 checked) and carry none.**

## 1. Setting (what was computed)

Local optima of the side of 11 unit squares by SLSQP on the SELECTED SAT rows (per pair the axis with the largest
min-corner gap, 4 corner rows each, re-selected in an outer loop until the selection and the point are stationary;
`code/opt217.py`), then the active rows at the point (walls |g| <= 1e-7, every tied axis of every touching pair) and
the Fritz-John multipliers lam >= 0 with A^T lam = e_s (NNLS residual; HiGHS LP for the polytope; `code/stress217.py`).
The theta-component of a row gradient IS the torque of the row's force about the square's centre ((q - c) x n), so an
FJ certificate is a frictionless force network: every square in force and torque balance, the far-wall forces summing
to lam0 = 1.  Variants: the TILT BOX (every square meeting a corner box has theta in [t, 90 - t] deg, t = 3 / 10 / 20:
the no-settled-corner constraint; an active bound's multiplier is the torque the packing fails to supply) and the
CROWD rows (`code/crowd217.py`: two designated squares per corner each with a vertex inside the open corner box by a
margin delta = 0.05 / 0.02; an active row's multiplier is an external force at that vertex pulling it toward the
corner).  Seeds: A85's 262 k0 optima, 600 random starts, 168+ crowd starts (each seed run free and in every variant),
D4-quotiented; `code/search217.py`, logs in `logs/`, runs in `results/search217_*.jsonl`.

Corner frame: (u, v) = distances from the corner's two walls; det = -1 at BR and TL (reflections), torques in the frame
are det x global; chi(meeter) = +1 if its tilt in the frame is < 45 deg (its nearest alignment is the u-wall).

## 2. [T] What is a theorem (and why it is not an invariant)

**Lemma W (the wall torque).**  A square tilted by theta (mod 90 deg) touching a wall at a vertex receives from that
wall a torque W (sin theta - cos theta)/2 about its centre, W the wall force -- for EVERY wall the same expression:
the wall torques a tilted square toward its nearest axis alignment, with sign -chi.  A square touching two walls
receives twice the same sign (W = the sum).  *Proof.* The extreme vertex in the wall normal n is the rotated corner
h with h x n = (sin theta - cos theta)/2 for each of the four (n, h) pairs.  [checked to 2e-15 on every witness.]
Consequently at a free FJ point the holders supply +chi |tau_wall| -- an identity (C2, C3 of the table), which is why
"the meeters receive net wall torque of sign chi" cannot separate settled from open corners.  Global: the wall forces
have zero moment about the container centre (M_{x=s} - M_{x=0} + M_{y=0} - M_{y=s} = 0) at every FJ point -- also an
identity (internal contact torques cancel pairwise), checked to 1e-8.

**What the interior grains do [M].**  A tilted square with no wall contact is held on all sides (the non-convex
pocket): at the 883 genuine FJ points every such square with loaded contacts receives holder torques of BOTH signs on
the same square (254 / 254, `code/verify217.py`).  The sign constraint appears exactly where the PI put it: on the
wall-touching squares (one wall: half of it, the single wall's W; two walls: the full corner case).

## 3. [M] What survives -- the four-crowd obstruction

C4: no FJ point has four doubly-met open corners.  0 of 883 genuine FJ points (SETTLED 430, K0FREE 417, BOXK0 36;
sides 3.8867 .. 5.0; the maximum is THREE, once, K0FREE at 4.2855 with torque-neutral 45-deg diamonds); the 8 HELD
witnesses with four 2-crowds are held by tilt bounds (bound torque of sign chi, 494 / 494); the 185 CROWD witnesses
are held by 1 / 2 / 3 / 4 corners' external pulls (3 / 67 / 61 / 51), the pull ALONG THE MEETER'S WALL TOWARD THE
CORNER in 569 of 639 rows and on a wall-touching square in 639 of 639: what a 2-crowded corner lacks is a square that
pushes its meeter into the corner along the wall; the interior holders push the meeter flat as well in 368 of 551
cases.  C5 (thin, 14 corners): at the k0 FJ points every wall-loaded meeter of a doubly-met corner is torque-neutral
(upright-flush or exactly 45 deg); Trump's open TL corner is not (square 6 at 40.18 deg), so C5 is k0-specific.

## 4. [C] Lemma TORQUE (conjecture, stated for any n; the proof route is a count and closes only at n = 11)

**Conjecture TORQUE(n).**  Let P be a packing of n unit squares at minimal side that is Fritz-John for every consistent
selection (every sigma-minimiser is, D3').  Then at most three corner boxes (0,1)^2 of the container are met by two
or more squares.  With Lemma K0-2 (`fj_census_k0.md` s.3: the k-maximal minimiser has every corner box met by >= 2
squares) this gives: **the k-maximal minimiser is not k0 -- every optimal packing has a settled corner up to
teleport**, the k0_00 obligation in MinForm (`drain_flow_k0.md`, Theorem DF-K0).

*Proof route (n = 11).*  (i) [T, corner_seal.md / sideband.md Theorem B] the two meeters A (touching the u-wall) and B
(touching the v-wall) of a 2-crowded open corner lie in the corner's quadrant, at least one is tilted, and a contact
between them pushes each AWAY from the corner (A is on B's corner side); so a meeter that carries any force from its
partner, or from the wall pressure of the retreat direction, needs a HOLDER on its far side pushing it along its wall
toward the corner.  (ii) [M -> C, gap G1] every wall-loaded meeter of a 2-crowd needs such a holder (the crowd data:
569 / 639 pulls are exactly that force; the reading is Lemma CH corner-hurt / the two-meeter lemma: an unpinned
meeter retreats along its wall and the side descends).  (iii) [C, gap G2] a holder serves at most two meeters -- the
two meeters of one wall (it sits between them: the two corner boxes of a wall are >= s - 2 >= 1.82 apart, a unit
holder in between can touch both) or the two meeters of one corner (the elbow square) -- and the 8 meeters are
distinct squares (corner boxes >= 1.82 > sqrt 2 apart).  Then 8 meeters + >= 4 holders = 12 > 11.  For n >= 12 the
count is silent, which is consistent with the best-known packings at higher n having tilted middle grains and
(possibly) open corners; the torque identity of s.2 contributes nothing to the count -- what a proof needs is (ii).
Obligations: G1 (state and prove "a 2-crowd meeter is pinned along its wall" from FJ + the corner geometry: the force
balance of B along the wall with A's push and the far-side contacts), G2 (the holder-sharing bound as a reach
statement on the page), and the K0-2 composition through `stratify`'s k-maximal representative (S-flagged, as in
`drain_flow_k0.md` Lemma F-LEAF (S)).

## 5. Files

`code/geom217.py` (rows, SAT, corner frames), `opt217.py` (SLSQP local optimiser, active rows, NNLS residual, D4
signature), `crowd217.py`, `search217.py`, `stress217.py`, `collect217.py`, `hunt217.py` / `hunt217b.py`,
`verify217.py`, `fig217.py`; `results/torque217.md`, `witnesses217.jsonl`, `torque217.jsonl`, `hunt217.txt`,
`search217_{cp85,rand0,crowd0}.jsonl`; pages `docs/residue_map/campaigns/A217-torque/`.

## 6. Resume block (the crowd search was still running at the write-up; nothing waits on it)

    cd C:/Users/esumm/code/packing; A=attempts/A217-torque-probe
    export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
    python $A/code/collect217.py --cap 40          # re-dedupes every search file, re-runs the stress (~2 min)
    python $A/code/hunt217.py > $A/results/hunt217.txt; python $A/code/hunt217b.py >> $A/results/hunt217.txt
    python $A/code/verify217.py; python $A/code/fig217.py --max-per-class 6
    # more witnesses: python $A/code/search217.py --seeds crowd|random|cp85|atlas --tag <new> --n N --seed K --wall SEC
    # (detached: nohup ... > $A/logs/<tag>.log 2>&1 &; BelowNormal set inside via A210's c_void_p(-1) fix)
    # The one number to watch: a CROWD0 witness (crowd rows all inactive, four 2-crowds) would refute C4 / Lemma TORQUE.
