# A158 — the SLOT-SPLIT leaf, its statement, and its Lean shape

## 1. The statement

Fix an alive node `H` of a pinned class (`k5_11`, `k5_16`, `trump5`), a **usable** slot `C` of that
class (a cell whose extension class is certified dead on the node's window — for `trump5 TL(0,0)`
the extension is `k6_23`, converted to the FULL window `[191/50, 969271/250000]` by **A114**
(scoreboard `a114.rows_converted_to_full_window`, ledger rule `soundness.md` P7 + A86 T4), so the
slot is usable), and two parameters `r > 0`, `tt ∈ [0, 45)`. Put

    S(r, tt) := { poses : |centre − slot centre|_∞ ≤ r ,  tilt ∈ [0, tt] ∪ [90 − tt, 90] }

in the cell's corner frame (the frame of `lane.cframe_boxes`, in which `C = [i, i+1] × [j, j+1]`).

**LEAF SLOT-SPLIT.** If

* **(YES)** `LANE_K'(C | S) = 0` and `M(C | S) = 0` — A141's certified lane bound and certified
  conditioned-meeter count, both computed with `K'(S)` added to the obstacle list — and
* **(NO)** the node LP with the extra hypothesis `NoFam(S)` has `tau < budget`,

then the node is dead.

*Proof.* Either some square of the packing has its pose in `S` or none does.

* **YES branch.** Let `Q_S` be a square with pose in `S`. Every other square that meets `int C` is
  either free or one of the node's conditioned squares. A free one is counted by
  `LANE_K'(C | S)`: the pose cover of the centre window discharges every box either because every
  pose of it leaves the container, or because every pose of it misses `int C`, or because it
  shares a rational point with a conditioned box (⇒ it *is* that conditioned square, impossible
  for a free square) or with `S` (⇒ it *is* `Q_S`). A conditioned one is counted by `M(C | S)`,
  the same three discharges applied to its own box. So `int C` is met by at most
  `1 + LANE_K'(C | S) + M(C | S) = 1` square. Lemma SLOT-CROWD demands **≥ 2** non-pin meeters of
  a usable slot, so the packing lands in the slot's extension class, which is certified dead on
  the node's window (teleport / K0-FREE).
* **NO branch.** `NoFam(S)` is exactly "no square's pose is in `S`", the hypothesis the node LP's
  NO-family clause consumes; `tau < budget` is the standard case-LP kill.  ∎

The only new content over A141/A112 is the extra `CondSq` in the YES branch — the discharge
against `K'(S)` is an **identification** ("the same square as `Q_S`"), not a contradiction, which
is why it costs nothing and why the count is `1 + LANE + M` rather than `LANE + M`.

## 2. Every piece already exists

| piece | where | status |
|---|---|---|
| the tautology `SomeIn S ∨ NoneIn S` | `lean/…/LocalCompose.lean` `yes_or_no` (with `Ls = [S]`) | **proved** |
| the composition of the two branches | `LocalCompose.node_dead_of_yes_no` / `classKilledAt_of_yes_no` | **proved** (see §3 for the one change) |
| the clamp of the NO zone to `[1/2, s − 1/2]` | `LocalCompose.centre_in_slab` + `noneIn_of_clamped` | **proved** |
| `ZONE ⊆ BOX` on the WRITTEN rationals | A136 `a136lib.zone_sub_box` (decidable; raises `FCoverError`) | **deployed** |
| the NO leaf itself | `case-measure-certificate-v1` + frozen `verify_case.py` (sha `521cb01f…`) | **deployed** |
| the shared-point discharge | `PolyCoreT5.shared_point_same_square` (T5‴), on `Zones.core_meet_same_square` | **proved** |
| the certified polygon core `K'(B)` | A132 `polycore.build` / `vertex_ok` = Lean `checkVertexInPBox` | **deployed** |
| the lane bound and the `M` cover | A118 §1.2 / A141 `polylane.lane_cover`, `cond_can_meet` | **deployed** |
| SLOT-CROWD (≥ 2 non-pin meeters at a usable slot) | A118 `notes/method.md` §2 (class-`S` composition) | **stated** |
| teleport | `Selection.teleport_packing` | **proved** |

## 3. The Lean shape

With `|L| = 1` the composition collapses to a two-line `Or.elim` (sketch — the `List.get`
reductions on a one-element list are `simp`):

```lean
theorem node_dead_of_slot_split
    {S : Box} {s0 : ℝ} {H : ℝ → Cfg → Prop}
    (hyes : ∀ (s : ℝ) (z : Cfg), s ≤ s0 → CfgPacking s z → H s z → SomeIn S z → False)
    (hno  : ∀ (s : ℝ) (z : Cfg), s ≤ s0 → CfgPacking s z → H s z → NoneIn S z → False) :
    ∀ (s : ℝ) (z : Cfg), s ≤ s0 → CfgPacking s z → ¬ H s z := by
  intro s z hs hz hH
  rcases yes_or_no [S] z with hy | ⟨i, hi⟩
  · exact hyes s z hs hz hH (hy ⟨0, by simp⟩)
  · exact hno  s z hs hz hH (by simpa using hi)
```

i.e. **`yes_or_no` with a one-element list**, nothing else. It differs from
`node_dead_of_yes_no` only in that the YES side is discharged by an arbitrary `False`, not by
`LocalDead Ls Ps s0`; A120's clauses **A2** (pairwise pose-disjointness of the boxes) and **A3**
(pose-disjointness from the pins) are **vacuous at `|L| = 1`**, which is the one structural
simplification the slot split buys over A120's `|L|`-box cover.

The two obligations are then:

* **`hno`** — already discharged by the existing chain:
  `verify_case.py` PASS ⇒ the certificate's claim ⇒ `NoneIn ZONE z → False`, and
  `noneIn_of_clamped` (with `B' := ZONE`, `B := S`) lifts it to `NoneIn S z → False` provided
  `ZONE ⊆ S` on the written rationals — which A136's `narrow` establishes by construction and
  `zone_sub_box` decides.
* **`hyes`** — **the one new named obligation**, `slot_singly_met_of_someIn`:

      SomeIn S z  →  #{ i : Q i meets int C } ≤ 1

  from `LANE_K'(C | S) = 0` and `M(C | S) = 0`, each a finite conjunction of interval facts over a
  replayed box cover, whose only non-arithmetic step is `shared_point_same_square`. Composed with
  SLOT-CROWD and the slot's extension certificate it yields `False`. This is the same shape as
  A141's `polycore_slot_lane_v1` leaf with one extra core in the obstacle list, so the certificate
  format needs **one new field** (`s_box`) and the checker one extra core.

## 4. What A158 measured (why the leaf is, so far, not deployable)

The two branches pull on the same knob in opposite directions:

* `K'(S)` **shrinks** as `S` grows, so the YES branch wants `S` **small**;
* `NoFam(S)` exempts LP rows only when `S` is **large** — and `caselp` drops a row only if its
  centre is inside the zone by `EPS_ZONE = 2e-3` and its tilt inside a `t`-interval by
  `EPS_TH = 0.3°`, so an `S` narrower than `4e-3` in centre or `0.6°` in tilt exempts **nothing**
  and the NO branch is literally the original LP.

The measured thresholds are in `results/xover158*.jsonl` (YES) and `results/no158.jsonl` (NO), and
they do not overlap on any cell run here — see `notes/method.md` §4. The leaf is therefore correct
and cheap, and **its window is empty at the radii the LP can feel**.

**The obstruction is in the TILT variable alone, which makes it independent of `r`.**

* The NO side cannot exempt a single row unless `tt > 0.3°`: `NoFam.inside_many` drops a row only
  when its tilt is inside a `t`-interval by `EPS_TH = 0.3°`, and the two intervals of `S` are
  `[0, tt]` and `[90 − tt, 90]`, whose margined forms `[0, tt − 0.3]` and `[90 − tt + 0.3, 90]`
  are empty for `tt ≤ 0.3°`. (The `0` and `90` ends carry no margin — they are the domain
  boundary — which is why the intervals are one-sidedly margined.)
* The YES side was measured to fail at `tt = 0.5°` **with the centre exactly pinned (`r = 0`)** on
  every cell tried: `K'(S)` over a 0.5°-wide tilt range has already lost the corner sliver through
  which the second meeter enters.

So the only band in which the two could conceivably meet is `tt ∈ (0.3°, 0.5°)`, independently of
`r`; A158 measured the YES side there as well (`results/xover158_gap.jsonl`, `tt = 0.31, 0.4,
0.49`). Any anisotropic box — wide in the centre, narrow in tilt — inherits the same obstruction,
because the tilt bound does not involve `r` at all.
