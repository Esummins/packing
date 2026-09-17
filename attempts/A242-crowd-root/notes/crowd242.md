# STUCK-4(11) by certificate: the k0 cascade from the CROWD ROOT H_B, its three leaves, and the price — A242, 2026-09-16

The PI (15:00): *"given those results, is there any way we can show that no stable k0 packing exists below the
trivial side?"*  STUCK-4(11) is that question made exact: **no teleport-stuck (all four corner boxes doubly met)
LOCKED packing of eleven unit squares has side < 4** — "stable" = LOCKED = retreat-free, A233's word
(`local_lock.md` §1.1; rattler meeters are excluded because a strictly opening first-order motion IS a retreat).
This file states the root, proves the leaves' soundness with citations, records the one theory question the brief
asked to be escalated rather than guessed (box-valid FJ certificates), and prices the cascade from the cells it
actually ran.  Tags: [T] proved, [S] routine given cited items, [M] measured, [C] obligation, [Q] theory question.
Sources: `k0_route.md` §3–§4.4 (K0-FREE, K0-WIDEN, K0-BLOCKED, K0-PAIR, the pair census), `local_lock.md` (LOCALITY,
RADIAL, CHAIN, LOCKED-CROWD-FREE), `wedged_seal.md`, `attempts/A239-rings-below-4/notes/rings_below_4.md` (REACH,
GEAR-RATIO, LEVER), `noroom.md` (ROT; A189 Lemma 1), `pocket_waste.md` (PIERCE), `ring_capacity.md` (NO-CLOSURE),
`local_certificate.md` (Theorem LOCAL, Lemmas COVER / LEAF / RELAX), `lockfree.md` (ROT-W, LINE), A171/A172
(multibox, K'), A209 (CN), A221 (POCKET-DEAD, POCKET-INHERIT), A185 (cell format), A211 (bisection).
Code `attempts/A242-crowd-root/code/` (`root242.py`, `leaves242.py`, `cascade242.py`, `verify242.py`,
`report242.py`, `pages242.py`, `run242.sh`); results `results/crowd242_<band>.jsonl`, `results/crowd242.md`;
pages `docs/residue_map/campaigns/A242-crowd-root/`; Lean `Statements/Open/Stuck4.lean`.

## 0. Verdict

> **[T] The route is sound and it is built; [M] it is not affordable, and the measurement says exactly why.**
> The CROWD ROOT `H_B` is a cell in A185's format over each of four side bands covering [3.82, 4) (§1), with the
> eight corner meeters boxed by Lemma K0-WIDEN + LOCALITY (i) and three anonymous free squares.  Leaf **L1 =
> NO-ROOM(m = 3)** over the eight meeters' CORES is sound for every packing, locked or not (§2), and it is the only
> leaf that can fire in the cascade as built.  **[M] L1 cannot fire until ALL EIGHT roles are at A60's working box
> scale** (centre width 0.15, ~13° tilt): the free region is the container minus the union of the cores, and a role
> whose box is coarse has an EMPTY core and contributes nothing — so the cascade is a PRODUCT over the four
> corners, not a sum.  That is A85 §4.2's `N_pair⁴/8` restated with the geometric leaf in place of the LP, now with
> a measured per-cell cost: **≈ 10¹⁷ cells and ≈ 10¹⁵ CPU-h** (§5).  The only kill the cascade produces at
> reachable depth is A171's **EMPTYBOX** pair leaf — the (C) rule of `k0_route.md` §4.2, a corner's two meeter
> boxes whose cores must overlap — which fires on a constant fraction of every level and never on the free squares.
>
> **[T] Lemma BOX-GORDAN** (§3) is the sound box-valid form of the FJ leaf L2, proved here in four lines: a
> constant separating vector `h` with `h·(−e) > 0` on the cell's corner-ward directions and `h·g ≤ 0` on a
> SUPERSET of the possible contact directions certifies that no configuration of the cell is W-HELD at that
> meeter, hence none is LOCKED.  **[Q] It is NOT licensed by Theorem LOCAL**, and nothing else in the lab licenses
> a box-valid FJ certificate: `local_certificate.md` proves exactly one box-valid form, an LP VALUE bound
> (`inf_θ v_λ(θ) > s0`) with Lemma COVER's selection split and Lemma RELAX's affine rows; ROT, ROT-W, LINE, RADIAL
> and A217's free FJ LP are all single-configuration statements, and the naive extension to a box is FALSE in the
> direction that matters (the active set GROWS as the pose moves, so an infeasible force system can become
> feasible).  BOX-GORDAN repairs that by over-approximating the active set; it is new, stated with its proof, and
> flagged as such rather than attributed to Theorem LOCAL.
>
> **[M] L2 is gated off by L1's own weakness, and the gate is the finding.**  A free square of unknown tilt
> contributes a contact normal of unknown direction, so the generator set is all of S¹ and no `h` exists — unless
> the cell already forbids a free square from touching the meeter.  The exact condition is
> `dist_inf(pocket, role box) > √2` (§3.2).  **On every cell decided so far the worst gap is 0**: the pocket that
> survives L1 is still the whole centre box.  L1 and L2 are therefore not independent leaves — **L2 can only act
> where L1 has almost closed**, which is the same product wall.
>
> **[T] L3 is DROPPED, and the reason is a quantifier, not a gap in A239.**  REACH / GEAR-RATIO / LEVER are proved
> for the TILT-MIN flat-meeter crowd under torque balance, and the "no along-wall holder" step needs Corollary
> CHAIN, whose hypothesis is NOCRIT-SEL — valid at the **Ψ-minimiser**, not at an arbitrary locked packing (§4).
> Used as a cell kill it would silently replace STUCK-4(11) by LOCKED-CROWD-FREE(11).  **That trade is worth
> making**: LOCKED-CROWD-FREE(11) still closes k0_00 for the value (Lean `psiMin_not_stuck`, `no_optimal_of_stuck4`),
> and it buys A239's whole toolkit as leaves.  Recorded as the recommended re-root for A243+.
>
> **[C] The one structural idea that would change the price** (§5.3): branch on the four corners' REACH SUMMARY —
> two numbers per corner, the crowd's extent along each of its walls — instead of on the eight pose boxes.  The
> projection is a sound cover (every crowd has a reach), it is 8-dimensional instead of 24-dimensional, and A239's
> REACH inequality is a kill EXPRESSED IN EXACTLY THOSE COORDINATES.  10⁸ cells instead of 10¹⁷.  The leaf would
> have to be the capacity/shape argument of A236/A237, not L1 (a reach box has no core).
>
> **k0_00 unchanged.**  `stuck4_eleven` is an axiom in Lean, with the consequence chain to k0_00 proved.

## 1. The root H_B

### 1.1 [T] The statement and what it covers

Fix a BAND `[m_lo, m_hi] ⊆ [3.82, 4)` and put `S := m_hi`.  For a packing `P` at side `m` in the band put
`λ := S/m ∈ [1, S/m_lo]` and `F := Δ_λ P`.  Lemma B.0 (`closed_disjoint_bridge.md`): `F` is a strictly disjoint
closed 11-family inside `[0, S]²` with positive wall margins.  **Lemma K0-WIDEN** (`k0_route.md` §4.1) is proved
there at `s0`, and its proof uses only `λ ≥ 1` and the container, so it holds verbatim with `S` in place of `s0`:
a square of `P` meeting `int B_c(m)` has its image meeting `int B_c^w(S)` with

    w = (λ_max − 1)(1 + √2/2),   λ_max = m_hi/m_lo.

**H_B(band)** is then, by **Lemma K0-BLOCKED (structure)** (`k0_route.md` §4.2): *F has, at each of the four
corners, two distinct squares meeting `int B_c^w(S)`; the four pairs are pairwise disjoint sets of squares (CC-1(ii)
with the widening: a unit square has diameter √2 < S − 2 − 2w, checked per band by `root242.band_ok`); so eight
distinct squares of F are localised to the four widened corner reach sets and three are free.*

| band | sides | S | λ_max | w | CC-1(ii) slack | role box `[1/2, 1+w+√2/2]²` |
|---|---|---|---|---|---|---|
| W | [3.8200, 3.877084] | 3.877084 | 1.014943 | 0.025510 | 0.412 | [0.5, 1.7326]² |
| B1 | [3.877084, 3.9200] | 3.920000 | 1.011069 | 0.018896 | 0.468 | [0.5, 1.7260]² |
| B2 | [3.9200, 3.9600] | 3.960000 | 1.010204 | 0.017419 | 0.511 | [0.5, 1.7245]² |
| B3 | [3.9600, 4.0000] | 4.000000 | 1.010101 | 0.017244 | 0.551 | [0.5, 1.7244]² |

Every teleport-stuck packing with side in [3.82, 4) lies in exactly one band, so **the four roots cover all of
"teleport-stuck k0 below 4"**.  (`W` alone covers the k0_00 window [3.82, ŝ]; the other three are what STUCK-4's
statement adds beyond the window.)

### 1.2 [T] The role box

In the frame of corner `c` a meeter `Q` of `F` has centre `z` with (i) `z_u, z_v ≥ h(θ) = w(θ)/2 ≥ 1/2`
(containment; F2 of `frame_census.md`) and (ii) a point `p ∈ Q` with `p_u, p_v < 1 + w` and `|p − z|_∞ ≤ w(θ)/2 ≤
√2/2`, hence `z_u, z_v < 1 + w + √2/2` (F1; `local_lock.md` §2.1 Lemma LOCALITY (i) with the widening).  Tilts are
taken mod 90°.  So `R_c^w ⊆ [1/2, 1 + w + √2/2]² × [0°, 90°)`, the root box of both of `c`'s roles.

### 1.3 [T] What the root does NOT use

* **WEDGED-SEAL / PUSH's floor–wall split** (`wedged_seal.md` §5) says that in a doubly-met corner neither meeter
  touches both walls, one touches at most the floor and the other at most the wall.  That is a statement about
  CONTACTS, and a meeter of a general (non-extremal) packing need not touch a wall at all; as a constraint on the
  pose box it is measure-zero and prunes nothing.  It is used only to justify the LABELLING of the two roles
  (A = the floor-side one, B = the wall-side one) and it enters L2's generator set, not the root.
* **ONE-TILTED / K0-PAIR (a)**: at most one meeter is axis-aligned — again a measure-zero box constraint at the
  root; it becomes a real prune only when a role box is inside the near-flush tilt bin.
* **The LOCKED hypothesis.**  L1 does not read it.  Therefore **every DEAD cell of the cascade kills every
  K0-BLOCKED packing of that cell, locked or not** — a stronger statement than STUCK-4 needs, and the same
  statement A103's Theorem NOROOM wanted.

### 1.4 [T] Symmetry: nothing is quotiented, and why

The two meeters of a corner are an UNORDERED pair, which looks like a free factor 2⁴ = 16, and D4 (Lemma K0-D4 (ii))
a further 8.  **Neither is taken.**  The pair prune "drop the child whose B box is lexicographically below its A
box" is sound only if the mirror cell `(P′, P)` is itself a cell of the tree whenever `(P, P′)` is dropped.  This
tree splits the WIDEST role of the whole cell, a rule that is not equivariant under the A ↔ B swap (its tie-break
prefers A), so the two roles of a corner can reach different refinement depths and the mirror need not exist: the
cover would have a hole, i.e. an unsound kill.  Splitting a corner's two roles in LOCKSTEP restores equivariance
and the factor 16; D4 needs orbit representatives on the four-corner product (A85 §4.2).  Both are recorded in
`root242.pair_order_ok` and are worth ×128 on a price that needs 10¹⁷ (§5).

## 2. [T] L1 — NO-ROOM(m = 3) over the cores

**The hypothesis of a cell**: eight distinct squares of `F`, one per role, with poses in the role boxes, and
`m = 11 − 8 = 3` further squares of `F`, anonymous, inside `[0, S]²`, all interiors pairwise disjoint.

**The over-approximation and its direction.**  A172's `K'(role)` is the intersection of the posed unit squares over
ALL poses surviving in the role's box, so `K'(role)` lies inside EVERY pose of that role (A132/A172, the fixed
point of `multibox.Node.normalise`).  Hence the three free squares have interiors disjoint from every `K'(role)`,
and the sound over-approximation of the free region is **the container MINUS THE CORES** — never minus the roles'
reach sets.  (A171's direction, and the brief's: a core is a subset of every pose, a reach set is a superset of
one; subtracting cores LOSES exclusions, which is the safe side.  Subtracting reach sets would be a kill from an
over-strong hypothesis.)

**The leaf.**
* **A189 Lemma 1** (`noroom.md` / `noroom189.py`): bisect the free square's (centre, tilt) space against the cores
  with multibox's exact dead test; every DROPPED piece is certified "every pose in it meets some core", so every
  free pose survives in the residue; rectangles `P_1..P_r` covering the residue's CENTRES give `m ≤ Σ_j LANE(P_j)`,
  and the cell is DEAD as soon as the right-hand side is `< m = 3`.
* **A221 Lemma POCKET-DEAD**: a pocket every pose of which meets a core holds no free centre; if every pocket is
  dead the cell has NO free square at all — DEAD for every `m ≥ 1`.
* **A209 Lemma CN** (`noroom221.cn_upgrade`, applied to the pockets that SURVIVE): pockets whose pairwise l-inf
  diameter is `< 1` hold at most one centre between them, so the group count bounds the number of free squares;
  group count `< 3` is DEAD.
* **A221 Lemma POCKET-INHERIT**: a child's roles have boxes inside its parent's, so its cores are LARGER and its
  free poses fewer — the parent's pockets cover the child's free centres and the child runs the cover on them with
  no fresh global bisection.  The cascade passes `alive` down every edge.
* **A171 EMPTYBOX** (the pair leaf): if `normalise` drives a role's box empty the cell's hypothesis is
  unsatisfiable — the (C) rule of `k0_route.md` §4.2 (two meeters of a corner whose cores must overlap).

Every verdict is one-sided: DEAD is a certificate for the cell, UNDECIDED says nothing.  The verifier clause and
the audit sampling are `code/verify242.py` (§6); the frozen verifiers are untouched.

## 3. L2 — the box-valid FJ leaf: what is licensed, what is not, and the gate

### 3.1 [T] Lemma BOX-GORDAN (proved here)

Let `C` be a cell and `r` a role at corner `c`.  Let `G(C, r) ⊆ ℝ²` contain every contact-force direction that can
act on role `r`'s square at ANY configuration of `C` (walls, the corner partner, the other roles, the virtual
corner row of ROT-GRAD — a SUPERSET of the possible active set), and let `E(C, r)` contain every corner-ward
direction `−e(z)` as `z` ranges over `C`.  **If some `h ∈ ℝ²` satisfies `h·d > 0` for all `d ∈ E(C, r)` and
`h·g ≤ 0` for all `g ∈ G(C, r)`, then no configuration of `C` is W-HELD at `r`; hence no configuration of `C` is a
LOCKED four-crowd, and `C` is DEAD for STUCK-4's hypothesis.**

*Proof.*  Fix `z ∈ C`.  The actual contact-force directions of the square at `z` form a subset `A ⊆ G(C, r)`, so
every non-negative combination of them lies in `{x : h·x ≤ 0}`.  The corner-ward direction `−e(z)` lies in
`E(C, r)`, so `h·(−e(z)) > 0` and `−e(z) ∉ cone(A)`.  By Lemma ROT-W's Farkas form (`lockfree.md` §1.2: W-HELD ⟺
the corner-ward unit force lies in the cone of the square's contact force directions, walls included) the square is
not W-HELD, so it admits a depth-decreasing translation with every active row rate `≥ 0`, i.e. it RETREATS
(`local_lock.md` §1.1).  ∎

### 3.2 [T] The gate, and [M] what it measures

If two unit squares touch they share a point `p`, and a unit square's body lies within l-inf distance
`w(θ)/2 ≤ √2/2` of its centre; so their CENTRES are within `√2` in l-inf.  Hence a free square whose centre lies in
a pocket `P` cannot touch the meeter of role `r` whenever `dist_∞(P, B_r) > √2`, with `B_r` the role's CENTRE box.
Both objects are supersets of what they stand for (A189 Lemma 1's pockets cover the free centres; `B_r` covers the
meeter's centres), which is the correct side for a "cannot touch" conclusion — the opposite of L1's cores.

Unless that holds for every role and every surviving pocket, an anonymous free square of unknown tilt contributes a
contact normal of **unknown direction**, `G(C, r)` is all of `S¹`, and no `h` exists.  **[M] On every cell decided
so far the gate reads 0** — L1's surviving pocket is still the whole centre box, which meets every role box.  So
L2 is not an independent leaf: it can act only where L1 has almost closed.

### 3.3 [Q] The theory question, escalated rather than guessed

`local_certificate.md` proves **one** box-valid certificate form: Theorem LOCAL, an LP VALUE bound
`inf_{θ∈K} v_λ(θ) > s0` per cell and per selection leaf, with Lemma COVER's finite selection split (Lemma SAT per
near pair) and Lemma RELAX's affine rows.  It is about SIDES, not FORCES.  Every force statement the lab has —
ROT, ROT-W, LINE, RADIAL, NO-SELF-STRESS, A217's free FJ LP, A239's gear and lever computations — is stated and
measured at a SINGLE configuration.  **No theorem in the lab licenses "the FJ system is infeasible at z*, therefore
it is infeasible on a box around z*"**, and the implication is false in the direction that matters: the active set
can GROW as the pose moves (a pair at positive gap can come into contact), and adding generators can only make the
cone bigger, so an infeasible force system can become feasible.  Lemma BOX-GORDAN is the sound repair because it
quantifies over a SUPERSET of the active set; it is new here and must be cited as A242's, not as Theorem LOCAL's.
Two obligations remain before it can be run: (i) an interval enclosure of `E(C, r)` (the argmin point, hence the
corner-ward direction, moves with the pose — ROT-GRAD's virtual row), and (ii) a proof that the enumerated
generator list is complete over the cell (it must include every wall row and every pair row whose gap enclosure
contains 0, i.e. `local_certificate.md`'s NEAR pairs).  Both are routine given Lemma RELAX's enclosures; neither is
done here.

## 4. [T] L3 — dropped, with the reason

The brief's L3 is: *a wall whose two crowds cannot span it in contact and whose gap admits no bridging interior
square leaves a corner meeter without its along-wall holder.*  Its two halves have different standing.

* The **span** half is A239's Lemma REACH: two TILT-MIN crowds close a wall of side `s` in contact iff
  `R(θ, δ) = cos θ + sin θ + δ − (δ − sin θ) tan θ ≥ s − 2`, and below 4 the residual gap is `< 1`, so a third
  member juts.  This is proved **for crowd type F** (a FLAT meeter at offset `δ` and a tilted partner in mode (a)) —
  the only crowd type with a flat meeter, by WEDGED-SEAL + ONE-TILTED + TILT-MIN.  A general cell of `H_B` contains
  two-tilted crowds, for which the note's own §1 says the inequality is vacuous below 4.
* The **holder** half needs Corollary CHAIN (`local_lock.md` §3): *the loaded component of a crowd reaches a far
  wall with load.*  CHAIN is derived from NOCRIT-SEL, whose hypothesis is that the packing is **Ψ-minimal**.  An
  arbitrary LOCKED four-crowd is not Ψ-minimal, so CHAIN is not available under STUCK-4's hypothesis.

Used as a cell kill, L3 would therefore silently replace STUCK-4(11) by its Ψ-minimal restriction.  **That is a
trade worth making, and it is the recommended re-root**: the Ψ-minimal restriction is exactly LOCKED-CROWD-FREE(11),
which still closes k0_00 for the value (Lean `psiMin_not_stuck`, `psiMin_singly_met`, `no_optimal_of_stuck4`), and
it makes A239's REACH / GEAR / LEVER and A233's RADIAL / CHAIN admissible as leaves.  It is not done here because
the change is to the ROOT's hypothesis, not to a leaf, and the brief's root is the stuck one.

## 5. The price

### 5.1 [M] What the cascade measured

See `results/crowd242.md` (regenerated by `code/report242.py` from the live jsonl).  Shape of the run: the DFS
splits the widest role of the cell; the only kills at reachable depth are **EMPTYBOX** (A171's pair leaf), which
fires when a corner's two roles are driven into the same sub-box; L1 returns UNDECIDED with exactly ONE surviving
pocket — the whole centre box — at every depth reached, and the per-cell cost climbs from ≈ 3 s at the root to
≈ 30–35 s by depth 16–20 as more roles acquire cores.

### 5.2 [T+M] The product law, and why L1 cannot fire early

L1's exclusions are the union of the eight cores.  A role whose box is coarse has an EMPTY core (A172's
intersection over the surviving poses is empty as soon as the box is wider than the square can tolerate), and
`mbpatch178`'s sound semantics make such a role clip nothing.  **So no subset of the eight roles can kill the
cell: all eight must be at A60's working scale simultaneously** (centre width 0.15, σ-closed tilt cell ≈ 90/7°).
From the root box (width ≈ 1.2326, tilt 90°) that is `2⌈log₂(1.2326/0.15)⌉ + ⌈log₂ 7⌉ = 11` binary splits per role,
`D = 88` in all: `2⁸⁸ ≈ 3·10²⁶` cells before pruning.  The pruned figure is independent and measured elsewhere:
A85 §4.4 counts `N_pair ≈ 3.4·10⁴` core-disjoint meeter pairs per corner at exactly that box scale, so
`N_pair⁴ ≈ 1.3·10¹⁸` four-corner cells, `≈ 1.7·10¹⁷` with the D4 quotient this cascade does not take.  At the
measured 30 s/cell that is `≈ 1.4·10¹⁵ CPU-h`.  **The cascade from `H_B` is not affordable by fifteen orders of
magnitude, and the obstruction is the PRODUCT over four corners — the same wall A85 §4.2 named ("N_pair⁴/8
four-corner nodes before any LP has slack"), now with the geometric leaf instead of the LP and with the constant
measured.**  The two symmetry quotients left on the table (§1.4) are worth ×128, i.e. nothing.

### 5.3 [C] The branching that would change the exponent

Branch not on the eight POSE boxes (24 real coordinates) but on the four corners' **REACH SUMMARY**: for each
corner `c`, the two numbers `R_c^u, R_c^v ∈ [1, 1 + √2]` giving how far the crowd extends along each of its walls.
Every crowd has a reach, so a grid of boxes in those 8 numbers is a sound COVER, and the cells are
`grid⁸ ≈ 10⁸` at grid 10 instead of `10¹⁷`.  A239's REACH inequality, GEAR-RATIO and LEVER are stated in exactly
those coordinates, and A236/A237's capacity and PIERCE act on the pocket the reaches leave.  What does NOT survive
the projection is L1: a reach box has no core, so the leaf must be the shape/capacity argument, not the no-room
cover.  This is the one design change A242 recommends; it is not a small edit to this code.

## 6. Files, verifier clause, obligations

* Root and branching: `code/root242.py` (bands, `w`, the role box, the split rule, the symmetry hooks).
* Leaves: `code/leaves242.py` (L1 wrapping A221/A189/A171 read-only; the L2 gate).
* Cascade: `code/cascade242.py` (DFS, per-cell jsonl + atomic stack, resume) and `code/run242.sh` (detached
  worker, `logs/STOP`, explicit-pathspec commits).
* **Verifier clause** (the frozen verifiers are untouched; the new leaves get their own): `code/verify242.py` —
  clause L0 (EMPTYBOX: rebuild and re-raise) and clause L1 (re-decide with a fresh budget and no inherited
  pockets), plus an AUDIT that is independent of the clip machinery: random free-square poses in the container's
  centre box are tested against the roles' `K'` polygons with a plain shapely intersection, and any pose that
  meets no core and lies in no surviving pocket is reported as a falsifier.
* Pages: `docs/residue_map/campaigns/A242-crowd-root/{crowd_root,cells_W,cells_B3}.svg`.
* Lean: `Statements/Open/Stuck4.lean` — `stuck4_eleven` (axiom [C]) and the consequence chain
  `locked_crowd_free_eleven`, `psiMin_not_stuck`, `psiMin_singly_met`, `no_optimal_of_stuck4` (theorems, 0 sorry).
* **[C] obligations**: STUCK-4(11) itself; BOX-GORDAN's two enclosures (§3.3); the reach-summary cascade (§5.3);
  the lockstep + D4 quotients (§1.4).

## 7. Addendum (PI, 15:40) — "no ring constructable below ŝ", i.e. L1 alone and the UNLOCKED form

*"Is it possible to show that no ring is constructable below ŝ, so no fully pinned k0 configuration exists below
ŝ?"*  The PI's point is exactly right about the leaf: **L1 reads no lock and no force hypothesis.**  Its whole
content is "the container minus the eight meeters' CORES, against three free squares" (§2), so a cell L1 kills is
killed for every packing of that cell — locked, rattling or neither.

**[T] What L1 alone would prove.**  If the cascade closed a band with L1 only, the theorem is the UNLOCKED form

> **STUCK-4-UNLOCKED(11):** no packing of eleven unit squares at a side in that band is teleport-stuck
> (all four corner boxes doubly met),

Lean `stuck4_unlocked_eleven`.  With K0-FREE (`k0_route.md` §3) it closes k0_00 **directly** — `link` teleports the
singly-met corner into a corner slot square at the SAME side and (k1-a) kills that — with no minimiser selection,
no Ψ-minimality and no A233: Lean `not_stuck_of_unlocked`, `no_packing_of_stuck4`.  A233 is needed only for the
weaker LOCKED form (`stuck4_eleven` → `psiMin_not_stuck` → `no_optimal_of_stuck4`).  Both are axioms in
`Statements/Open/Stuck4.lean` with the implication `stuck4_of_unlocked` proved; the cascade closed no band, so
neither is discharged.

**[M] L1 alone, over the window [3.82, ŝ] (band W) and at the top of the range (band B3).**  Both ran; see
`results/crowd242.md`.  Every kill is A171's EMPTYBOX pair leaf (a corner's two roles driven into boxes whose cores
must overlap — `k0_route.md` §4.2's (C) rule); **L1's no-room cover has not killed one cell**, and the reason is
§5.2's product law, visible directly in the audit (`results/audit242_W.json`): the number of roles with a NON-EMPTY
core is `0` at the root, `3` at depth 6, `6` at depth 12 — a cell needs all eight, and the free-pose sample that
survives the cores only falls from 2501/3000 to 693/3000 over those twelve splits.

**[M] Per surviving cell: the capacity and the poses** (the addendum's two asks; table in `results/crowd242.md`).
* **Capacity.**  At every cell reached, L1's cover leaves exactly ONE pocket — the whole centre box `[1/2, S−1/2]²`
  — whose l-inf diameter exceeds 1, so A209's Lemma CN returns no bound and the capacity is **≥ 3 (undecided)**.
  Not one cell has reached capacity 2 or 1.  This is the sharpest statement of the wall: the leaf that A239
  measured to give capacity 1 on a CONSTRUCTED ring (a single configuration, where the meeters are points in pose
  space) gives nothing at all on a CELL whose role boxes are 0.6 wide and 45–90° tall.
* **The poses.**  The role boxes of the surviving cells are still the first DFS spine — all the "lower half"
  children — so their corner-frame ranges (`u`, `v` = the centre's distance from the corner's two walls) are the
  crude halves `[0.50, 1.12]` / `[1.12, 1.73]` with tilt ranges still 45–90° wide.  **No cell has yet been refined
  enough for the question "are these the deep, corner-wasting poses?" to have an answer**: a box spanning
  `u ∈ [0.5, 1.12]` contains both the flush-in-the-corner meeter (`u = 0.5`) and the pose that wastes most of the
  corner.  Answering it needs the reach-summary coordinates of §5.3, where `u`, `v` ARE the branching variables —
  another reason to re-root there.

**[F] So the PI's question is not refuted, and it is not reachable from this root.**  "No ring below ŝ" in the
UNLOCKED form is the strongest statement A242's machinery could in principle deliver, its leaf is sound and
implemented, and the measured obstruction is entirely the branching: 10¹⁷ cells because the eight meeters are
refined independently.  The recommendation is unchanged and now doubly motivated (§5.3, §4): re-root on the four
corners' REACH SUMMARY, where A239's own inequality is the leaf and the capacity question is a coordinate.
