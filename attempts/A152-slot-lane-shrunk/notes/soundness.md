# A152 T1 — the refined slot-lane leaf: the exact statement, a counterexample, and the repair

Everything below is in the cell's **corner frame** at side `m` (A118 §1: `(u, v) = (x or m−x,
y or m−y)`, so the corner's two backed walls are `u = 0` and `v = 0` and the cell is
`C = [i, i+1] × [j, j+1]` at every `m`).  `δ` is the pin slack of the class family and

    h := δ / √2 = 7.0710678…e-3            (δ = 10⁻², A57 `tree57.build_children`, lemmas.md T23)

is the **half-width of the pin box**: a square is "pinned at slot σ" iff its centre lies in
`σ + [−h, h]²` and its tilt is 0.  A57's G1 tree conditions on this slack family; A60's
`deepen.py` pins are DEGENERATE (`Box(x, x, y, y, 0, 0)`), i.e. exact.

---

## 1. What A141's leaf actually is

`docs/proofs/slot_crowds.md` / A118 §1, in the teleport form (which is the form the refinement
generalises, and is equivalent to the SLOT-CROWD counting form):

> **LEAF (A141, `polycore_slot_lane_v1`).** Let `p` be an unclipped completable slot of class `S`
> and `C` its cell.  If at most one NON-PIN square of the packing meets `int C`, delete that
> square and put a unit square exactly on `C`.  The result is a packing of class `T = S ∪ {p}`
> with **exact** pins, contradicting the A56/A61/A114 window kill of `T`.
> `LANE_K′(C) + M(C) ≤ 1` is the certified sufficient condition for the hypothesis.

Two exactness assumptions are buried here, and both are A118-O1:

* the snapped square is placed **exactly** at the slot, so `T` must be dead with exact pins;
* the five existing pins are treated as **exact** obstacles (A141 builds the pin `K′` from
  `lane.cframe_boxes`'s *m*-hulled slot box, which for a near-wall pin is a POINT and whose `K′`
  is therefore the FULL unit square).  Under the `δ = 10⁻²` family the true obstacle is the
  smaller core of the fattened box, half-side `½ − h = 0.49293`.

---

## 2. The refined leaf, stated exactly

**Definition (admissible translate).**  `t ∈ ℝ²` is *admissible* for the slot `p` of the node iff

* **(T0)** `|t|_∞ ≤ h` — so a square placed at `C + t` is a legal pin of `T` in the δ-slack family;
* **(T1)** `C + t ⊆ [0, m]²`;
* **(T2)** `int(C + t)` is disjoint from every position any pin of `S` may occupy, i.e. from
  `σ + [−½−h, ½+h]²` for every pin slot `σ` of `S` (with `h = 0` for A60's exact pins).

Write `A` for the set of admissible translates.  `A` is a (possibly empty, possibly degenerate)
convex subset of `[−h, h]²`; `code/lane152.admissible_translates` returns its corner points on the
`{−h, 0, h}²` grid, which is a sound sub-selection.

**Lemma SNAP-t.**  Fix `t ∈ A` and let `n_t` be the number of non-pin squares `Q` of the packing
with `int Q ∩ int(C + t) ≠ ∅`.  If `n_t ≤ 1` then there is a packing of 11 unit squares in
`[0, m]²` whose six pins are the five pins of `S` (unchanged) together with one square exactly on
`C + t`, whose centre is therefore within `h` of the slot `p`.

*Proof.*  Delete the unique meeter (if `n_t = 0`, delete any non-pin square — there are six), and
place a unit square on `C + t`.  It lies in the container by (T1), is interior-disjoint from every
pin by (T2), and is interior-disjoint from every remaining non-pin square because those miss
`int(C + t)`.  ∎

> **REFINED LEAF (`polycore_slot_lane_shrunk_v1`).**  If for SOME `t ∈ A`
>
>     LANE_K′(C + t) + M(C + t) ≤ 1
>
> and the extension class `T = S ∪ {p}` is certified dead **in the δ-slack-pin form** on a window
> containing the node's side range, then the node is DEAD.

`LANE_K′` and `M` are A141's, verbatim, with the rectangle `C` replaced by `C + t` — and, for a
slack-pin family, with the pin obstacle cores rebuilt from the FATTENED pin boxes (§5).
`n_t ≤ LANE_K′(C+t) + M(C+t)` because every non-pin square is either conditioned (at most `M` of
those can reach the cell) or free and pairwise interior-disjoint (at most `LANE_K′`).

---

## 3. The PI's "shrunk cell" is NOT this leaf, and is unsound

Let `C_h := C ⊖ [−h, h]² = [i+h, i+1−h] × [j+h, j+1−h]` — the slot's *core*, the exact analogue of
the pin core.  The proposal is: *meeter := intersects `C_h`.*

**The blocked-translate set.**  For a square `Q`, the translates it forbids are

    B(Q) = { t : int(C + t) ∩ int Q ≠ ∅ } = int( Q ⊕ (−C) ),

an OPEN CONVEX set (Minkowski sum of two convex sets).  A snap exists iff some `t ∈ A` lies in at
most one `B(Q)` (the one square we are allowed to delete).

**What "misses `C_h`" buys — and only that.**

> **Sub-lemma (one square).**  If `int Q ∩ int C_h = ∅` then some `t ∈ [−h, h]²` has `t ∉ B(Q)`.
>
> *Proof.*  `Q` and `C_h` are disjoint convex compacta, so a unit `ν` separates them:
> `sup_{C_h} ν·x ≤ inf_Q ν·y`.  For a box, `h_C(ν) = h_{C_h}(ν) + h‖ν‖₁`, so the corner
> `t_ν := −h·sgn(ν)` (componentwise, `|t_ν|_∞ = h`) gives
> `sup_{C+t_ν} ν·x = h_C(ν) + ν·t_ν = h_{C_h}(ν) ≤ inf_Q ν·y`, i.e. `C + t_ν` and `Q` are
> separated by `ν`.  ∎

The escaping corner `t_ν` **depends on `Q`**.  Since `C_h ⊆ C + t` for every `|t|_∞ ≤ h`, the
shrunk-cell count satisfies `#meeters(C_h) ≤ n_t` for EVERY `t` — the inequality points the wrong
way, and no union bound repairs it:

> **COUNTEREXAMPLE (four grazers).**  `C = [0,1]²`, `h` any value in `(0, ½)`.  Put
>
>     Q₁ = [−1+h/2, h/2] × [−½, ½]        (enters C through the left face by h/2)
>     Q₂ = [1−h/2, 2−h/2] × [½, 3/2]      (through the right face)
>     Q₃ = [−½, ½] × [1−h/2, 2−h/2]       (through the top face)
>     Q₄ = [½, 3/2] × [−1+h/2, h/2]       (through the bottom face)
>
> These are four unit squares, **pairwise interior-disjoint** (each pair is separated on one axis:
> `Q₁|Q₃` and `Q₂|Q₄` on `y`, `Q₁|Q₂`, `Q₁|Q₄`, `Q₂|Q₃`, `Q₃|Q₄` on `x`), **each meets `int C`**,
> and **each misses `C_h`** (their incursions live in the strips `x ≤ h/2`, `x ≥ 1−h/2`,
> `y ≥ 1−h/2`, `y ≤ h/2`, all strictly inside the eroded margin `h`).  So the shrunk-cell meeter
> count is **0** — the proposed leaf fires.
>
> But `Q₁` blocks `t` iff `t_x < h/2`, `Q₂` iff `t_x > −h/2`, `Q₃` iff `t_y > −h/2`, `Q₄` iff
> `t_y < h/2`.  Every real `t_x` satisfies `t_x < h/2` or `t_x > −h/2`, and likewise for `t_y`, so
> **every `t` is blocked by at least two of the four**.  Deleting one square is not enough: there
> is no admissible placement of the sixth pin, and the packing is not in the slack stratum of `T`.
> ∎
>
> **Machine-checked** in exact `Fraction`s at `h = δ/√2`: `code/t0_counterexample.py`,
> `results/t0_counterexample.json` — all unit / pairwise-disjoint / meets-`C` / misses-`C_h`
> checks pass, and over a 129 × 129 rational grid of `[−h,h]²` refined at the switching points
> `±h/2` the MINIMUM number of blockers is **2**.

So the PI's step "*the grazers leave a free translate*" is false as an unquantified union
statement.  It is true for one grazer, and false from four; with two or three grazers the leaf can
still be rescued by deleting the right one, which is exactly the `n_t ≤ 1` bookkeeping of §2.

**Consequence.**  `C_h` may be used as a *screen* (a square meeting `C_h` meets every `C + t`, so
`#meeters(C_h)` is a valid LOWER bound on `n_t` and a `#meeters(C_h) ≥ 2` reading rules the leaf
out cheaply) but never as the leaf's meeter test.  A152's records carry the shrunk-cell row as a
**diagnostic** and never emit a certificate from it.

---

## 4. Why the sound form is nevertheless VACUOUS on this corpus

**Proposition (backing).**  Let `p = (i, j)` be a *completable* slot of a Young down-set class `S`.
Then each of the two predecessor cells `(i−1, j)` and `(i, j−1)` is either off-grid (a container
wall) or occupied by a pin of `S`.

*Proof.*  `S ∪ {p}` is a down-set, so every predecessor of `p` lies in `S ∪ {p}`, hence in `S`. ∎

**Checked on the corpus** (`code/t0_backing.py`, `results/t0_backing.json`): the proposition holds
at all **16** usable (class, slot) pairs, with zero OPEN predecessors.  Only **2** of the 16 —
`k5_11 TR(0,0)` and `trump5 TL(0,0)` — are wall-backed on BOTH axes; the other 14 have at least
one PIN backing.

Therefore (T1)+(T2) force

    t_u ≥ 0  and  t_v ≥ 0,       with  t_u ≥ h (resp. t_v ≥ h) whenever the −u (resp. −v)
                                 backing is a SLACK pin rather than a wall,

so `A ⊆ [0, h]²` **always**: the tolerance can only be spent moving the slot square *away from its
two backed sides*.  But nothing can graze the cell through a backed side — that is where the wall
and the pin are.  Grazers arrive through the two OPEN faces `+u`, `+v`, and a translate in `+u`,
`+v` moves the cell *towards* them while shedding only the (empty) strips against the wall and the
pin.  The refinement is therefore **structurally incapable of removing a grazer at a completable
slot**; it can only add meeters.

Two corollaries worth recording:

* **the exact snap `t = 0` is inadmissible in the slack family** at every slot whose backing is a
  PIN rather than a wall — a pin displaced by `+h` towards the slot overlaps `C` itself.  In this
  corpus the wall-backed slots are exactly the corner cells `k5_11 TR(0,0)` and `trump5 TL(0,0)`;
  everything else (`(0,1)`, `(1,0)`, `(1,1)`, `(0,2)`) is backed by at least one slack pin.  A141's
  leaf therefore does not merely *fail to prove* the slack statement — for those slots its snap is
  literally unavailable there.
* the useful direction would be `−u`/`−v`, i.e. pushing the snapped square INTO the wall or the
  pin.  Against a wall that is impossible; against a slack pin it would need the pin itself to be
  moved, i.e. a genuine two-square exchange (A98/A130 territory), not a snap.

Measured, per §`results.md`: at `k5_16_interior_Y1117` no variant at any of the six usable slots
improves on A141, and over the swept population the translated cells produce **no kill that A141's
exact cell does not already produce**.

---

## 5. What else has to change with the leaf (and makes it strictly weaker)

For an A57 node the family is the `δ = 10⁻²` slack one, so the PIN obstacles in `LANE_K′` must be
the `K′` cores of the FATTENED pin boxes, half-side `½ − h` instead of the near-degenerate
`½ − 3.08e-8`.  This is a strict weakening of every discharge (`polylane.find_witness` has less
core to aim at) and it also raises `M` (a fattened pin can itself reach the cell).  A152 runs the
sweep in the node's own regime and records the exact-pin baseline alongside, so the two effects
are separated in `results/t2_sweep_s*.jsonl`.

---

## 6. Lean shape

Four obligations; three are small, one is the whole prerequisite.

1. `SlotSnap.admissible` — a decidable predicate on `t`: `|t|_∞ ≤ h`, `C + t ⊆ container`, and
   `C + t` interior-disjoint from `σ + [−½−h, ½+h]²` for each pin slot `σ`.  Pure rational
   interval arithmetic over a fixed finite slot list; the same shape as `Zones.pin_disjoint`.
2. `SlotSnap.teleport_translated` — Lemma SNAP-t.  This is `Zones.teleport_packing` with the
   target square `C` replaced by `C + t`; the existing proof goes through verbatim once (1) is
   available, because the only facts used are container membership, pin-disjointness and
   "everything else misses the target".
3. `PolyCoreT5.lane_bound` / `M_bound` on a TRANSLATED rectangle — no new content: A135's
   `box_misses_cell` and `path_cover_complete` take the cell rectangle as a parameter, so the
   translated cell is an instance, not a generalisation.  The certificate schema gains
   `translate : ℚ × ℚ` and the checker re-derives `cell_rect = C + t`.
4. `Extension.dead_slack` — *"class `T` has no packing on `[191/50, 969271/250000]` with its six
   pins within `h` of their slots"*.  **This does not exist** (see `notes/prereq.md`); today's
   axiom is `Extension.dead_exact`, with a pin tolerance of `3.08e-8`.

Obligation 4 is the leaf.  Without it, 1–3 prove nothing new, and with it the leaf is (by §4)
worth nothing on this corpus.
