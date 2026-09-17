# A244 — the 12-STUCK four-crowd: does it exist, and at what side?  (PI, 2026-09-16 19:30)

The PI, at A243's addendum: *"have you started that search?  if you can't construct a ring like
that, that's a pretty big issue for k0 existence"* — the ring in question being a packing of 11
unit squares with **all twelve border cells doubly met**: the four corner boxes c00 = [0,1]² AND
the eight wall slots c01 = [0,1]×[1,2] (up c's wall) and c10 = [1,2]×[0,1] (along c's floor), in
each corner's frame (A243 `notes/wall_slot243.md`, Lemma WALL-SLOT [T] + SLOT-MET [S]).  A square
MEETS a cell iff their interiors overlap.

Code `code/{cells244,fast244,feas244,search244,probe244,verify244,stress244,hand244,draw244,
pages244,summarise244}.py` + `run244.sh`; results `results/twelve244.md`, `results/twelve244.jsonl`
(every verified candidate), `results/probe244_*.jsonl`, `results/hand244.json`; pages
`docs/residue_map/campaigns/A244-twelve-stuck/{twelve_stuck,threshold244}.svg`.
Tags as elsewhere: [T] proved here, [M] measured, [S] proof route with a gap, [C] recommendation,
[F] a claimed step that fails.

## 0. The answer in one line

PLACEHOLDER-ANSWER

## 1. What is constrained, and how

**The cells.**  `cells244`: in corner c's frame (u, v), c00 = [0,1]^2, c01 = [0,1]x[1,2] (up c's
wall), c10 = [1,2]x[0,1] (along c's floor); every frame map is a signed diagonal, so all twelve
cells are global axis-aligned rectangles.  At s = 4 they are exactly the twelve boundary cells of
the 4x4 grid and they tile the border strip (A243's observation, re-checked in `test244`).

**Meeting.**  A square meets a cell iff their INTERIORS overlap.  For a unit square and an
axis-aligned rectangle the separating-axis set is {e_x, e_y, n_0(th), n_1(th)}, and the OVERLAP
DEPTH is the min over those four axes of the projection overlap: > 0 iff the interiors meet.  For
any unit axis a the square projects to [c.a - h/2, c.a + h/2] with h = |a.n_0| + |a.n_1| and the
rect to [b.a - v/2, b.a + v/2] with v = |a_x| w_x + |a_y| w_y, so depth and its gradient are
closed-form (`fast244`).

**Why not A217's crowd rows.**  A217 forces a corner box by pushing a DESIGNATED VERTEX of a
designated meeter into the box.  That is only sufficient for meeting, and it cannot express the
CROSS configuration -- a 45-degree unit square centred on a cell meets it with no vertex of either
inside the other (`test244` checks this) -- which is exactly what a wall slot invites.  A244 first
replaced the vertex row by a WITNESS-POINT row (`crowd244`: a point constrained into the cell and
into the square, 8 smooth rows per designated pair, no selection) and minimised s with SLSQP
(`opt244`).  **[F] That form does not work**: with the designation frozen, the phase-1 problem
(maximise the uniform slack t over all rows) converges to t = -delta/2 at EVERY margin and from
every seed -- the designated meeter clips a cell at a corner and cannot enter without overlapping
its neighbour, and SLSQP has no way to re-designate.  The files are kept (and `test244` still
checks the witness-row jacobian) because the failure is the reason for the second form.

**The form that works** (`fast244` + `feas244`): a DESIGNATION-FREE penalty

    F(z) = sum_walls min(g,0)^2 + sum_pairs min(gap,0)^2 + sum_cells min(d2 - delta, 0)^2,

where d2 is the SECOND LARGEST overlap depth of the cell over the eleven squares.  Which two
squares meet a cell is decided afresh at every evaluation, so the assignment moves during the
descent.  Phase A finds a feasible point with the side FREE (the twelve-cell condition is
infeasible for LARGE s as well as small -- see s.3 -- so widening alone never finds the window);
phase B is a halving descent on s, re-polishing at each side and accepting only F = 0 exactly.
Optional tilt floor: every square's tilt at least `--tilt` degrees from a multiple of 90.

**Verification** (`verify244`, 40-digit mpmath INTERVAL arithmetic).  An optimiser output has
gaps of order -1e-15, so it is not literally a packing.  The verifier first INFLATES: c -> lam c,
s -> lam s (this adds (lam-1) n.(c_p - c_o) >= (lam-1)(gap + 1) to every selected separating-axis
gap and (lam-1) * a non-negative centre coordinate to every wall gap), takes the smallest lam on a
ladder that makes it a packing, and then certifies AT THAT SIDE: containment, pairwise
interior-disjointness, and >= 2 strictly positive overlap depths for each of the twelve cells.
Every verdict is taken only when the whole interval lies on one side of 0.  Cells are anchored at
the walls, so a meeting of depth d survives any inflation with lam - 1 < d / (2 s): the certified
sides use lam - 1 ~ 1e-14 against depths >= 1e-5.

## 2. The thresholds ([M]; the authoritative tables are `results/twelve244.md`)

**[M] 12-STUCK EXISTS, and it is common just above 4.**  Before any new search: of A217's 1217
FEASIBLE four-crowds (`search217_crowd0.jsonl`, min pair and wall gaps >= -1e-9), **282 are
already 12-stuck** -- all twelve border cells doubly met -- the least at side 4.002076.  So the
configuration type the PI asked about is constructible; it was already in the lab's own corpus,
unlabelled.

**[M] The least CERTIFIED 12-stuck side is 4.0000xx** (see `results/twelve244.md` s.1 for the
exact value and the witness), reached by the halving descent at crowd margin delta = 1e-5 from
A217 seeds and certified by `verify244` in interval arithmetic.  The descent's limit moves with
the margin exactly as `4 + c delta` (delta = 1e-3 gives ~4.0004, delta = 1e-5 gives ~4.00002), so
the measured infimum of the sides carrying a 12-stuck packing is **s = 4, the trivial side**, and
the search never gets below it.

**[M] Nothing below 4.**  The fixed-side probe minimises the residual
`max(-min wall gap, -min pair gap, delta - min second depth, 0)` at a FIXED side; it is 0 exactly
when a delta-margin 12-stuck packing exists there.  Over the ladder (each side seeded from A217's
crowds, random, border and grid starts):

| side | 3.82 | 3.877084 = s-hat | 3.95 | 3.999 | 3.9999 |
|---|---|---|---|---|---|
| best residual | 3.5e-2 | ~2.7e-2 | 5.8e-3 | 4e-6 | 3.5e-6 |

and **no strict 12-stuck packing was found at any side below 4** (`strict_ok` never true).  Near 4
the residual is of the order of the margin itself (0.35 delta), i.e. the obstruction has gone; at
s-hat and below it is four orders of magnitude larger.  Caveat: at 3.82 the side is at the
certified LOWER bound for s(11), so part of that residual is the packing being infeasible, not the
cells; s-hat and 3.95 carry packings and are the honest readings.

**[M] The 4-STUCK control** (corner boxes only, A217's condition) is run through the SAME optimiser
and verifier; see `results/twelve244.md` s.1 and s.3.  A217's published four-crowd threshold
4.0013 was measured at crowd margin 0.02 on a vertex-based row, so it is an upper bound for the
depth-based condition; the control here separates the two.

**[M] None of them is LOCKED.**  On every 12-stuck candidate the FREE Fritz-John system (walls and
contacts only, no crowd rows; `stress244` on A217's `opt217`/`stress217`) is INFEASIBLE -- least
residual 1.28e-2 over the candidates -- and no candidate has all of its cell meeters loaded.  The
12-stuck packings are held at their side by the artificial crowd rows alone.  This is the same
reading A239 got on all twelve rings below 4, and it answers the brief's secondary question: NO,
for everything found.

## 3. Why the window is where it is (`code/hand244.py`, `results/hand244.json`)

**[M] How many of the twelve cells can ONE unit square meet?**  Exhaustive over a 181 x 181 x 181
grid in (c_x, c_y, theta):

| side s | 3.82 | 3.877084 | 4.0 | 4.2 | 3 + sqrt2 = 4.414214 | 4.6 |
|---|---|---|---|---|---|---|
| max cells met | **5** | **5** | **4** | **4** | **3** | **3** |

with witnesses BL00 BL01 BL10 BR10 TL01 (below 4: a square at the BL corner still reaches the
NEXT corner's floor slot and the next corner's wall slot), BL01 TL00 TL01 TL10 (at 4 and 4.2: the
three cells of one wall plus the neighbouring top-wall slot) and BL00 BL01 BL10 (at and above
3 + sqrt2: only its OWN corner's triple).  So the reach falls monotonically as s grows, and the
last drop is exactly at **s = 3 + sqrt2**:

**[T] Lemma CROSS-CORNER-REACH** (n-general, any n, any side).  A square with a point in a corner
box c00 (u < 1 in the wall's coordinate) and a point in the FAR slot of the same wall (u > s - 2)
has extent > s - 3 along that wall; a unit square has extent <= sqrt2 in every direction; so for
**s >= 3 + sqrt2 = 4.414214** no square meets both, i.e. no wall slot can be supplied by the
ADJACENT corner's meeter.  (The same computation kills the c'00-meets-c01 form.)  This is the
upper end of the twelve-cell window: A217's own four-crowds are 12-stuck up to side 4.391318 and
no further, 0.023 below the bound.

**[M] A corner is NOT SELF-SUFFICIENT.**  Can two DISJOINT unit squares in the quadrant each meet
all three cells c00, c01, c10 of one corner?  ONE square can (penalty 0 at every margin tested;
a square straddling the frame point (1,1) meets all three).  TWO cannot, to any positive depth:
1500 L-BFGS restarts of the six-variable penalty give best value 3.339e-07 at margin delta = 1e-3
and 3.359e-13 at delta = 1e-6 -- exactly proportional to delta^2, i.e. the achievable common
depth is **0**, the two squares can at best TOUCH the three cells.  [S] proof route: both squares
meet the three quadrants Q1 = {u<1,v<1}, Q2 = {u<1,v>1}, Q4 = {u>1,v<1} around the frame point
(1,1); a separating line of the two must then itself meet all three cells, which forces it to run
up-left through the corner box, and the unit-square constraint must be brought in to finish
(obligation O-NO-SELF-SUFFICIENT).

**The consequence.**  Each corner's two slot-meetings cannot both come from its own two meeters
with room to spare, so under SLOT-MET the second meeter of a slot is (a) the adjacent corner's
meeter -- dead for s >= 3 + sqrt2 by CROSS-CORNER-REACH -- (b) the corner's own other meeter, or
(c) one of the three free squares, which is A243 s.4's list.  The twelve-cell condition therefore
lives in a WINDOW of sides, bounded above by the reach and below by the measurement of s.2, and
that window does not reach down to s-hat.

## 4. What this does and does not say about k0

**The PI's worry is answered, and the answer is the reassuring one for the HYPOTHESIS and the
unwelcome one for a cheap kill.**  A 12-stuck four-crowd IS constructible: 282 of A217's own 1217
feasible four-crowds already have all twelve border cells doubly met, and the campaign certifies
one at a side just above 4.  So A243's Lemma WALL-SLOT + SLOT-MET does NOT make STUCK-4(11)
vacuous by non-existence of the configuration type: 12-STUCK is a real class, it is only EMPTY in
the window.

**What it does say.**  Reading the measurement as evidence for the k0 statement: over the whole
window [3.82, s-hat] the twelve-cell condition fails by a LARGE margin -- the least residual the
fixed-side probe reaches is of order 1e-2, not 1e-6 -- while just above 4 it is satisfied with a
certificate.  In other words the boundary of the 12-stuck class sits at the TRIVIAL SIDE 4, the
same place A217 found the four-crowd boundary (4.0013 at crowd margin 0.02), and the window is
nowhere near it.  That is exactly the conclusion A242's cascade would have to prove -- and the
measurement says the conclusion is true with roughly 0.12 of side to spare, which is why the
cascade's leaves keep returning UNDECIDED rather than DEAD: they are being asked to certify
something that is true but not LOCALLY visible.

**What it does not say.**  (i) It is a SEARCH.  A side at which the search found nothing is a side
at which the search found nothing; nothing here is a proof, and the note never calls the threshold
one.  (ii) None of the 12-stuck packings found is LOCKED: on every candidate the FREE Fritz-John
system (walls + contacts, no crowd rows) is infeasible, best residual 1.28e-2, and no candidate
has all of its meeters loaded.  They are held at their side by the crowd rows alone -- the same
reading A239 got on all twelve rings below 4.  So the secondary question ("is any 12-stuck packing
LOCKED?") is answered NO for everything this campaign found, which is consistent with, and no
stronger than, LOCKED-CROWD-FREE(11).  (iii) The one place this could become a proof is s.3: the
two structural facts there (CROSS-CORNER-REACH [T], NO-SELF-SUFFICIENT-CORNER [M]/[S]) are
n-general and cheap, and together with SLOT-MET they reduce the supply of every wall slot to A243
s.4's three cases with the ADJACENT case dead above 3 + sqrt2 -- but inside the window the
adjacent case is alive, and the argument still needs the room statement that A237/A242 could not
supply.

## 5. Reproduce / resume

```
bash attempts/A244-twelve-stuck/code/run244.sh test          # the self-tests
bash attempts/A244-twelve-stuck/code/run244.sh A [WALL]      # structure + the descent lane
bash attempts/A244-twelve-stuck/code/run244.sh B [WALL]      # the fixed-side probe lane
bash attempts/A244-twelve-stuck/code/run244.sh pages         # summary + the two pages
# stop:   touch attempts/A244-twelve-stuck/logs/STOP
# resume: rm attempts/A244-twelve-stuck/logs/STOP   then lane A and lane B again
```
