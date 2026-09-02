# A61 — closing G-A56-1: the 12 s0-only stratum kills

Window W = [191/50, 969271/250000] = [3.82, 3.877084]. All semantics, soundness statements and
measured laws are A56's (`attempts/A56-sparametric/notes/soundness.md`, P0–P7); A61 adds no new
soundness content, only a repair pipeline and its measurements. Labels: [T] theorem, [M] measured,
[S] soundness statement.

## L1 [T+M] — THE eps_geo LEAK: why A56's repair recipe converted the LP but not the 4D verifier

**Statement.** In `attempts/A56-sparametric/code/resolve_margin.py` the row-shrink margin
`eps_geo` is installed by assigning `lpbox.EPS_GEO = a.eps_geo` **in the driver's own process**,
which governs step 3 (the node solve) only. Step 4 invokes A54 `certify.py` as a **subprocess**
with `--scale 0 --scale_cap 1.06 --loop_cols` and **no `--eps_geo`**, so inside that subprocess
`lpbox.EPS_GEO` keeps its module default `1e-4`. `certify.py --loop_cols` re-solves the node
(rows *and* columns) after every failed verification round. Therefore the certificate that
finally PASSes is built from a measure re-optimised at 1e-4 of shrink — the positional slack the
recipe bought is spent again inside certify, and the 4D verifier sees an unshrunk certificate.

**Proof that it fired, from A56's own logs (not a code reading).** With `EPS_GEO` held fixed, a
witness-feedback round only ADDS rows, so τ is nondecreasing across rounds. Every one of A56's
seven "certify PASS but 4D open" rows PASSed at round ≥ 1, and τ **fell** at the first re-solve:

| row | eps_geo asked | τ round 0 | τ at the PASSing round | PASS round |
|---|---|---|---|---|
| k5_10 | 0.001 | 5.58824 | 5.50000 | 1 |
| k6_20 | 0.001286 | 4.66667 | 4.50000 | 1 |
| k6_21 | 0.001286 | 4.60000 | 4.50000 | 1 |
| k6_29 | 0.0015 | 4.71811 | 4.50000 | 1–4 |
| k5_17 | 0.001846 | 5.40000 | 5.33333 | 3 |
| k6_27 | 0.001 | 4.67098 | 4.62162 | 3 |
| k5_05 | 0.002948 | 5.00000 | 5.00000 | 2 |

A drop of τ under strictly added rows is impossible at fixed shrink; it is exactly the signature
of the shrink being released from `eps_geo` to `1e-4`. 7 of 7. ∎

**Consequence for A56's banked law.** P6(v)'s conversion statistics ("eps_geo ≥ 0.0015 converted
13/16, < 0.0015 converted 0/5") are measurements of a pipeline in which the requested eps_geo
survived only when certification happened to PASS at round 0. The *threshold* reading stands (a
round-0 PASS keeps the full shrink); what does **not** follow is that the 12 survivors are
eps_geo-unrepairable — they are the rows that needed ≥ 1 feedback round and therefore never got
the shrink they were priced for.

**The fix (A61).** `certify.py` already carries the exact flag pair for this:
`--eps_geo <eps> --no_resolve` ("set EPS_GEO but skip the initial re-solve — the node json is
already solved at that EPS_GEO"). `resolve61.py` passes it. Soundness is unaffected in either
direction: the arbiter is the unmodified exact fixed-s verifier, which never sees `EPS_GEO`
(A57 T14 / A56 P3 — the shrink is a robustness margin on the LP rows, never a relaxation of what
is verified). The leak cost *completeness*, not soundness; no A56 PASS is invalidated by L1.

## L2 [M] — the column pool is the lever that moves τ0, and A56 left it on the floor

A55/k3_ext E3 and A57 T4/T13: the progress variable is the COLUMN (atom) set, not τ's own
dynamics; rows only ever raise τ. A56's `resolve_margin.build_warm` read columns from ONE file
(`A53/results/nodes/<name>.json`) — 25–90 atoms — and then generated 4.9k–7.8k orbits inside the
time limit, which it checkpointed to `A56/results/nodes/<name>_state.json` and never re-used.
A61's `enriched_warm` folds every orbit this lab ever produced for the node (warm57's A53/A54/A55/
A57 sources, extended to A56's and A61's own `_state` checkpoints) as the *initial* column pool.

Measured effect at the baseline shrink (τ0, the quantity P6(v)'s gate is stated on), all 12 rows:

| row | budget | A53/A54 cert slack | A61 τ0 (enriched) | slack0 | gate 0.5 |
|---|---|---|---|---|---|
| k5_05 | 6 | 0.66623 | 5.000000 | **1.00000** | pass |
| k5_17 | 6 | 0.33499 | 5.333333 | **0.66667** | pass |
| k5_10 | 6 | 0.07749 | 5.500000 | **0.50000** | pass (exactly at) |
| k6_20 | 5 | 0.10748 | 4.500000 | **0.50000** | pass (exactly at) |
| k6_21 | 5 | 0.13090 | 4.500000 | **0.50000** | pass (exactly at) |
| k6_29 | 5 | 0.36490 | 4.500000 | **0.50000** | pass (exactly at) |
| k5_02 | 6 | 0.00055 | 5.605206 | 0.39479 | fail |
| k5_12 | 6 | 0.16330 | 5.620000 | 0.38000 | fail |
| k6_27 | 5 | 0.07888 | 4.620690 | 0.37931 | fail |
| k5_03 | 6 | 0.16331 | 5.666667 | 0.33333 | fail |
| k5_13 | 6 | 0.03745 | (see results) | | |
| k5_14 | 6 | 0.13819 | (see results) | | |

The enrichment moves every row, and by a large factor on the thin ones (k5_02: 0.00055 → 0.395,
a 700×). Full records in `results/resolve61_*.json` and `results/campaign61_progress.json`.

## L2b [M] — the enriched guard LP lands on EXACT rationals, and the modal value is the gate

Four of the six rows that clear the gate land on τ0 = budget − 1/2 to 12 significant figures
(k5_10: 5.500000000001527 at budget 6; k6_20: 4.500000000000028; k6_21: 4.500000000000409;
k6_29: 4.499999999999991 at budget 5); the other two land on budget − 2/3 (k5_17: 5.333333333)
and budget − 1 (k5_05: 5.0). The below-gate rows land on 5.605206, 5.62, 4.62069, 5.666667 —
also exact rationals (5.62 = 281/50, 4.62069 = 134/29, 5.666667 = 17/3). So the guard LP is not
drifting toward a continuum optimum: with a large enough column pool it snaps to a small-
denominator rational floor, and for this family of strata that floor is **exactly** P6(v)'s
repairability threshold.

**Operational consequence (cost a full campaign pass to learn).** A61's first pass compared
`slack0 < 0.5` in floating point and rejected k5_10 (slack0 = 0.4999999999984732) and k6_21
(0.49999999999959144) — rows sitting exactly ON the law, refused on solver dust, each after a
~25-minute LP. The gate now carries `--gate_tol` (1e-6). Any future use of a P6-style measured
threshold against an LP optimum must do the same: these τ are exact rationals plus noise, and
the interesting rows pile up precisely at the threshold rather than scattering around it.

## L2c [M] — BLAS oversubscription, not RAM, is the failure mode (A57 T18, re-confirmed)

A61's first launch lost k5_05's stage A twice to `MemoryError: bad allocation` with ~10 GB
physically free, exactly the signature A57 banked in T18. Two mitigations were applied and both
are kept: (i) single-thread pinning of every BLAS backend (`OPENBLAS/OMP/MKL/NUMEXPR_NUM_THREADS
= 1`) set in the process environment BEFORE numpy or highspy is imported, in `resolve61.py`,
`campaign61.py` and the child environment; (ii) a memory-bounded LP — `prune_cols = 3` (A14
semantics: only ZERO-weight columns with strictly positive reduced cost are dropped, they are
regenerable by the column oracle, and dropping them cannot lower τ, so it is a pure memory
bound and not a change to the LP's value) plus a `--max_atoms` cap on the initial pool and a
`lp_robust` ladder that steps the pool down rather than losing the stratum.

## L3 [M] — the A61 pipeline and its gate

`code/resolve61.py`, per stratum:

1. **enriched warm** — columns from every artefact (L2); rows = A53's `rows_all` + the 27-point
   stencil around every 4D witness A56/A61 recorded (an LP row is the demand μ(Q) ≥ 1 at a
   placement; adding it at s0 can only tighten the measure — A56 P3).
2. **stage A**, `EPS_GEO = 1e-4`, cap `--lp_time`: measures τ0 and `slack0 = budget − τ0`.
3. **GATE** (P6(v), the 1500 s lesson): `slack0 < 0.5` ⇒ record and stop. dτ/dε ≈ 1.4e2 makes
   ε = 0.003 cost ≈ 0.42 of budget, so a sub-gate row cannot pay for it and a certify round on it
   is a pure loss (~1500 s). No certify round is ever burnt below the gate.
4. **stage B**, `EPS_GEO = eps_geo` (0.003), warm-started from stage A's own columns and rows.
5. **certify** with `--eps_geo --no_resolve` (L1) `--warm_state <stage-B checkpoint>`.
6. **4D** `verify_param` at depth 48 over W, walking the full anchoring ladder
   gap → nearest-wall → mid-band on FAIL (anchoring is completeness, never soundness — A56 P3 —
   and a 4D run costs 10–250 s, so A56's single `gap` attempt left a cheap lever unused).
7. **C2** on a PASS: the unmodified A53 `verify_case.py` at s_lo, the midpoint and s0.

## L5 [M] — dτ/d(eps_geo) is HALVED by the enriched pool, so P6(v)'s 0.5 pre-gate is ~2x conservative

A56 measured dτ/dε ≈ 1.1–1.7 × 10², making eps_geo = 0.003 cost ≈ 0.42 of budget, which is where
the 0.5 gate comes from. A61 measures it directly on its three first-pass conversions:

| row | τ0 | τ(0.003) | dτ/dε | cost of ε = 0.003 |
|---|---|---|---|---|
| k5_17 | 5.333333 | 5.500000 | 57.5 | 0.167 |
| k6_20 | 4.500000 | 4.689227 | 65.3 | 0.189 |
| k6_29 | 4.500000 | 4.760417 | 89.8 | 0.260 |

**57–90, i.e. roughly half A56's figure.** The reason is structural: a shrunk row is a harder
constraint, and how much harder depends on whether the measure has an ALTERNATIVE atom that
still covers the shrunk square. A rich column pool supplies those alternatives, so the same
shrink costs less. The lever that drops τ0 (L2) also flattens the shrink curve.

Consequence: the P6(v) pre-gate at 0.5 was calibrated on the un-enriched pipeline and, under
enrichment, rejects rows that can in fact pay (cost ≈ 0.26 worst case, not 0.42). A61 therefore
splits the gate in two:
* **pre-gate** on slack0 — an extrapolation, now recalibrated to 0.30 for enriched runs;
* **post-shrink gate** (`--gate_b`, default 0.03) on the MEASURED `budget − τ(eps_geo)` — this is
  the real condition for a certificate to exist (certify builds `total = τ·scale` with
  `scale ≥ 1.005`, so it needs `budget − τ > 0.005·τ ≈ 0.028`).

The abort-early discipline is preserved exactly — no certify round is ever burnt on a row that
provably cannot certify — while the honest test moves from a prediction to a measurement. The
extra cost of being wrong is one stage-B LP (~15 min), not a ~1500 s certify burn.

## L4 [S] — what an A61 conversion licenses (unchanged from A56)

A61 produces no new soundness statement. A PASS is exactly A56 P3's parametric soundness theorem
applied to a NEW base certificate, and under P7's ledger rule the stratum-level claim is
certificate-fungible: the A53/A54 certificate remains the s0 witness, the A61 certificate carries
the window claim, both are recorded with provenance in the A56 scoreboard.
