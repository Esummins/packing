# A118 T3 — the exact leaf statement for the frozen chain, its Lean shape, and what the verifier checks

## 1. The statement a LANE-COUNT leaf certificate carries

A leaf file `lane-count-certificate-v1` fixes:

| field | meaning |
|---|---|
| `class` | the Young class `S` (pin slots as `alpha + beta*s`, `beta in {0,1}^2`) |
| `cell` | corner `c`, offsets `(i, j)`; and the extension class `T = S u {p}` with its window row |
| `s_lo, s_hi` | the node's side interval `[m_lo, s0]` |
| `cond` | the node's conditioned parameter boxes, PULLED BACK to side `m` and mapped into `c`'s corner frame (interval hulls of affine-in-`s` endpoints) |
| `pins` | the class pins in `c`'s corner frame over `[s_lo, s_hi]` (same affine hull) |
| `cover` | the boxes `B_1..B_N` (rational); `N = 0` is the `LANE = 0` case |
| `M` | the number of conditioned squares that can meet `int C` |

and claims

> **LANE-COUNT.** For every `m in [s_lo, s_hi]` and every packing `P` of 11 unit squares in
> `[0,m]^2` containing the pins of `S` and realising the node's conditioned boxes, the cell
> `B_p(m)` is met (open interiors) by at most `LANE + M <= 1` non-pin squares of `P`.

Composed with **SLOT-CROWD** (`slot_crowds.md` §2; for k0, **K0-FREE**, `k0_route.md` §3) this is
`False`, so the node is empty — a KILL with no LP, no measure and no certificate replay.

## 2. Lean shape, against the T5 pattern

T5 (`core_meet_same_square`) is: *`K_B` is contained in every unit square whose pose lies in `B`;
`K_B` meets a pin core `K_P`; two distinct squares of a packing have disjoint interiors;
contradiction.* One containment lemma + one interval inequality + `Packing.disjoint`.

LANE-COUNT is the same skeleton with `teleport_packing` supplying the "two meeters" hypothesis:

```lean
-- the crowd input, already available: slot_crowds.md §2 = teleport_packing + class_kill
theorem slot_crowd  (S : YoungClass) (p : Slot) (hp : S.UnclippedCompletable p)
    (hT : ClassKilledOn (S.extend p) W) (m : ℝ) (hm : m ∈ W)
    (z : Packing m) (hz : ContainsPins S.pins m z) :
    2 ≤ (z.nonPin.filter (fun Q => (interior Q ∩ interior (cell S p m)).Nonempty)).card

-- the new leaf
theorem lane_count_kill
    (S : YoungClass) (p : Slot) (hp : S.UnclippedCompletable p)
    (hT : ClassKilledOn (S.extend p) W)
    (N : Node) (cov : List Box) (M : ℕ)
    (hcov  : ∀ m ∈ N.sides, ∀ (z : Packing m), ContainsPins S.pins m z → N.Realises z →
             ∀ Q ∈ z.free, (interior Q ∩ interior (cell S p m)).Nonempty → ∃ B ∈ cov, Q.pose ∈ B)
    (hpair : ∀ B ∈ cov, ∀ B' ∈ cov, AlwaysOverlap B B')
    (hM    : ∀ m ∈ N.sides, ∀ z, N.Realises z →
             (z.conditioned.filter (fun Q => (interior Q ∩ interior (cell S p m)).Nonempty)).card ≤ M)
    (hbudget : 1 ≤ M → cov = [])                -- i.e. LANE + M ≤ 1
    : ∀ m ∈ N.sides, ¬ ∃ z : Packing m, ContainsPins S.pins m z ∧ N.Realises z
```

Proof sketch (five lines, all existing API):
`slot_crowd` gives two DISTINCT non-pin meeters `Q1 ≠ Q2`; `hM` puts at most `M` of them among
the conditioned squares, so at least `2 - M ≥ 1` are free; `hcov` puts each free meeter's pose in
a cover box; if there are two free meeters, `hpair` on their two boxes contradicts
`Packing.interiorDisjoint Q1 Q2`; if there is one free meeter and `M = 1`, `2 ≤ 1 + 1` is only an
equality and the two meeters are `Q1` free, `Q2` conditioned — this case is excluded exactly when
`LANE + M ≤ 1`, i.e. `cov = []` (`hbudget`), which makes `hcov` say NO free square meets the
cell, so both meeters are conditioned and `2 ≤ M ≤ 1`.

Three obligations, all interval arithmetic, none of them a new checker kind:

* **O-COVER** (`hcov`) — the complement of `cov` in the grid is discharged box by box by four
  interval inequalities: (1) `x1 < h_min(θ)` etc. (the square leaves the container for every
  pose), (2) a separating axis against the cell certified over the box, (3) T5/T5'' against a
  hypothesis core, (4) Lemma CONT (`mu <= 0` in the two shifted frames). Exactly `verify_case.py`'s
  box recursion shape, with a discharge predicate instead of a measure bound.
* **O-PAIR** (`hpair`) — `AlwaysOverlap B B'` is ONE rational inequality per ordered pair:
  `max_{d in D(B,B')} |d| < 1/2 + 1/2 * min_{Δ} (|cos Δ| + |sin Δ|)`, together with the two
  elementary facts `|n·d| ≤ |d|` and `|cos| + |sin| ≥ 1`. Strictly stronger than Lemma TC
  (core-vs-core), and it subsumes A112's "Lemma TC as a certified leaf" obligation.
* **O-HULL** — the affine-in-`s` hull of the pins, the cell and the pulled-back conditioned boxes
  over `[s_lo, s_hi]`. The same affine `alpha + beta*s` form `verify_param.py` already carries for
  atoms and cores; here it is only evaluated at the two endpoints.

`SLOT-CROWD` itself needs nothing new: it is `teleport_packing` (Selection.lean) plus the
extension class's parametric window row (`ParamBridge`), one instance per usable slot — the same
composite `slot_crowds.md` §8 already specifies. **k0 additionally needs k1_00's tree** (K0-O1,
open): every k0 verdict here is conditional.

## 3. What the verifier must check

A `lane-count-certificate-v1` replay is:

1. re-derive the pin / cell / conditioned hulls from `class`, `cell`, `s_lo`, `s_hi` (exact
   rationals; check they match the file);
2. walk the grid: every cell either appears in `cover` or satisfies one of the four discharge
   inequalities (recursive bisection, exactly `verify_case.py`'s driver);
3. check the `N(N+1)/2` pair inequalities;
4. check `M` against the conditioned boxes (the same cell-separation inequality);
5. check `LANE + M <= 1`, i.e. `N <= 1 - M`;
6. check the slot's usability row (the extension class is FULL on a window containing
   `[s_lo, s_hi]`) against the scoreboard.

No measure, no LP, no column generation; ~150 lines on top of the existing box recursion, and a
replay is milliseconds (the covers that fire have `N = 0`).
