# A118 — LANE-COUNT: the leaf, exactly; what it is sound for; what it is not

## 0. Discipline

* READ-ONLY on every campaign (`A57`, `A60`, `A61`, `A85`, `A96`, `A99`, `A38`, `A107`, `A114`):
  every node json is read, none is written, no campaign process was started, stopped or re-niced.
  All writes are under `attempts/A118-lane-count/**`, plus the registry row, `LOG.md` and one
  note field on the A57 depgraph node.
* `verify_case.py` copied byte-identical from the frozen file:
  `sha256 = 521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`
  (same file as A53/A57/A94/A109).
* At most 2 A118 python processes, BLAS pinned to one thread (`blas1` imported before numpy in
  every entry point); `PYTHONDONTWRITEBYTECODE=1`; no recursive deletes.
* Every tilt interval is normalised to `[0, 90]` (asserted), every core half-side asserted
  `<= 1/2` (asserted), and every tolerance is in the KEEP direction — `R(C)` is only ever
  enlarged, which is the sound direction for an UPPER bound on `LANE`.

## 1. The leaf

Fix a Young class `S` with pin set `P_S`, and a cell `p` of a corner `c` at offsets `(i, j)`:

* **pinned classes** — `p` an UNCLIPPED COMPLETABLE slot of `S` whose extension class
  `T = S u {p}` is certified dead on a window `W_T` containing the node's sides
  (`docs/proofs/slot_crowds.md` §1.2, §2);
* **k0_00** — `p` a corner cell, `T = k1_00` (`docs/proofs/k0_route.md` §3).

Work in `c`'s CORNER FRAME `(u, v) = (x or m-x, y or m-y)`, in which the cell is exactly
`C = [i, i+1] x [j, j+1]` **at every side m** — the frame is anchored to `c`'s two walls, so the
cell, the depth functional and Lemma CONT are all `m`-free there.

    R(C) := { poses (u, v, theta) of a unit square Q :
                Q subset [0, s0]^2                                  (container; m <= s0)
                int Q  meets  int C                                 (the leaf's "meets")
                Q  disjoint from  R_p = {u'<0, v'<1} u {v'<0, u'<1} (Lemma CONT)
                int Q  disjoint from every hypothesis core }

    LANE(C) := max # of PAIRWISE interior-disjoint unit squares with poses in R(C)
    M(C)    := # of the node's conditioned squares that can meet int C

> **LEAF (LANE-COUNT).** If `LANE(C) + M(C) <= 1` then no packing of class `S` at any side of the
> node's side interval realises the node's hypothesis: the node is DEAD BY TELEPORT.

*Proof.* Let `P` be such a packing. Lemma SLOT-CROWD (pinned classes) / Lemma K0-FREE (k0) gives
`>= 2` NON-PIN squares of `P` meeting `int C`. Each is a conditioned square of the node (at most
`M(C)` of those can meet `int C`) or a free one. A free one is a unit square inside `[0, m]^2`,
interior-disjoint from every pin square (hence from every pin core) and from every conditioned
square (hence from every conditioned core), it obeys Lemma CONT (it is a non-pin square of a
packing containing `P_S`), and it meets `int C`: its pose is in `R(C)`. Free squares are pairwise
interior-disjoint, so there are at most `LANE(C)` of them. Hence `2 <= LANE(C) + M(C) <= 1`. ∎

`LANE(C) = 0` (i.e. `R(C) = {}`) is the strongest and, empirically, the ONLY form that fires.

### 1.1 Why the leaf runs on the ORIGINAL packing, not on the dilated family

A57's node hypothesis is stated at `s0` for the DILATED family `Δ_λ P`, `λ = s0/m`. One may
either (a) run the count in that frame against the widened crowd family `F_p(a_w)`, or (b) pull
the hypothesis back and run the count on `P` itself. **(a) is structurally vacuous and (b) is the
leaf.**

* **(a) is vacuous.** The licensed pad on A57's G1 slab is `a_w = 1` EXACTLY: with every
  extension now FULL on the closed window, SLOT-SLIDE's depth credit `d = s0 - m` and Lemma
  B-YES-S's dilation pad cancel, and `sup_m [λ(1-d) + (λ-1)(1/sqrt2 + max(i,j))] = 1`
  (A109 `aw_check`, exact). But `F_p(1) = {mu_p <= 1}` contains the whole **grazing staircase**:
  a square sitting in the arm `{u' <= 0, v' in [1, 2]}` has `mu_p = 1` exactly, obeys Lemma CONT,
  touches no core, and is disjoint from a square sitting in the cell — so `LANE >= 2` for
  structural reasons at EVERY node. Measured directly: with `a_w = 1 + 1e-5` the refinement never
  closes, and the sampler's witnesses are exactly the grazing arm. The pad that makes the
  transfer sound is precisely the pad that destroys the count.
* **(b) is sound and sharp.** SLOT-CROWD's teleport happens in `P`, at side `m`, with EXACT pins;
  it is `P`'s cell `B_p(m)` that must be met by `<= 1` non-pin square. Pulling the node's
  hypothesis back costs only interval widening: a world box `[x0, x1]` at `s0` is the image of
  `[x0 m/s0, x1 m/s0]` at side `m`, and a census slot is `a + b m` with `b in {0,1}` — every
  position is AFFINE in `m`, so the hull over `m in [m_lo, s0]` is the hull of the two endpoints,
  exactly. On A57's G1 slab (`m_lo = 3.8616374951330865`) the widening is `<= 0.0155`; for A60's
  fixed-side-`s0` cover it is 0 and the pin cores are the FULL unit squares.

### 1.2 Certifying `LANE(C) <= 1`

A finite box cover `B_1, ..., B_N` of `R(C)` (rational endpoints, tilt in `[0, 90]`) with:

* **(i) COVER** — every grid cell NOT in the list is discharged by one of three interval
  inequalities: the square leaves the container for every pose; the square misses the cell for
  every pose (a separating axis certified over the box); every pose overlaps a hypothesis core
  (**T5**, the tight common-inscribed core `K_B` meeting the core, OR **T5''**, the octagon
  box-vs-core test). Lemma CONT contributes a fourth: every pose crosses a backed side.
* **(ii) PAIRWISE** — for every `a <= b` (the diagonal included: two squares from the same box),

      max_{d in D(B_a, B_b)} |d|  <  1/2 + 1/2 * min_{Δ in [th_b] - [th_a]} (|cos Δ| + |sin Δ|)

  where `D` is the interval hull of the centre difference. This certifies that NO separating
  axis exists for any pose pair (`|n . d| <= |d|` for every unit `n`, and the support of a unit
  square along any axis is `(|cos|+|sin|)/2 >= 1/2`), i.e. the two squares always overlap. It is
  the octagon/Minkowski test of T5'' with a bin in place of the pin, and it is strictly stronger
  than the core-vs-core screen (Lemma TC), which needs `|d| < ~0.7` where this needs `|d| < 1`.

`LANE(C) = 0` is `N = 0`. If some pair fails (ii) the offending boxes are bisected and the cover
re-pruned; if a concrete disjoint pose pair is realised inside two of them, `LANE >= 2` with two
explicit witnesses; if the box budget runs out the verdict is UNDECIDED (never a kill).

**Confirmation.** Every `LANE <= 1` verdict is re-sampled INSIDE the certified cover until
`>= 10^4` pose pairs have been drawn from `R(C)`; the kill is only booked if none of them is
interior-disjoint (`max_gap < 0` reported per kill). A cover that realises no pose at all is
reported as such.

## 2. What the leaf is sound FOR (A118-O1, the one honest caveat)

A LANE-COUNT leaf excludes the dilated images of **class-`S` packings** (exact pins at
`slot_j(m)`). A57's LP leaves exclude more: the whole `delta = 10^-2` SLACK-PIN family at `s0`
(Lemma B'). The composition A57 needs is unaffected — the tree is a cover of the CONDITIONED
square's parameter box, every class-`S` image lands in some leaf, and every leaf is empty of
class-`S` images, so the tree still proves "no class-`S` packing at any side of the slab". But a
LANE-killed leaf may NOT be re-used for the broader slack statement (`lemmas.md` T23's
"every packing whose pins are within 7.07e-3 of the slots"). If that broader use is wanted, the
leaf must be re-derived with slack pin cores AND the extension class killed in slack form.

## 3. Usable slots, as of 2026-09-06

Read from `attempts/A56-sparametric/results/scoreboard.json` (A56 + A61 + **A114**). Every
extension below is now **FULL `[191/50, 969271/250000]`**, the CLOSED window — which also
discharges **A109-O1** (SLOT-CROWD at the slab's top endpoint `m = s0` needs the extensions dead
AT `s0`, not merely below it).

| class | usable cells | extension |
|---|---|---|
| k5_11 | BL(1,1), BR(0,1), TL(1,0), TR(0,0) | k6_18, k6_20, k6_20, **k6_23 (A114)** |
| k5_16 | BL(1,0), BR(0,1), **BR(1,0)**, TR(0,1), TR(1,0), **TL(1,0)** | k6_23, k6_29, **k6_27 (A114)**, k6_30, k6_28, **k6_27** |
| trump5 | BL(0,2), BL(1,1), **BR(0,1)**, TR(0,1), TR(1,0), TL(0,0) | **k6_07 (A114)**, k6_19, **k6_21 (A61)**, k6_22, k6_24, **k6_23** |
| k0_00 | BL(0,0), BR(0,0), TR(0,0), TL(0,0) | k1_00 — **OPEN** (`k0_route.md` §3): every k0 verdict here is CONDITIONAL on k1_00's tree |

`slot_crowds.md` §1.2's table is superseded: k5_16 gains BR(1,0) and TL(1,0) (m_u 4 -> 6) and
trump5 gains BR(0,1) and BL(0,2) (m_u 4 -> 6).

## 4. Canaries (`results/canary118.json`, all PASS)

* **C1** the corner/slot frames reproduce `slot_crowds.md` §7's exact Trump depths at all six
  unclipped trump5 slots to `< 5e-7`, with the same two witnesses each.
* **C2 (the brief's Trump canary)** at the trump5 ROOT the leaf returns `LANE >= 2` at every one
  of the six usable cells — including **BL(0,2)** (Trump's upright sq4 at depth 0.967 and sq7 at
  0.016) and **TL(0,0)** (sq6 0.168, sq4 0.155) — and Trump's OWN pair is in `R(C)` and
  interior-disjoint in each case (`pair_gap >= -0.0`). Nothing of trump5 fires at the root.
* **C3** positive/negative control of the machinery: a cell boxed in by eight blockers certifies
  `LANE <= 1` (8 boxes, 12 561 confirmation pairs, `max_gap = -0.903`); the same cell with the
  blockers removed returns `LANE >= 2` with witnesses.

## 5. T4 — the reversed leaf (pair-box branching)

The split `(>= 2 non-pin squares meet C) OR (<= 1 meets C)` is tautologous and the second branch
is the T1 leaf: FREE, no LP, no certificate. The first branch is covered by
`child(a,b) = parent + core(B_a) + core(B_b)` at `budget - 2`, one child per unordered pair of a
box cover of `R(C)` (boxes emitted in A57's world frame at `s0` through the dilation, so
`pinguard`, `Box.core`, the tight core and the octagon tests apply verbatim; pairs de-duplicated
by the class stabiliser that fixes the cell — the main diagonal for k5_11's BL(1,1)/TR(0,0),
identity otherwise). Free kills at the pair level: `core(B_a)` meets `core(B_b)` (Lemma TC
between the two bins) or the octagon pair test of §1.2(ii); per-box kills: T5/T5'' against the
pins, and `pinguard` 'parent' boxes are booked UNSOUND-AT-REDUCED-BUDGET, never certified.
