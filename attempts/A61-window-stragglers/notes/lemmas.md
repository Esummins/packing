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

Measured effect at the baseline shrink (τ0, the quantity P6(v)'s gate is stated on):

| row | budget | A53 cert τ0 | A61 τ0 (enriched) | slack0 | gate 0.5 |
|---|---|---|---|---|---|
| k6_21 | 5 | 4.86910 | **4.500000** | 0.500 | pass (exactly at) |
| k5_17 | 6 | 5.83669 | **5.333333** | 0.667 | pass |

(Full table in `results/campaign61_progress.json`; see L3.)

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

## L4 [S] — what an A61 conversion licenses (unchanged from A56)

A61 produces no new soundness statement. A PASS is exactly A56 P3's parametric soundness theorem
applied to a NEW base certificate, and under P7's ledger rule the stratum-level claim is
certificate-fungible: the A53/A54 certificate remains the s0 witness, the A61 certificate carries
the window claim, both are recorded with provenance in the A56 scoreboard.
