# A158 — drafts of the three named appends

Numbers marked `[[…]]` are filled from `results/summary158.json` immediately before the append.

## 1. `attempts/A60-trump5-campaign/notes/ledger.md`

**A158 (2026-09-08) — the slot split: the NO child is a real, certified narrowing on `c0_Y0076`;
the YES child does not exist at any radius the LP can feel (exact-pin form, class-S composition,
A118-O1 stands).** The leaf is the tautology `SomeIn S ∨ NoneIn S` on the near-simple slot box
`S(r, tt)` = {centre within `r` of the exact slot centre, tilt within `tt` of 0/90}, with the YES
child killed by A141's lane leaf carrying `K'(S)` as an extra obstacle (the discharge against
`K'(S)` identifies the pose with the `S`-square, so the meeter count is `1 + LANE + M`) and the NO
child by one `caselp` `NoFam(S)`.

**`c0_Y0076` `TL(0,0)` (extension `k6_23`, FULL window by A114): the NO child is DEAD.**
`NoFam(S(0.10, 10°))` — zone `[0.4, 0.6] × [3.277084, 3.477084] × ([0,10] ∪ [80,90])°`, clamped by
`centre_in_slab` to `[1/2, 0.6] × [3.277084, 3.377084]` — takes the node LP from `tau = 5.000000`
to `tau = 4.000000`, `eta = budget − tau = 1.000000`; certificate
`attempts/A158-slot-split/certs/no_c0_Y0076__TL0_0__r0.1_tt10.json` (4 atoms, total `103/25` =
4.12 < 5), written through A136's `a136lib.narrow` (`ZONE ⊆ BOX` decided on the written rationals,
max inward shift 7.4·10⁻⁸) and [[VERIFY]]. **So under `c0_Y0076`'s hypothesis some square MUST sit
within 0.10 of the exact `TL(0,0)` slot centre with tilt within 10° of axis-aligned.** That is a
genuine new structural constraint on the node, and it is the half of the PI's reading that holds.

**The YES child is refuted, at every radius.** With `K'(S)` among the obstacles, a free pose that
meets `int C` and clears every pin core, `K'(H)` and `K'(S)` is realised at 400,000 draws for every
`(r, tt)` tried: at `tt = 10°` already at `r = 0` (the pose `(1.6914, 0.6973, 33.04°)` in the
corner frame), and at `tt = 0` for every `r > 3.66·10⁻⁴`. The measured upper bound on the closable
radius is `r_yes = 3.66·10⁻⁴` and only with the tilt PINNED (`tt = 0`); `M(C | S)` is the looser
of the two (`H` is blocked out to `r ≈ 3.6·10⁻²` at `tt = 0`, but can meet at `r = 0` once
`tt ≥ 10°`). `c0_Y0787 BR(0,1)`: `r_yes = 4.88·10⁻⁵` at `tt = 0`, refuted at `tt ≥ 0.5°`.
`c0_Y0959 TR(0,1)`: `r_yes = 2.92·10⁻⁶` at `tt = 0`, refuted at `tt ≥ 0.5°`.

**The two windows cannot meet, and the reason is arithmetic, not geometry.** `caselp` exempts an
LP row only if its centre is inside the zone by `EPS_ZONE = 2·10⁻³` and its tilt inside a
`t`-interval by `EPS_TH = 0.3°`, so any `S` narrower than `4·10⁻³` in centre or `0.6°` in tilt
exempts nothing and the NO child is bit-for-bit the original LP. Measured on `c0_Y0076`, the NO
child needs `r ∈ (0.02, 0.03]` at `tt = 10°` and `tt ∈ (1.5°, 2°]` at `r = 0.10` — two orders of
magnitude above the largest `r` at which the YES child can close, and a tilt window the YES child
fails at outright.

**The other two PI cells are `NEITHER`.** `c0_Y0787 BR(0,1)` and `c0_Y0959 TR(0,1)` keep
`tau = 5.000000` under `NoFam(S(0.10, 10°))` (4.9 s and 72.7 s), and at `r = 0.05` and `r = 0.02`
as well: the LP simply moves the slot square just outside the box. So the coordinator's reading
that forcing `BR(0,1)` to be doubly met strands the space right of `H` is not what the LP says —
`c0_Y0787` survives the NO child at every radius tried [[BIG]].

Nothing in A60 was written; the two new certificates live under
`attempts/A158-slot-split/certs/`.

## 2. `attempts/A57-shadow-trees/PAUSED.md`

**The near-simple slot box is a usable NO-family and not a usable YES leaf (A158, 2026-09-08;
exact-pin form for the leaf, A118-O1 stands; the A57 nodes carry `delta = 10⁻²` slack pins, so
their YES branch would additionally owe the A152 caveat).** A158 ran the PI's tautologous split
`SomeIn S ∨ NoneIn S` on the near-simple slot box `S(r, tt)` (centre within `r` of the exact slot
centre, tilt within `tt` of 0/90) — YES by A141's lane leaf with `K'(S)` as an extra obstacle
(`LANE_K'(C | S) = 0 ∧ M(C | S) = 0` ⇒ the slot is met by the `S`-square alone ⇒ teleport into the
slot's certified-dead `k6` class), NO by one `caselp` `NoFam(S)` and an exact-core re-solve
through A135's emitter, A136's inward-rounding wrapper and the frozen `verify_case.py`
(sha `521cb01f…`).

**The population.** Of the 1,693 alive A57/A60 nodes, **1,238 (73 %)** have LP dual support with
weight ≥ 0.5 inside some usable slot's `S(0.10, 10°)` box — i.e. their `tau ≥ budget` rests on a
square sitting in a near-simple slot position (A57 1,079: k5_11 575, k5_16 504; A60 159). The
commonest are `k5_11 TR(0,0)` 420, `k5_11 BR(0,1)` 219, `k5_11 TL(1,0)` 205, `k5_16 BR(0,1)` 184.
**The split was run on the top 20** [[TOP20]].

**The YES child does not exist.** On all 20 cells a free second meeter of the slot cell — in the
container, meeting `int C`, clear of every pin core, of `K'(H)` and of `K'(S)` — is REALISED at
400,000 draws at `tt = 10°` **already at `r = 0`**, and at `tt = 0` for every `r` above
`4.9·10⁻⁵ – 1.2·10⁻³` (per cell; `k5_11_interior_Y0130 TR(0,0)` and `Y0147 TR(0,0)` and
`k5_16_interior_Y0881 BR(0,1)` fail even at `r = 0, tt = 0`). A realised free pose is a sound
`LANE_K'(C | S) ≥ 1`, so this is a refutation of the leaf, not a budget failure — no cover was
bought.

**The NO child is real but needs a box two orders of magnitude bigger.** [[NO20]] `caselp` exempts
a row only if the centre is inside the zone by `EPS_ZONE = 2·10⁻³` and the tilt by
`EPS_TH = 0.3°`, so an `S` narrow enough for the YES child exempts nothing at all and the NO child
is bit-for-bit the original LP. That gap is arithmetic and cannot be closed by more compute.

**What to carry forward.** The slot split as a KILL is dead; the slot split as a NO-family is a
new, cheap structural constraint — one 20–70 s LP per node says whether the node forces a square
into the near-simple slot box. `k5_11_interior_Y0130 TR(0,0)` is the sharpest measured case: the
NoFam takes `tau` from 5.500000 to exactly 5.000000, i.e. it consumes the node's whole slack and
stops at the budget.

## 3. `docs/residue_ledger.md` §1

**The near-simple slot box splits the node but only one half closes (A158, 2026-09-08; exact-pin
form, A118-O1 stands):** 1,238 of the 1,693 alive A57/A60 nodes (73 %) keep `tau ≥ budget` on a
dual square sitting in some usable slot's near-simple box `S(0.10, 10°)`, and forbidding that box
as a `caselp` `NoFam` is cheap (a 20–70 s exact-core re-solve) and sometimes decisive — on
`c0_Y0076 TL(0,0)` it takes `tau` from 5.000000 to 4.000000 (`η = 1`, certificate
`no_c0_Y0076__TL0_0__r0.1_tt10.json`, frozen `verify_case` [[V]]), so that node PROVABLY puts a
square within 0.10 of the exact slot centre at tilt within 10° of axis-aligned — but the YES half
never closes: on all [[N]] cells run a free second meeter of the slot cell clearing every pin core,
`K'(H)` and `K'(S)` is REALISED at 400,000 draws already at `r = 0` for any tilt window
`tt ≥ 0.5°`, and at `tt = 0` for every `r` above `3·10⁻⁶ – 1.2·10⁻³`, while `caselp` only exempts
a row whose centre is `EPS_ZONE = 2·10⁻³` and whose tilt is `EPS_TH = 0.3°` inside the zone — so
the two halves' parameter windows are disjoint by two orders of magnitude and the split cannot be
completed as a kill (`attempts/A158-slot-split/notes/method.md`).
