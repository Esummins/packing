# A158 — what the slot split actually is, and what it measures

## 0. Discipline

READ-ONLY on every campaign and on A112 / A118 / A132 / A135 / A136 / A141 / A157: `polylane.py`,
`polycore.py`, `lane.py`, `corpus.py`, `caselp.py`, `emit135.py`, `exactcore.py`, `a136lib.py` and
both frozen verifiers are **imported**, never edited or copied. Every A158 file is new, under
`attempts/A158-slot-split/**`, plus the three named appends (`attempts/A57-shadow-trees/PAUSED.md`,
`attempts/A60-trump5-campaign/notes/ledger.md`, `docs/residue_ledger.md` §1).
`PYTHONDONTWRITEBYTECODE=1`; Normal priority, affinity `0xFFFF`; no recursive deletes; no shard
launched; no foreign sentinel touched (A57's `PAUSE`, A137's `PAUSE` and A124's `PAUSE` are all
set and all scoped elsewhere — reported, never cleared).

**Process count, counted first and re-counted before every launch.** The box carried **15** lab
python processes throughout (A149 4 workers + 4 `node137` children, A156 2 + 2, A136 2 `run151`
+ 1 `certify136`), oscillating to 16 whenever one of those workers spawned a verifier child. The
brief's ceiling is 16, so A158 ran **exactly one** process at a time and `run158.ps1`'s gate waits
for a free slot instead of launching. The first pass of `run158.ps1` recorded seven `SKIPPED: box
already at 16` lines — that gate firing, correctly.

**One accounting wrinkle, recorded honestly.** The gate counts python processes whose command line
matches `*code\packing\attempts*`; A158's own children are launched with the working directory set
to `code/` and a RELATIVE script path (`no158.py`), so **the gate does not count A158's own
process**. It therefore launches when it sees 15, taking the true total to 16 — at the ceiling,
never above it — and it refuses at 16, taking the true total to 17 only if it had launched, which
it never did. The counts printed in `logs/run158*.out` are consequently "others", and the true
figure is that number plus one. No launch ever put more than 16 lab python processes on the box.

## 1. The leaf

See `notes/leaf.md` for the statement, the proof and the Lean shape. In one line: for a usable
slot `C` and the near-simple slot box `S(r, tt)`, the tautology `SomeIn S ∨ NoneIn S` splits the
node into

* **YES** — killed iff `LANE_K'(C | S) = 0` **and** `M(C | S) = 0`, A141's two certified counts
  with `K'(S)` added to the obstacle list (the discharge against `K'(S)` is an *identification*
  with the `S`-square, so the meeter count is `1 + LANE + M`);
* **NO** — killed iff the node LP with one extra `NoFam(S)` has `tau < budget`.

## 2. The two frames, and the only sound direction in each

The lane leaf lives in the cell's **corner frame** on the ORIGINAL packing at side `m`
(`lane.cframe_boxes`); the LP lives in the **world frame at `s0`** on the DILATED family. With
`frame X = v·m/s0` (or `m − v·m/s0` at a flipped corner):

* the **NO** zone must satisfy *dilated pose in `Z` ⇒ original pose in `S`*, so `Z` is the
  **intersection** over `m ∈ [m_lo, s0]` of the pullbacks — INWARD. For A60 (`m_lo = s0`) the map
  is exact; for A57 (`m_lo = 3.8616374951330865`) it costs up to 1.6·10⁻³ per coordinate (visible
  in `results/pop158.jsonl`: an A57 `TR(0,0)` zone is `[3.277084, 3.475484]`, not
  `[3.277084, 3.477084]`).
* the **YES** obstacle is `K'(S)`, and `S' ⊆ S ⇒ K'(S) ⊆ K'(S')`, so running the cover with the
  **float (larger) box** proves the kill for every written (inward-rounded) sub-box — also the
  sound direction.
* the tilt set `[0, tt] ∪ [90 − tt, 90]` is invariant under the corner reflection `θ ↦ 90 − θ`, so
  it is the same set in both frames; as a set of SQUARES it is the tilt window `[−tt, tt] mod 90`.
  The YES child runs the two tilt pieces as separate sub-cases (a pose box must be a box).
* the NO zone is clamped to `[1/2, s − 1/2]` (`a136lib.zone_of_box`; sound by
  `LocalCompose.centre_in_slab`), which for a corner slot is a real bite: `c0_Y0076 TL(0,0)`'s
  nominal `[0.4, 0.6] × [3.277084, 3.477084]` clamps to `[0.5, 0.6] × [3.277084, 3.377084]`, a
  quarter of the box — and it still kills.

## 2-bis. The result, in one table

| | count |
|---|---|
| alive A57/A60 records scanned | **1,693** (1,590 distinct nodes: A57 k5_11 713, k5_16 552; A60 trump5 325) |
| with dual weight ≥ 0.5 in some usable slot's `S(0.10, 10°)` | **1,238 (73 %)** |
| cells with the YES side measured | **141** (20 ranked + 120 uniform sample + 1 candidate) |
| YES **refuted** by a realised pose at `S(0.10, 10°)` | **139** |
| YES cover bought | **2** — both close one half only (§4c-ter) |
| YES child **dead** | **0** |
| NO child dead, attributable to the slot box (control-checked) | **1** — `c0_Y0076 TL(0,0)`, `tau 5 → 4` |
| **BOTH children dead (= the node dies)** | **0** |
| realised (pose in `S`, free second meeter) interior-disjoint pairs | **0** |

## 3. The population metric

`tau ≥ budget` is what keeps a node alive, and the LP's dual is the maximum fractional packing of
admissible core-avoiding unit squares — the node record's `packing` list, each entry a square with
its dual value `y`. So the PI's selector

    w_S(node, slot) = Σ { y : the dual square's pose lies in S(slot) }  ≥  0.5

is literally "how much of the reason this node is alive is a square sitting in the near-simple
slot position". `pop158.py` computes it over every alive A57/A60 node (`corpus._alive`, the same
test A141/A157 used), with the zone written in the world frame as in §2.

## 4. What was measured

### 4a. The YES side has an upper bound on `r`, and it is tiny

`xover158.py` bisects the largest radius at which every sampled free meeter of `int C` is forced
to overlap `K'(S_r)` (`r_lane`) and every conditioned meeter is blocked (`r_M`); `r_yes =
min(r_lane, r_M)` is an UPPER bound on the closable radius, since it comes from a finite sample —
above it the YES kill is **refuted by a realised pose**, no cover needed. `pair158.py` goes
further and realises an explicit interior-disjoint pair (a pose IN `S`, and a free second meeter),
which refutes the PI's geometric claim itself and not only the leaf.

### 4b. The NO side has a lower bound on `r` and on `tt`, and it is not tiny

`caselp` drops an LP row only if the centre is inside the zone by `EPS_ZONE = 2·10⁻³` and the tilt
inside a `t`-interval by `EPS_TH = 0.3°` (`NoFam.inside_many`). So **any `S` narrower than
4·10⁻³ in centre or 0.6° in tilt exempts nothing at all** and the NO child is bit-for-bit the
original LP. That is a floor below which the NO branch cannot even be attempted, independent of
the geometry.

### 4c. The two windows do not meet

Measured thresholds — `results/xover158_tt.jsonl`, `results/xover158.jsonl` (YES) and
`results/no158.jsonl` (NO); assembled in `results/summary158.json`.

**The YES side, `r_yes` = the largest radius at which no free meeter and no conditioned meeter
escapes `K'(S_r)` (an UPPER bound: it comes from a 400,000-pose sample, so the true threshold can
only be smaller).**

| cell | `r_yes` at `tt = 0` | largest `tt` with `r_yes ≥ 0` | binding |
|---|---|---|---|
| `c0_Y0076 TL(0,0)` | 3.66·10⁻⁴ | **0** (refuted at `r = 0` from `tt = 0.5°`) | `r_lane` (`r_M` = 3.6·10⁻²) |
| `c0_Y0787 BR(0,1)` | 4.88·10⁻⁵ | **0** | `r_lane` (`r_M` = 4.1·10⁻²) |
| `c0_Y0959 TR(0,1)` | 2.92·10⁻⁶ | **0** | `r_lane` (`r_M` ≥ 0.25) |
| `k5_11_interior_Y0130 TR(0,0)` | **refuted at `r = 0`** | — | `r_lane` |
| `k5_11_interior_Y0147 TR(0,0)` | **refuted at `r = 0`** | — | `r_lane` |
| top-20, the other 15 | 4.98·10⁻⁵ … 1.15·10⁻³ | 0 on every one | `r_lane` |

`r_lane` is what binds everywhere; `r_M` (whether the hypothesis square `H` can still reach the
cell) is one to four orders of magnitude looser. `r_M` is itself a sampled bound, so it is
"not refuted", never "certified 0".

**The NO side, on `c0_Y0076 TL(0,0)`** (`tau = 5` → kill iff `tau < 5`):

| `r` at `tt = 10°` | 0.0025 | 0.005 | 0.01 | 0.02 | 0.03 | 0.04 | 0.045 | 0.05 | 0.10 |
|---|---|---|---|---|---|---|---|---|---|
| `tau` | 5 | 5 | 5 | 5 | **4** | **4** | **4** | **4** | **4** |

| `tt` at `r = 0.10` | 0.5° | 1° | 1.5° | 2° | 5° | 10° |
|---|---|---|---|---|---|---|
| `tau` | 5 | 5 | 5 | **4** | **4** | **4** |

So the NO child needs `r ∈ (0.02, 0.03]` and `tt ∈ (1.5°, 2°]`, against a YES child that closes
only at `r ≤ 3.66·10⁻⁴` with the tilt **pinned**. Two orders of magnitude in `r`, and a tilt
window the YES side does not survive at all.

**And the gap is arithmetic before it is geometric.** `EPS_ZONE = 2·10⁻³` / `EPS_TH = 0.3°` mean
that no `S` the YES child could ever close on exempts a single LP row, so on such an `S` the NO
child is the original LP by construction — `tau` unchanged, `NoFam` inert. Refining the split
(partitioning `S` and running the leaf per piece, as A141's `lane_corner_split` does for a
conditioned box) does not help: the pieces must still be ~`10⁻⁴` wide in the centre, so
`S(0.10, 10°)` would need ≳ 10⁵ pieces per tilt slice, each with its own cover, and the NO child
would still be the one on the whole `S`.

### 4c-bis. What the leaf is refuted BY, and what it is not

`xover158.py` / `yesscreen158.py` refute the **leaf**: a realised pose in `R'(C | S)` means the
certified bound `LANE_K'(C | S)` cannot be 0. `pair158.py` was written to refute the PI's
**geometric claim** as well, by realising an explicit interior-disjoint pair (a pose IN `S`, and a
free second meeter of the cell). It found **none**: over the six PI cells at `(r, tt) ∈
{0.10, 0.01} × {10°, 0.5°}`, `600,000` draws each, the maximum pair gap is **negative everywhere**
(−6.1·10⁻⁴ on `c0_Y0959`, −0.67 on `k5_11_interior_Y1110`). So

> **the PI's geometry is not refuted — the `K'`-based leaf is.** `K'(S)` is the intersection over
> the WHOLE box `S`; the free meeter clears that intersection while still overlapping every
> individual square with a pose in `S`. The leaf can only discharge with a point shared by *every*
> pose of `S`, which is far stronger than "the `S`-square blocks the intruder".

The repair is the obvious one and it is priced: partition `S` and run the leaf per piece (A141's
`lane_corner_split` shape). The pieces must be `≲ 3.7·10⁻⁴` in centre half-width and `< 0.5°` in
tilt, i.e. `≈ (0.2 / 7.3·10⁻⁴)² × (20 / 1) ≈ 1.5·10⁶` pieces for `S(0.10, 10°)`, each needing its
own cover at ~1 s — **≈ 400 CPU-h per cell**. Not affordable, and the NO child would still be the
one on the whole `S`.

### 4c-ter. The two cells where a cover WAS bought

Two of the 141 screened cells were not refuted by the screen, so the certifying cover was run
(`yescert158.py`, both tilt pieces, 5–7 s each):

| cell | `LANE_K'(C \| S)` | `M(C \| S)` | `1 + LANE + M` | verdict |
|---|---|---|---|---|
| `k5_11_interior_Y1110 TR(0,0)` | **0 (certified)** | 1 | 2 | no kill |
| `k5_16_interior_Y1014 TL(1,0)` | 1 | **0 (certified)** | 2 | no kill |

This is the first time the conditional lane cover has closed at all (`LANE_K'(C | S) = 0` on
`Y1110`, both pieces) — and the two cells fail on *opposite* halves, which is why neither is a
kill. Note that A141's own `verdict` field reads `KILL` on both, because A141's rule is
`LANE + M ≤ 1`; the conditional leaf's rule is `1 + LANE + M ≤ 1`, and `yescert158.py` applies the
latter.

## 4d. The control every NO kill is quoted against

A `tau < budget` from `no158.py` is **not** by itself attributable to the slot box, for two
reasons, and both were live in this corpus:

* the re-solve uses A135's **exact** cores, which are strictly larger than several nodes' stored
  ones, so the re-solve alone can move `tau`;
* several A57 records carry `converged = false` — `k5_16_interior_Y0226` is
  `converged = false, dead_unconverged = true, minmass ≈ 1.1e-9, maxcov = 2.0` with a stored
  `tau = 3.99999999`, i.e. its stored `tau` is not a bound at all, and it is "alive" only because
  A124's rule refuses to let a non-converged LP be a verdict. The three A57 PI nodes
  (`Y0130`, `Y0147`, `Y1110`) are also `converged = false` with `dead_unconverged = false`.

So `no158.py --radii -1` runs the **control**: the identical `ExactHyp(..., scope="exall")`
re-solve with **no `NoFam` at all**. A kill is credited to the split only if the control does not
also kill (`sum158.py`, `kill_at_PI_box`). The control results are in `results/no158.jsonl` with
`control: true`.

## 5. Certificates

The NO child emits a `case-measure-certificate-v1` through A135's `make_cert` (the frozen emitter
with the LIVE `ExactHyp`, so the exact cores in the LP row filter and in the certificate are the
same objects) and A136's `a136lib.narrow` (NO zone rounded INWARD, intersected with the written
box, `zone_sub_box` decided on the written rationals and raising on failure). The arbiter is the
FROZEN `verify_case.py`; `verify_param.py` at the degenerate window `[s0, s0]` is the second,
independent implementation. `verify158.ps1` runs both, one process at a time, with a 1,500 s wall
that can only ABORT, never decide.

The YES child emitted **no** certificate: no cell reached `LANE_K'(C | S) = 0, M(C | S) = 0`, so
there was nothing to certify (`yescert158.py` is written and exercised, and would emit a
`polycore_slot_lane_v1` with one new field `s_box` the moment a cell closed). Caveat **A118-O1**
stands throughout: a LANE kill is exact-pin form, class-`S` composition; the A57 nodes here carry
`delta = 10⁻²` slack pins (pin boxes of half-width `10⁻²/√2 = 7.07·10⁻³`), so their YES branch
would additionally owe the A152 caveat.

**Both emitted certificates PASS the frozen arbiter.**

| certificate | atoms | total | verify_case (sha `521cb01f…`) | boxes / exempt |
|---|---|---|---|---|
| `no_c0_Y0076__TL0_0__r0.1_tt10.json` | 4 | `103/25` = 4.12 | **PASS**, 1.0 s | 7,262 / 1,863 (core 1,861, nofam 2) |
| `no_k5_16_interior_Y1014__TL1_0__r0.1_tt10.json` | — | `4120003/1000000` | **PASS**, 6.7 s | — |

`verify_param.py` (sha `0c58485c…`) **rejects both as MALFORMED — "unexpected format
'case-measure-certificate-v1'"**: it consumes the PARAMETRIC schema, not a fixed-side
`case-measure-certificate-v1`, so the second-verifier cross-check is not available for this
certificate kind (A136 likewise uses `verify_case.py` as the arbiter). The `Y1014` certificate is
**true but not attributable**: its control (§4d) also kills, so it is not evidence about the slot
box, and A158 does not claim it as a split result.
