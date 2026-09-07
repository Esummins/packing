# A117 T3 — accounting

Machine-readable: `results/accounting.json`, `results/equivalence.json`,
`results/no_reverify.jsonl`, `results/tc_replay.json`, `results/tc_sidecheck.json`,
`results/frozen.sha256`.

## 1. The frozen verifier

| file | sha256 |
|---|---|
| `verify_param.py` (v1, frozen, **unchanged**) | `0c58485c1a662453188af5b0aaf42099cf41c15f82a6647404598a44e8a505ec` |
| `verify_param_v2.py` (**new**, A117) | `153029baddfcb77a2fa5049fc29c4ed8042dc847262e3ecefd5636c77fce1806` |
| `verify_case.py` (frozen, unchanged) | `521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af` |
| `tcleaf.py` (A117 TC leaf check) | `5c127fe9712583fa6196a116c4942c965d68b5034d68fc853991709527d57a78` |

## 2. Equivalence with v1 — 30/30, byte-identical

Contract: the verdict **and every statistic v1 reports** (`boxes`, `covered`, `vacuous`, `exempt`,
`split`, `s_splits`, `exact_atom_checks`, `float_rejects`, `max_depth`, `max_s_depth`, `s_cells`,
`s_cells_built`, `depth_hist_covered`, `witnesses`); v2's only extra keys must be `exempt_core` /
`exempt_nofam`, their sum must equal `exempt`, and `exempt_nofam` must be 0.

| group | certificates | verdicts | identical |
|---|---|---|---|
| A96 `k5_11` G1 level 1 | 5 | 3 PASS / 2 FAIL | 5/5 |
| A96 `k5_11` G1 level 2 | 4 | 2 PASS / 2 FAIL | 4/4 |
| A96 `k5_11` L1 level 2 | 3 | 2 PASS / 1 FAIL | 3/3 |
| A96 `k5_16` G1 level 1 | 5 | 3 PASS / 2 FAIL | 5/5 |
| A96 `k5_16` L1 level 2 | 2 | 1 PASS / 1 FAIL | 2/2 |
| A96 resolver cells (narrow slab, depth 56) | 2 | 2 PASS | 2/2 |
| A100 protected classes `k3_02`, `k4_11` | 4 | 2 PASS / 2 FAIL | 4/4 |
| A99 level-3 k0 tree nodes | 2 | 1 PASS / 1 FAIL | 2/2 |
| A57 / A95 / A61 parametric certificates | 3 | 2 PASS / 1 FAIL | 3/3 |
| **total** | **30** | **16 PASS / 14 FAIL** | **30/30** |

Box counts span 6 890 to 14 518 182.  Zero regression surface is not an assumption: v1 *raises*
`nofams unsupported`, so no certificate emitted before A117 contains a NO-family, and
`exempt_nofam = 0` on every row of the table confirms the new rule never fired on them.

## 3. NO-side parametric re-verification — the multiplier is removed, the wall is not

77 fixed-side certificates of A111 and A112 carry NO-families (A111 18, A112 59); 62 of them are
fixed-side PASSes.  `to_param117.py` converts **74 of 77**; the 3 refusals are exactly the
certificates whose tree contains a YES child, whose branch core is neither a slot nor a `Q_dy`
cover coordinate (§5).

48 certificates were re-verified over the whole window `[191/50, s0]` at the fixed-side run's own
depth (56), `jobs = 1`, with a 240 s per-certificate cap:

| | |
|---|---|
| **window-valid kills gained (window PASS)** | **16** |
| fixed-side PASS that becomes a window FAIL | **0** |
| capped at 240 s (no verdict either way) | 32 |
| window wall on the 16 PASSes | 710 s |
| the four fixed-side runs they replace | 73 s |
| **ratio** | **9.8× — the window pass is not cheaper** |
| window wall over all 48 | 8 390 s vs 716 s for four sides (11.7×) |

**The caps are not failures — they are wall.**  One capped certificate was re-run with a 2 700 s
cap as a probe (`results/no_reverify_probe.jsonl`): `k5_11_interior_Y0036_D07_D06_m2__hybrid__RN`,
fixed side **0.80 s**, window **PASS in 302.7 s** — i.e. **95× the four fixed-side runs** it
replaces.  So the 32 capped certificates are very likely window-valid too, and the wall ratio is
worse than the 9.8× the finished set shows, not better: the certificates that cap are exactly the
ones where the fixed side was cheapest.

**This contradicts the projection A112's note carried.**  A95 measured `0.062` of four fixed sides
for a level-1 A57 leaf, and A112's `verify_param_nofams.md` inferred "a 4× cut of the NO-side
certification wall".  On the NO-side corpus that inference does not hold, and the reason is
structural rather than incidental: a NO certificate is *tiny* at a fixed side (4–135 atoms,
0.6–5 s), because the NO-family exempts most of the container outright; the 4-D pass still has to
resolve the whole `s`-slab, and 32 of 48 do not finish in 240 s.  **What v2 buys is
window-VALIDITY, not wall.**  The four-side grid was never the expensive part of a NO kill.

Per region (NO certificates only; a region needs *all* of its NO leaves to PASS on the window):

| region | NO certs | window PASS | capped |
|---|---|---|---|
| `k5_11_interior_Y0036_D07_D03` | 4 | 3 | 1 |
| `k5_11_interior_Y0036_D07_D06` | 4 | 0 | 4 |
| `k5_11_interior_Y0054_D00` | 13 | 6 | 7 |
| `k5_11_interior_Y0084_D03` | 4 | 0 | 4 |
| `k5_11_interior_Y0108_D07` | 1 | 0 | 1 |
| `k5_11_interior_Y0186_D00_D00` | 3 | 0 | 3 |
| `k5_11_interior_Y0738_D00` | 2 | 0 | 2 |
| `k5_16_interior_Y0054` | 1 | **1** | 0 |
| `k5_16_interior_Y0083_D02` | 3 | 0 | 3 |
| `k5_16_interior_Y0083_D03` | 4 | 0 | 4 |
| `k5_16_interior_Y0119_D07` | 1 | 0 | 1 |
| `k5_16_interior_Y0984` | 8 | 6 | 2 |

## 4. Lemma TC as a leaf — 170/170 fires reproduced, 1.7 M sampled pairs, 0 counterexamples

| | |
|---|---|
| TC fires replayed | **170** (A112 10, A111 160) |
| reproduced by the new EXACT check | **170 / 170** |
| not reproduced | **0** |
| sampled pose pairs (≥ 10⁴ per fire) | **1 700 000** |
| counterexamples | **0** |
| worst SAT gap over all samples | **−0.000898** (every sampled pair strictly overlapping) |
| smallest exact slack `need_lo − c_max` | **+3.36 × 10⁻⁵** |
| A111 census, rebuilt vs stored | **160 = 160** TC (and 1 403 CORE-MEET, not replayed here) |

The A111 rebuild is faithful fire-for-fire, so the replay is a replay and not a re-measurement.
Lean: `TCSupportMin`, `TCCentreDist`, `TCLeaf`, `TCLeaf_of_TCCentreDist` are frozen as `Prop`
definitions — `[C]`, **not axioms**, so the project's axiom roster is unchanged; the missing step
is the separating-axis theorem for interior-disjoint convex polygons, which `Band.lean` records as
not formalised here.

**Side transfer (`results/tc_sidecheck.json`).**  All **10 of A112's TC fires are window-valid**:
in 6 of them both boxes are branch/conditioned bins (the node's own `s`-independent support boxes),
and in the other 4 the second box is class pin `pin3`, whose core is `(3/2, 1/2)` — two slot
anchors with `β = 0`, so the pin box does not move with the side either.  A111's 160 fires are not
claimed window-valid here: both of their boxes come from a shadow at its own side `s*` mapped into
the node frame, and their transfer is A111's frame-slack question (`|s* − s0|` = 0.0097 for S02,
0.0085 for S07).

## 5. What A112's region-tree option can now claim window-valid

**One thing, and it is the free kill, not a certificate kill.**  `k5_11_interior_Y0041_D02` — a
whole A57 open box that A112 kills at the root under all four branching orders, with 0 LPs and 0
certificates, by a single Lemma-TC fire (`bin0` vs `pin3`) — is now **window-valid**: the fire
reproduces under A117's exact rational check, both of its boxes are `s`-independent, and 40 000
sampled pose pairs across the four orderings overlap strictly.  Its only obligation is Lemma TC
itself, which is `[C]` (exact machine check + frozen Lean statement), not a Lean theorem.

**Every certificate-based region-tree kill stays s0-only**, and the blocker has moved from the NO
side to the YES side.  A 3-node kill is (YES certified) ∧ (NO certified); A117 makes the NO half a
single window certificate, but the YES child's branch box enters *its* certificate as a **core**,
and A96's `core_affine` refuses a branch-box coordinate outright — it is neither a slot nor a
`Q_dy` cover coordinate (`to_param117.py` refuses `…Y0054_D00_m2__stranded__RNY`,
`…Y0108_D07_m2__hybrid__RNY`, `…Y0083_D02_m2__stranded__RYN` with exactly that message).  Until a
YES-core anchoring exists, no `(YES, NO)` pair can be window-valid, and A96's `regionopt96.py`
should keep `no_side_window = "s0-only"` on those transfers.

## 6. THE VERIFIER IS DETERMINISTIC; THE EMISSION IS NOT

`certify.py --loop_cols` re-solves the node LP under a time limit before emitting, so a
certificate's atom set is wall-clock dependent — the frozen VERIFIER is deterministic, the EMISSION
is not; kills are reproduced by replaying certificates, never by re-emitting.  (Recorded in
`notes/frozen_verifier_v2.md`, in the header of `verify_param_v2.py` itself, and in A57's
`code/FREEZE_TAGS.txt`.)
