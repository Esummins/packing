# A134 — results

`s0 = 969271/250000 = 3.877084`.  Both certificates are `local-cert-t-v2` = A133's
`local-cert-t-v1` plus the `pcert` field; SHA-256 and the per-certificate record are in
`certs/manifest.json` and `results/check_local_t2.json`.

## T1 — the re-emission with positivity certificates

| `N` | leaves | rays | rows | tree wall | **pcert wall** | file | `env` h/S/w | **pcert pieces** (1-var / 2-var) | **coeffs** | max depth |
|---|---|---|---|---|---|---|---|---|---|---|
| `S07_trump5_r0.10_rho40` | 2 140 | 768 | 25 377 | 23.2 s | **0.5 s** | 1.34 MB | 21 / 21 / 336 | 210 / 252 | 4 872 | **0** |
| `S02_k5_11_r0.20_rho10` | 16 406 | 1 950 | 270 199 | 172.7 s | **1.4 s** | 13.47 MB | 50 / 50 / 944 | 414 / 830 | 14 936 | **0** |

The trees, leaves, rows, Farkas bounds and certified minima are IDENTICAL to A133's
(3.877108392 and 3.877085705): `pcert` is pure addition.  **Every envelope of all four families
certifies at Bernstein depth 0 — one piece, no subdivision — so the "cost in leaves" of replacing
the checker's Sturm argument by the same Bernstein form the kernel can run is ZERO.**  File growth
is +0.7 % (S07) and +6.6 % (S02); the 2-variable pieces carry a 4×4 coefficient grid each and the
1-variable ones 4 coefficients each.

The `w` family splits by degeneracy: S07 has 252 genuine boxes, 42 with `t_o` pinned to `0` and 42
with `t_w` pinned; S02 has 830 / 100 / 14.  The pinned ones are certified as univariate chains
after substitution (`substY0` / `substX0`).

Three constants Lemma RELAX needs were NOT in A133's certificate and are now emitted with their
own certificates: `S_lo`, `S_hi` (the McCormick corners, and the chord scale `S_abs` of envelope
(A)) and `K = max(1 − cos φ)`.  That is why the `S` family carries five chains per entry rather
than two.

## T1 — the independent check (`code/check_local_t2.py`, `results/check_local_t2.json`)

| `N` | A133's checker | its wall | `pcert` | its wall | mutations |
|---|---|---|---|---|---|
| `S07_trump5_r0.10_rho40` | **ok** | 6.7 s | **ok** | 0.5 s | bump REJECTED, shrink REJECTED, drop n/a |
| `S02_k5_11_r0.20_rho10` | **ok** | 74.6 s | **ok** | 1.6 s | bump REJECTED, shrink REJECTED, drop n/a |

`check_local_t2: 2 certificate(s), ALL VALID`.  `drop` (delete one piece of a chain) is `n/a`
because at depth 0 every chain has exactly ONE piece; `shrink` (halve the last piece's interval)
is the same mutation for a one-piece chain and is rejected, so the tiling condition is exercised.

## T2 — Lean (`lean/PackingCertMathlib/PackingCertMathlib/LocalCertT2.lean`)

`lake build PackingCertMathlib.LocalCertT2` = **19.5 s** on top of the existing build.
**36 theorems, axiom roster `[propext, Classical.choice, Quot.sound]` on every one**
(audit `lean/PackingCertMathlib/scratch/A134Axioms.lean`, 14.2 s) — no project axiom (in
particular NOT `Local.sat_selection`: `SatInterior.sat_selection_thm` proves it), no
`native_decide`, no `sorry`.

| piece | theorems |
|---|---|
| §1 subdivided positivity | `peval_padZ`, `posChain_sound` |
| §2 the bivariate certificate | `peval2_padd2/pscale2/pmul2/scaleP/linAmul2`, `posAuxP_nonneg`, `posCheck2_sound`, `posColumn_sound`, `posGrid_sound` |
| §3 the degenerate side | `peval_substY0`, `peval_substX0` |
| §4 the envelope polynomials | `peval_hPoly`, **`wT_ge_aff`**, `sRel_mul`, **`sRel_le_aff`**, **`sRel_ge_aff`**, `peval2_wPolyT`, `wNum_eq`, **`wrel_ge_plane`** |
| §5 rational intervals | `IQ.add_mem/sub_mem/neg_mem/mul_mem`, `cosI_mem`, `sinI_mem`, `axI_mem`, `cosRelI_mem`, `sinRelI_mem`, **`wLoQ_le`** |
| **§6 (C2)** | `gsel_le_gapHi`, `selection_cover`, **`selectionOk_sound`** |
| **§7 (C3)** | **`relax_wall`**, `axis_decomp_t`, `cosRel_le_one`, `peval_cPoly`, `one_sub_cosRel_le`, `corr_bound`, `absQ_chord`, `relax_U_A`, `relax_U_B1`, `relax_U_B2`, **`relax_selection`** |
| **§8 (C4)** | **`localHyp_bodies`** |

**(C2), (C3) and (C4)'s geometric half are discharged.  `certCover_s07` and hence
`localDead_s07_t` / `localDead_s02_t` are NOT obtained** — see §9 of the Lean file and
`notes/lean.md` for what remains, which is bookkeeping of four named kinds and, the point of the
audit, **no missing library lemma**.

## T3 — the elaborator wall

`code/gen_pcert_lean.py` writes a certificate's whole `pcert` out as Lean data and asserts
`posChain` / `posGrid` on ALL of it by `native_decide` — the loop generator → checker → kernel,
closed on real certificate data.

| file | entries (h / S / w) | Lean source | `lake env lean` wall |
|---|---|---|---|
| `scratch/A134PCertTiny.lean` (`S02 (0.02, 2°)`) | 2 / 2 / 10 | 0.02 MB | **16.8 s** |
| `scratch/A134PCertS07.lean` | 21 / 21 / 336 | 0.94 MB | **36.2 s** |
| `scratch/A134PCertS02.lean` | 50 / 50 / 944 | 3.07 MB | **81.2 s** |

All three PASS (`hAll`, `sAll`, `wAll` by `native_decide`).  Subtracting the ~15 s of import
overhead: 21 s for S07's 4 872 coefficients and 66 s for S02's 14 936 — roughly linear, ≈ 4.4 ms
per coefficient, and the KERNEL is not the wall.

**A126's finding recurs exactly.**  The first attempt, one `List WEnt` literal with 336 entries,
died in the elaborator: `(deterministic) timeout at isDefEq, maximum number of heartbeats
(200000)`.  A126's remedy works verbatim — batches (32 entries per `private def`, concatenated
linearly) plus `set_option maxHeartbeats 2000000`.  With batching S02 is **81 s, far under the
brief's 10-minute gate**.

**Projection for the remaining eight certificates** (A133's manifest, per-certificate `env`
counts scaled by the S07/S02 fit `wall ≈ 15 s + 4.4 ms × coeffs`, coefficients ≈ 4 per 1-var piece
and 16 per 2-var piece): the eight together carry ≈ 2 900 `w` entries and ≈ 190 h/S entries, so
≈ 47 000 coefficients, ≈ **3.5 min of `native_decide` in total** for the `pcert` half.  The LEAF
half is the expensive one and is A126's measurement, not re-measured here (22 s + 19 s for S07's
2 302 leaves, 40 s + 67 s for S02's 32 570, on A119's certificates; A133's `t` leaf counts are
smaller — 2 140 and 16 406). The eight were NOT built, as the brief directs.
