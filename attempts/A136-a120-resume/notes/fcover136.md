# A136 — the F-COVER wrapper: what it writes, why the rounding goes the way it does, and the Lean predicate it discharges

`code/a136lib.py` (`narrow`, `zone_sub_box`), spliced into A112's emitter by `code/certify136.py`
and used by `code/recert136.py` (T1) and `code/run136.py` (T2).  Nothing under `attempts/A112-*`,
`attempts/A120-*`, `attempts/A126-*`, `attempts/A133-*` or `lean/` is edited; A112's `certify.py`
and `caselp.py` are IMPORTED and A112's rounding helpers (`TDEN`, `XDEN`, `t_of_deg`, `q_up`,
`t_lo`, `t_hi`) are imported rather than re-typed, so the denominators are identical by
construction.  The frozen `verify_case.py` (sha256 `521cb01f…`) is checked byte-identical before
every run.

## 1. The predicate

A120's cover is `node = YES ∪ NO_1 ∪ … ∪ NO_|L|` with `YES = node ∧ (∀ i, some square's pose in
BOX_i)` and `NO_i = node ∧ (no square's pose in BOX_i)`.  In Lean
(`PackingCertMathlib/LocalCompose.lean`) the cover is `yes_or_no` and the consumer is
`node_dead_of_yes_no`, whose NO hypothesis is

```lean
hno : ∀ (i : Fin Ls.length) (s : ℝ) (z : Cfg), s ≤ s0 → CfgPacking s z → H s z → ¬ NoneIn (Ls.get i) z
```

— about the **BOX**.  A `case-measure-certificate-v1` proves the corresponding statement about the
**ZONE** it writes into `hypotheses.nofams`.  The bridge is

```
NoneIn BOX z  →  NoneIn ZONE z          i.e.   ZONE ⊆ BOX  (as pose sets),
```

which is exactly `LocalCompose.noneIn_of_clamped` applied with `B' := BOX`, `B := ZONE`: its
`ht0 : B'.t0 ≤ B.t0` and `ht1 : B.t1 ≤ B'.t1` read `BOX.t0 ≤ ZONE.t0` and `ZONE.t1 ≤ BOX.t1`, and
its two centre clauses (`B'.cx0 ≤ max B.cx0 (1/2)`, `min B.cx1 (s − 1/2) ≤ B'.cx1`) hold as soon
as the zone's centre rectangle is inside the box's — the `max … (1/2)` / `min … (s − 1/2)` slack is
A120's clamp, free by `centre_in_slab`.  So the whole bridge is the finite rational test

```
zone.x0 ≥ box.x0 ∧ zone.x1 ≤ box.x1 ∧ zone.y0 ≥ box.y0 ∧ zone.y1 ≤ box.y1 ∧
  ∀ (a, b) ∈ zone.t_intervals, ∃ (c, d) ∈ box.t_intervals, c ≤ a ∧ b ≤ d
```

decidable on `ℚ` — one `decide` in Lean, `a136lib.zone_sub_box` here.

## 2. What A112 wrote, and why it failed

`caselp.make_certificate`'s `nofams=` clause rounds the zone **outward**: `t_lo` = `floor − 1` and
`t_hi` = `ceil + 1` unit of `2⁻²⁴ = 5.96·10⁻⁸`, `q` = nearest at `10⁻⁹`.  Measured by A126
(`zonecheck126.py`) on all 22 of A120's PASSing certificates: the written zone is `9.0·10⁻⁸ …
1.10·10⁻⁷` outside the box in tilt and `≤ 4.71·10⁻¹⁰` outside on 16 of the 22 upper centre bounds.
Outward is the right direction for the verifier (a wider zone exempts more, so the certificate
proves more) and the wrong one for the cover.  A120's own `A6_nofam_is_the_same_box` compared the
zone with the box **before** the rounding, which is why it passed on all nine nodes while none of
the emitted certificates satisfied the containment.

## 3. What the wrapper writes

`narrow(cert, nofams_exact, boxes, s)` re-derives every bound from the **exact** zone (the node's
own `hyp.nofams`, which A120 builds at full precision — the certificate's already-rounded
rationals are never re-rounded) and writes:

| object | lower bounds | upper bounds | t-intervals |
|---|---|---|---|
| `hypotheses.nofams[i]` (ZONE) | `q_up` = `ceil + 1` at `10⁻⁹` | `q_dn` = `floor − 1` at `10⁻⁹` | `[ceil + 1, floor − 1]` at `2⁻²⁴` |
| `hypotheses.nofam_boxes[i]` (BOX, new key) | `q_up` | `q_dn` | same |

i.e. **both inward**, then `ZONE := ZONE ∩ BOX`, then `zone_sub_box` on the written rationals,
raising `FCoverError` on failure.  A t-interval that would become empty is dropped, never emitted
reversed; it cannot happen here (narrowest measured t-interval `8.75·10⁻²`, six orders of
magnitude above the grid).  `verify_case.py` reads `hyp.get("nofams", [])` and ignores unknown
keys, so `nofam_boxes` and the `fcover` block ride along without touching the verifier.

**The one departure from the A136 brief, and why.**  The brief says "the YES box bounds outward".
The box is written **inward** instead.  The YES leaf is killed by "for every `i`, some square's
pose is in `BOX_i`" ⟹ A116/A119's hypothesis for `N`; shrinking `BOX_i` **strengthens** that
hypothesis (a pose in the smaller box is a pose in A119's box), so the YES kill survives, while
**widening** `BOX_i` would admit poses outside A119's certified box into the YES hypothesis and
would simply move the `10⁻⁷` defect from the NO side — where a decidable check catches it — to the
YES side, where nothing does.  Widening would also threaten A120's A2/A3 pose-disjointness, which
is what makes the four YES witnesses distinct squares.  The price of the inward box is one extra
Lean obligation, recorded in §5.

On unclamped edges the box and the zone are derived from the *same* float by the *same* helper, so
they coincide exactly and the containment holds with equality; on a clamped edge (only `BR(0,1)`'s
`x1 = 3.577084 > s₀ − 1/2`, which the `D4` map sends to `x1` or `y1` depending on the node's
`struct_op`) the zone is strictly inside.

### 3a. A clamped bound must be written EXACTLY, not rounded — measured, not guessed

The first T1 pass rounded the clamped bound inward like every other bound, and **every single
`NO3` certificate FAILed** (7 of 7 — `Y0230`, `Y0303`, `Y0637`, `Y0709`, `Y0973`, `Y0997`,
`Y1099`) while **every `NO0`/`NO1`/`NO2` PASSed** (15 of 15).  `NO3` is `BR(0,1)`, the only box
whose zone clamps.  The verifier's witnesses say exactly why: they are all `hole`s at
`t ∈ [0, 2⁻¹⁸]` with the centre coordinate in `[3.3770812…, 844271/250000]`, i.e. a band ending
**at the wall** `s₀ − 1/2 = 844271/250000`, carrying `exact_mass = 393593/500000 ≈ 0.787 < 1`.
Shaving `10⁻⁹` off the clamp took that band out of the exemption; it is at the very top of the
admissible strip, the emitted measure has no mass to spare there, and at depth 56 the verifier's
smallest cell (`≈ 2.8·10⁻⁶` wide) still straddles the new bound, so no amount of splitting
discharges it.

The fix is to write the clamp bound **exactly**, which costs nothing: `1/2` and
`s₀ − 1/2 = 969271/250000 − 1/2 = 844271/250000` are exact rationals.  It is sound in both
directions — `ZONE ⊆ BOX` still holds (`844271/250000 ≤ BOX.y1`), and
`noneIn_of_clamped`'s clamped clause is `min(ZONE.c1, s − 1/2) ≤ BOX.c1`, which is what an
exactly-written clamp satisfies.  With that change all 7 re-certify: **22 of 22 PASS.**

The lesson generalises past this attempt: *inward rounding is for bounds that came from a float;
a bound that came from an exact geometric fact (a wall, a clamp, a symmetry axis) must be written
as that fact.*  Rounding it inward invents an uncoverable sliver at precisely the place where the
measure is tightest.

## 4. Measured cost of the fix

Per bound, against the **exact** zone: `≤ 8.88·10⁻⁸` (2 units of `2⁻²⁴` in `t`, `1.5·10⁻⁹` in the
centre).  Against **A120's own written** certificate: `1.788·10⁻⁷` = 3 units of `2⁻²⁴` — the
outward bound and the inward bound sit on opposite sides of the exact value, which is why the
change is larger than the `1.2·10⁻⁷` the brief quotes for the distance from the exact zone.  Both
are three to four orders of magnitude below the LP's own conservativeness (`EPS_ZONE = 2·10⁻³`,
`EPS_TH = 0.3°`), so the **LP** is unaffected by the narrowing; what is affected is the
**certificate**, because the boxes in the thin shell between the two zones are no longer EXEMPT and
the emitted measure has to cover them.  That is a real cost and it is paid in
`certify.py`'s witness-feedback loop, not in the LP — see `notes/results136.md`.

## 5. Residual Lean obligations created or removed by this attempt

* **REMOVED** — F-COVER itself: `ZONE ⊆ BOX` now holds on the written rationals of every
  certificate this attempt emits or re-certifies, verified by `zone_sub_box` and recorded per
  certificate in the file's own `fcover` block. `noneIn_of_clamped` applies as stated.
* **NEW (small)** — `LocalDead` antitonicity in the box list: the written `BOX_i` is a subset of
  the mapped A119 box, so `hD : LocalDead Ls Ps s0` has to be transported from A119's boxes to the
  written ones.  This is monotone in the trivial direction (a smaller box is a stronger YES
  hypothesis: `SomeIn B' z → SomeIn B z` when `B' ⊆ B`, which is `Box.mem` monotonicity) and is one
  `intro`/`exact` away, not a new certificate.
* **UNCHANGED** — the three pre-existing gaps A126 lists: `CertCover` for
  `LocalCertS02.localDead_s02`; `checkCaseI_no_family` vs `CfgPacking` (Lemma B of `Dilation.lean`,
  closed squares vs interior-disjointness); and the `native_decide` replay of each certificate via
  `lean/gen_case_lean.py`.
