# MIN-TILT(11) — the smallest tilt of the all-ADJ ring that still admits the ninth square, the room in its pocket, and the flush-limit certificate — A253, 2026-09-17

The PI (2026-09-18 01:00): *"what's the smallest tilt angle the ring squares can possibly have that
still allows the ninth square to meet the overlap band? ... once you have the minimum tilt angle
possible in order to maximize the pocket size, you'll be able to run LP on the pocket geometry and
find that it can't fit more than 1 (maybe two) squares."*

Tags: [T] proved, [T-computed] certified / exactly verified, [M] measured, [F] false as stated,
[C] obligation.  Sources: `centre_disc.md` (A252: RING + POKER, the poker's corner in the slot
overlap [0,1]×[s−2,2], the residual obligation), `type_t_chase.md` (A249: the all-ADJ type-T ring at
ŝ, tilt 14.545°), `ring_pocket.md` (A251: the 17-coordinate family, the sound cores, INRADIUS),
`family250.md` (A250: the ILP count), `pocket_waste.md` (A237: PIERCE), `corner_chase.md` (A248:
TWO-POKERS), A226's corner-domino crowds.  Code `attempts/A253-min-tilt/code/` (`geom253`,
`mintilt253`, `room253`, `limit253`, `cert253`, `pages253`, `summarise253`, `test253`, `run253.sh`);
results `results/mintilt253.md` (+ `mintilt253_curve.jsonl`, `room253.jsonl`, `limit253.json`,
`cert253_*`); pages `docs/residue_map/campaigns/A253-min-tilt/{min_tilt_ring,ribbon_close,capacity_tilt}.svg`.

## 0. Verdict

> **[F] There is no positive minimum tilt: θ_min(s) = 0 on the whole window [3.82, 4).**  Write
> τ := min(θ, 90° − θ) for the tilt of a ring member (its deviation from flush; the term block
> 36..43 of `ring_margin`).  On the common-tilt slice of the pinwheel sign pattern σ = 00110011
> (A249's ring is exactly this pattern at τ = 14.54489°, spread 3·10⁻⁷°), the joint ring + poker
> margin M(τ, s) = sup over the eight δ and the poker pose of min(ring feasibility, A252's
> `poke_margin`) is **strictly positive for every τ > 0 tested down to 0.1°** — at ŝ,
> M = 7.75·10⁻³ (14.545°), 7.8·10⁻⁴ (4°), 4.8·10⁻⁵ (1°), 9.8·10⁻⁷ (0.25°), **5.7·10⁻⁸ (0.1°)** —
> and the quantity that degenerates is precisely the PI's one: at ŝ the binding term at every
> τ ≤ 4° is the **POKER's** (`poker_ribbon`, its depth in the slot-overlap ribbon, or its gap to the
> adjacent floor meeter), while the ring's own margin stays up to three orders of magnitude larger
> (1.2·10⁻³ against 9.8·10⁻⁷ at τ = 0.25°).  So the ribbon does close as the tilt falls, exactly as the
> PI said — but it closes only **in the limit**, at τ = 0.  (Effort: 24 Nelder–Mead sup-margin runs
> per side over an 8-δ + 3-poker joint objective, warm-started down the tilt ladder, ~40 s each; the
> upper end of the tilt window is between 26° and 30° at ŝ — the family is an OPEN interval
> (0, τ_max(s)) in the tilt, not a half-line.)
>
> **[T] The τ → 0 limit is the FOUR-CORNER DOMINO PINWHEEL, and its room is EXACTLY ONE.**  Every
> parameter converges: the limit ring is the eight axis-aligned squares
> [0,1]×[1,2], [0,1]×[2,3] on x = 0 and its three D4 images — four 1×2 corner dominoes (A226's crowd
> structure, A250's exchange dominoes).  Its pocket splits **exactly** into the central square hole
> [1, s−1]² of side s − 2 and four **isolated** 1 × (s−3) notches (verified in rational arithmetic
> and against shapely at six sides), and the slot-overlap ribbon [0,1]×[s−2,2] lies **inside** the
> wall block [0,1]×[1,3] — in the limit the ring's own two wall touchers close the ribbon and the
> poker dies.  Two n-general lemmas finish the room with no search at all:
>
> * **[T] Lemma HOLE-ONE.**  In a square container of side σ ≤ 2 every unit square contains the
>   container's centre, so **at most one** fits.  *Proof.* A unit square of tilt θ inside [0, σ]²
>   has centre q ∈ [w/2, σ − w/2]², w := cos θ + sin θ ≥ 1.  For the centre p = (σ/2, σ/2) and either
>   edge direction u of the square, |(p − q)·u| ≤ ((σ − w)/2)·w, and (σ − w)w − (σ − 1)
>   = (w − 1)(σ − w − 1) ≤ 0 because w ≥ 1 and σ ≤ 2 ≤ w + 1; hence |(p − q)·u| ≤ (σ − 1)/2 ≤ ½. ∎
>   Applied to σ = s − 2 the slack is **(4 − s)/2 > 0 exactly on s < 4** — the window's upper end is
>   where this lemma dies, which is why s = 4 is the boundary.
> * **[T] Lemma NOTCH-NARROW.**  A unit square has width ≥ 1 in every direction, so it does not fit
>   in a rectangle with a side < 1; the limit notches have side s − 3 < 1 for s < 4. ∎
>
>   So **capacity(flush-limit pocket) = 1** for every s ∈ (3, 4): 8 + 1 = **9 < 11**, by theorem, at
>   the extremal tilt the PI identified.
>
> **[M] The room does not grow as the tilt falls — it is CONSTANT 1.**  A237's box-valid PIERCE(1)
> certifies capacity ≤ 1 and A222's region search fits exactly one square, at **every** sampled tilt
> of the family at ŝ (τ = 26, 22, 18, 14.545, 6°, …; pocket area s² − 8 = 7.0318 throughout), and
> beside the pinned poker **no** further square fits — A252's residual is empty at every one.  So
> Conjecture MONOTONE-ROOM is not needed in the form the brief expected: the measured room is not
> merely monotone in τ, it never exceeds its limit value 1.
>
> **[C] What remains.**  The above is the COMMON-TILT slice of the family (a 2-parameter surface
> (τ, s) inside the 17-coordinate box) plus its boundary; extending it to the whole family needs
> Lemma MONOTONE-ROOM or a box-valid certificate off the slice.  RING-POKER-RESIDUAL(11) is
> **not** closed by A253; FAMILY-STUCK-EXIST(11) is not closed; k0_00 unchanged.

## 1. The tilt of a ring member, and the common-tilt slice (task 1 set-up)

A251's family is 17 coordinates: per corner c ∈ {BL, BR, TR, TL} a wall meeter's (θ_B, δ_B) and a
floor meeter's (θ_A, δ_A), plus s.  θ ∈ (0, 90°) is measured from the wall/floor in the corner
frame, so the square's deviation from flush is τ := min(θ, 90° − θ) ∈ [0, 45°] — the eight
`tilt_margin` terms of `twotilted249.ring_margin` (`geom253.tilts_of`).  Since those eight terms are
all equal to τ once the tilt is fixed, `geom253.feas` is the ring margin **with the tilt block
removed**: the geometric question, isolated (test `feas == ring_margin minus tilts`, 0 failures).

The COMMON-TILT slice fixes τ and a sign pattern σ ∈ {0,1}⁸ (member order B_BL, A_BL, B_BR, A_BR,
B_TR, A_TR, B_TL, A_TL), with θ_i = τ or 90° − τ.  A249's ring at ŝ is exactly σ = **00110011** — a
pinwheel: the two meeters of BL and TR lean one way, those of BR and TL the other.  That handedness
is what makes small tilts possible (§2).  `mintilt253 --mode screen` enumerates all 256 σ; the
reported ladders use the pinwheel, which is the one A249 found and which dominates at ŝ.

## 2. [F] θ_min(s) = 0 — and why (task 1)

**The measurement.**  `results/mintilt253.md` §1 carries M(τ, s) with, per row, the binding term of
the ring and of the poker.  The pattern is uniform across s = 3.82, ŝ, 3.99:

    tau (deg)   14.545     8       4       2       1      0.5     0.25     0.1
    M at s-hat  7.75e-3  2.84e-3 7.80e-4 2.15e-4 4.76e-5 1.42e-5 9.83e-7  5.70e-8
    ring feas   7.76e-3  2.84e-3 8.39e-4 2.15e-4 7.64e-5 1.45e-5 1.16e-3  2.22e-5
    who binds   poker    poker   poker   both    poker   poker   poker    poker

M falls smoothly and stays positive; the ring's own margin `feas` is far larger than M at the small
tilts (1.2·10⁻³ against 9.8·10⁻⁷ at τ = 0.25°), so **the ring is comfortable and the POKER is what
is starving**.  (At s = 3.82 the ring's own terms bind down to τ ≈ 1°, the poker's below that; the
search loses resolution at τ = 0.1° there — M = −3·10⁻⁶ is a failure to find, not an exclusion.)

**Why the ribbon closes only in the limit.**  Both wall touchers of the wall x = 0 (B_BL with offset
δ, B_TL with offset δ′) touch the wall at a single VERTEX when 0 < θ < 90°, at heights δ + cos τ and
s − δ′ − cos τ; their bodies lean away from the wall in opposite senses (the pinwheel).  So they
leave an open WEDGE against the wall of height s − δ − δ′ − 2cos τ = O(τ) — and the poker's corner
enters the ribbon [0,1]×[s−2, 2] through that wedge.  At τ = 0 the touchers become flush,
δ, δ′ → 1 and s − 3, the two squares close up into the 1×2 block [0,1]×[1,3], and the block CONTAINS
the ribbon (`limit253.verify`: exact, all four walls, six sides).  That is the PI's mechanism
precisely, and it identifies the blocker: **the pair of wall touchers of the wall itself**, not a
corner square (page `ribbon_close.svg`, the wedge measured per panel).

**(ii) the non-uniform minimum.**  θ_min^(ii)(s) ≤ θ_min^(i)(s) = 0 by construction, so the
minimax form adds nothing at the bottom end; `mintilt253 --mode minimax` (A252's protected form,
19 coordinates, J = max_i τ_i + pen·max(0, need − M)) runs in the detached ladder to record the
frontier at a fixed positive margin need — the interesting non-uniform question — rather than a
threshold.

**[T-computed] exactness.**  `cert253 --mode exact` re-verifies every reported ring and poker in
rational arithmetic (tan(θ/2) rationalised to 10⁻⁶, as `test249.test_ring_exact` does): containment,
28 pairwise SAT gaps ≥ 0, twelve border cells doubly met, and for the poker containment, eight gaps
≥ 0 and a STRICT overlap with the ribbon.  On A249's ring the exact and floating gaps agree to
2·10⁻⁵ (test `exact vs float ring gap`).

## 3. [T] The flush limit and its room (tasks 2–3)

`limit253.py` states and checks the limit ring; §0 has the two lemmas.  The decomposition is exact:

    pocket(limit ring at s) = [1, s-1]^2  (side s-2)  ⊔  four isolated 1 × (s-3) notches,
    area (s-2)^2 + 4(s-3) = s^2 - 8                    (all eight squares are unit squares)

and the shapely pocket has exactly five components with these areas at every s tested (3.5, 3.82, ŝ,
3.90, 3.95, 3.99, 3.999).  HOLE-ONE's quantity max_θ ((σ−w)w)/2 equals (s−3)/2 (the max is at w = 1),
so the certificate margin is (4 − s)/2: **0.090 at ŝ, 0.005 at 3.99, 0 at 4** — the lemma is SHARP
at s = 4, which is exactly where the twelve-cell window ends.

The brief's step (c) — "the pocket holds ≤ 1 (maybe 2)" — is therefore **proved at the extremal
tilt**, with = 1, and needs no LP.

**Room against the tilt (task 2).**  `room253.py` reads the capacity three ways at each sampled
ring: FIT(k) (A222's `region222.cspace`/`greedy` region search + a sup-margin polish + the lab's SAT
check) as a lower bound, PIERCE(k) (A237's `geom237.pierce`, box-valid over 1° tilt bins) as a
certificate, and A252's poker-anchored residual.  Every feasible sample at ŝ so far returns
**capacity ∈ [1, 1]** with nothing fitting beside the poker.  The tilt ladder therefore reads:

    tau        26     22     18   14.545    6    ...   -> 0 (limit)
    capacity    1      1      1      1      1            1   [T]

**Conjecture MONOTONE-ROOM [C].**  *For the all-ADJ ring family the capacity of the pocket is
non-increasing in the tilt, so the flush limit is extremal.*  A proof would need a monotone
enclosure: that the pocket at tilt τ is contained in a τ-independent enlargement of the limit
pocket, i.e. a Hausdorff bound ‖pocket(τ) △ pocket(0)‖ = O(τ) uniform over δ, plus stability of
HOLE-ONE under an O(τ) fattening of the hole — the fattened hole has side s − 2 + O(τ), and
HOLE-ONE's slack (4 − s)/2 buys exactly O(4 − s) of that, so the argument closes on any subinterval
[3.82, 4 − ε] with the constant beaten.  **Not proved here**; the samples do not contradict it (they
show the stronger "capacity ≡ 1").

**The one-parameter certificate (task 3).**  With θ_min ≡ 0 the natural one-parameter curve is not
θ = θ_min(s) but **s ↦ the flush-limit ring**, and along it capacity ≤ 1 is a closed-form theorem
for the whole window with slack (4 − s)/2 — no interval arithmetic needed.  For τ > 0
`cert253 --mode oneparam` does the box version at a fixed tilt: over each s-interval the members
move by ρ_i = δ-variation + κ_i·ds (θ fixed, so A251's LIP_C_THETA term vanishes), A251's sound
cores `geom251.core_members` lie inside every ring of the interval, and A237's box-valid PIERCE(1)
is run on those cores.  This is cheap exactly because it is ONE parameter, which was the brief's
point; it runs in the detached ladder.

## 4. Conjecture ONLY-RING [C], and what A249/A250 actually say

**Conjecture ONLY-RING [C]** (the PI).  *Below s = 4 the common-tilt all-ADJ ring (+ poker) is the
only structure that doubly meets all four corner boxes without a trivial slot decomposition.*

What the lab has, and what it does not:

* **[T-computed] A250's ILP**: below 4 the exact minimum number of squares over all incidence
  structures satisfying PROJECTION, NOT-SELF-SUFFICIENT and TWO-FAR is **9**, and it stays 9 under
  SLOT-MET, A247's 62 certified pair kills and the restriction to corner-cell families.  The
  minimising structures are rigid — and A249 §3 identifies the extreme one as **the all-ADJ ring
  plus one poking square**, which exists (poker margin +0.0017 at ŝ).  That is *consistent* with
  ONLY-RING and is the reason the conjecture is plausible, but the ILP counts incidence structures,
  not geometric realisations, and the n = 11 list is A247's walk problem again (13·10⁹ labelled
  walks after the pair kills): **the count does not prove uniqueness**.
* **[T] A248's TWO-POKERS** removes the type-F ring on the whole window (two type-F pokers on one
  wall need s ≥ 3.9342370 > ŝ), so a doubly-met-corner structure below ŝ has type-T corners — one
  half of ONLY-RING.
* **[C] mixed and non-ring structures** (some corners type T, some type F; corners met by free
  squares) are open in A248 §5, A249 §3.4 and A250 §5, and A253 does not touch them.

So ONLY-RING is recorded as an obligation, **not claimed**.

## 5. What is certified, and the resume block

Certified here: the flush-limit ring and its pocket decomposition (rational, six sides); Lemmas
HOLE-ONE and NOTCH-NARROW (proofs above, plus 40 000-sample and 2 000-point numerical checks in
`test253.py`, 9/9 tests pass); the exactness of every reported ring + poker (`cert253 --mode exact`);
PIERCE(1) at each sampled tilt.  Measured, not proved: M(τ, s) > 0 down to τ = 0.1° (a search
result — a failure to find a ring at a smaller τ would not be a proof either way, and at τ = 0.1°
the margins are at the optimiser's resolution); the constancy of the room in τ; θ_max(s) ∈ (26°, 30°)
at ŝ.

**Detached at exit** (`bash attempts/A253-min-tilt/code/run253.sh ladder` and `... roomlane`, two
pythons, BelowNormal, affinity 0xFFFF): `limit` → `curve` (the remaining sides 3.85, 3.92, 3.95) →
`summary` + `pages` → `bisect` (formal brackets per side, ring-only and joint) → `exact` →
`oneparam` (box certificate at fixed tilts) → `minimax` → `summary` + `pages`; the room lane sweeps
the tilt ladder at 3.82, ŝ, 3.99.  Every stage is **resumable**: rows are keyed in
`results/*.jsonl` and a rerun skips what is done; `touch attempts/A253-min-tilt/logs/STOP` stops
both lanes cleanly between rows, and deleting it and rerunning the same command resumes.  Per-shard
commits use explicit pathspecs (`run253.sh`'s `shard`).
