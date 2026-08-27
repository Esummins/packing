# A35 / M1b — M1 re-run on the repaired row basis v2

Code: `code/m1b_enum.py` (+ v2 additions to `code/strata_lib.py`, opt-in; the v1
path is byte-identical and asserted intact in the self-check, so M2/M3 are
unaffected). Data: `results/m1b_strata.json` (5.5 MB). Runtime 5 min, single
process (cap was 1 h). Rigour tags as in M1, plus `[LP]` = float64 HiGHS, with
every headline LP verdict re-checked by a rational certificate verified in
mpmath.iv.

## BASIS v2 — precise statement

| rows | content |
|---|---|
| 0–35 | verbatim A22 `krawczyk_cert.json` constraints 0..35 |
| ~~36, 37~~ | v1's `D0-1`, `D0-3` centre-distance surrogates — **dropped** |
| 36 `F0-1a` | flush (0,1), owner 0 right edge vs corner 3 of sq1 |
| 37 `F0-1b` | flush (0,1), owner 1 left edge vs corner 2 of sq0 |
| 38 `F0-3a` | flush (0,3), owner 0 top edge vs corner 0 of sq3 |
| 39 `F0-3b` | flush (0,3), owner 3 bottom edge vs corner 3 of sq0 |
| 40 `C1-3x` | (1,3) corner-corner, **x-branch** (owner 1 left edge) |
| 41 `C1-3y` | (1,3) corner-corner, **y-branch** (owner 3 bottom edge) |

42 rows, all `t3lib` sep-row language, all dominance-valid at z-hat, all
`g_k(z-hat) = 0` to 6.7e-60.

**Both reported defects confirmed independently, in exact rational arithmetic:**

* `(1,3)`: centre distance² = **exactly 2** (so no `dist` row could ever have
  been active there), SAT gap 0 within ±4.7e-61 → genuine 14th contact pair,
  absent from v1.
* `(0,1)`, `(0,3)`: centre distance² = **exactly 1**, SAT gap 0 → flush
  contacts; the `dist` rows read 0 but pin only the centre distance.

**Menu semantics.** The two `(1,3)` branches are alternatives, not conjuncts
(true gap = max over branches). For the CONE analysis treating both as separate
rows with independent `λ ≥ 0` is exactly right (∂max = conv of the branch
gradients and `cone(conv{a,b}) = cone{a,b}`); for RANK/dof it is not. So the
stratum enumeration is run in **three variants**: `conj` (both maintained,
reference only), **`selx`** and **`sely`** (geometrically meaningful).

---

## 1. rank / self-stress / nonnegative self-stress

| | v1 (38 rows) | **v2 (42 rows)** |
|---|---|---|
| rank | 34 `[RFP]` | **34** `[RFP]`, Rump bound 2.39e-13, σ_min 0.1282 |
| self-stress dim | 4 | **8** |
| self-stress support | 20 rows | **29 rows** (all `[RFP]`-certified) |
| Farkas min verified lower bound | 0.229700 | **0.221300** |

> ### NO nonnegative self-stress on v2 — the alarm does **not** fire.
> The 0-1-3 block with the `(1,3)` diagonal brace does **not** carry one.
> Certified `[IV]`: all 42 products `∇g_k · y` verified **> 0** in mpmath.iv at
> dps 60 for a rational `y`, min = **0.221300**. Gordan ⟹ no nonzero
> nonnegative self-stress. This also re-certifies cone pointedness, boundedness
> of the multiplier polytope, and keeps the **FJ λ₀ = 0 branch empty at z-hat**.

---

## 2. λ* — the uniform floor: headline caveat, constant intact

> **The uniform floor over all 42 rows is 0.** Exactly two rows are *forced* to
> `λ = 0` over the entire multiplier polytope:
> **row 0 `W0c0[x=0]` and row 2 `W0c1[y=0]`** (square 0's corner-0-vs-left-wall
> and corner-1-vs-bottom-wall). Their max over `P` is 0.
>
> **Excluding exactly those two rows the floor is 0.047644047 — identical to
> v1's to all printed digits.** theory.md's constant survives the basis repair;
> only its *statement* needs the restriction.

| | v1 | v2 |
|---|---|---|
| floor (all rows) | 0.047644047 | **0** |
| floor (load-bearing rows) | 0.047644047 | **0.047644047** |
| Σλ* | 4.353502 | 4.518763 |
| `‖Aᵀλ* − e_s‖₁` `[IV]` | 9.68e-45 | **9.91e-45** |

**Impact on theory.md (A)/Consequence 1.** As written, `s(z) ≥ Φ(z) + λ_floor·G(z)`
with `G` summing **all** rows is **false on v2** (`λ_floor = 0`). The repaired
form sums the **40 load-bearing rows**, with the *same* constant 0.047644. The
only escapes with no first-order ascent guarantee are those opening **only**
rows {0, 2} — disposed of explicitly in §4.

**Structural obstacle found while doing the exact correction:**
`rank(A₂ over the 40 load-bearing rows) = 33`, not 34. There is **no square
34-row retained subsystem that avoids the two statically dead rows** — they are
geometrically essential (they pin square 0) but carry no load. The correction
therefore runs on a `[RFP]`-certified 33×33 block with λ pinned to *exactly* 0
on rows 0, 2, and the full 34-equation residual verified afterwards in `[IV]`.

---

## 3. Cone analysis — K blows up

| | v1 | **v2** |
|---|---|---|
| rows that can be zero (`Z0`) | 10 | **20** |
| minimal dead singletons | 28 | **22** |
| minimal dead pairs | 6 | **11** |
| min support | 32 | **29** |
| **K** (max break-set preserving the cone) | **6** | **13** |
| cone-alive break sets (of 2^n) | 223 | **70 499** |
| maximal alive sets | 16 | **72** |

Alive sets by size: 20, 179, 947, 3295, 7936, 13560, 16572, 14423, 8795, 3643,
970, 149, 10 (sizes 1…13). Method: aliveness is downward closed, so a
breadth-first sweep extending only alive sets by rows of `Z0` enumerates the
**entire** alive family — 122 339 LPs, exhaustive over all 2⁴² break sets.
Cross-check: 20 random cone-dead sets of size K+1 = 14 all got rational Farkas
witnesses verified in mpmath.iv (**20/20**).

Every alive break set is still drawn from a single 20-row family
`{0,1,2,3,4,8,9,10,12,21,22,23,26,29,36,37,38,39,40,41}` — the 22 rows outside
it remain singleton cone-killers.

---

## 4. Synthesis with the wedge test (5-test cascade)

Test order: **EMPTY** `[RFP]` → **CONE-DEAD** `[LP/IV]` → **WEDGED**
(M4's escape-cone LP, `C(B) = {v ∈ ker A_M : A_B v ≥ 0} = {0}`) → **COLLAPSE** →
**LOADPATH**.

**Wedge test validated first**: the same routine on the v1 basis returns
**81/81** wedge-empty for M1's 81 survivors, reproducing M4 §1 exactly.

| variant | alive | empty | wedged | collapse | loadpath | **TRUE SURVIVORS** |
|---|---|---|---|---|---|---|
| `conj` (reference) | 70 498 | 24 719 | 28 155 | 0 | 0 | **17 625** |
| **`selx`** | 19 799 | 4 463 | 2 961 | 0 | 0 | **12 375** |
| **`sely`** | 22 499 | 7 487 | 9 387 | 0 | 0 | **5 625** |
| union | — | — | — | — | — | **25 050** |

(cone-dead is 0 by construction — only alive sets are enumerated; every other
break set in the 2⁴² lattice is cone-dead. Collapse and load-path again add
nothing on top of the earlier tests.)

### The work queue is generated by exactly two seeds

Survivors of size ≤ 2 across all variants reduce to two mechanisms:

**Seed A — `{0, 2}` = `{W0c0[x=0], W0c1[y=0]}`**, survives in **all three**
variants. dof 1, movable, both broken rows open at rate 0.8165, and

> **`e_s · v = 9.0e-17` — the escape is FIRST-ORDER FLAT in s.**

The kernel vector moves **square 0 alone** (`|dc,dθ| = 1.0`, θ-component 0.8165,
`cx = cy = 0.408`): square 0 pivots in the bottom-left container corner, corner 0
sliding along `y=0` and corner 3 along `x=0`, while its flush contacts with
squares 1 and 3 are maintained *to first order*. This is exactly the break set
whose λ* is forced to 0, so §2's caveat is not hypothetical.

**Seed B — `{4}` = `{W1c0[y=0]}`**, a **single-row** survivor, in the `selx`
variant only (dof 1; dof 0 under `sely` and `conj`). Square 1 alone pivots,
rate 0.8165, again `e_s · v = 1.1e-16` — **first-order flat**. The `(1,3)`
y-branch blocks this rotation; the x-branch does not. v1's k = 1 layer was
*fully* disposed of; v2's is not.

**Interpretation (honest).** Both seeds are the same phenomenon: a 2-row flush
description of a flush contact between upright squares still admits a
first-order relative rotation. The true constraint — non-interpenetration —
forbids it at **second** order. So these are almost certainly first-order
artifacts of the linearization rather than real escapes, and they are **flat,
not descending**: nothing here says `s` decreases. But no first-order test can
close them, which is precisely why the queue exploded. Disposing of them is a
second-order question and belongs to M2's (C)/(V) machinery.

---

## 5. M2 transfer coverage — **zero, and structurally so**

Existing M2 assets: 143 (E) empty-stratum certificates, 81 (W) wedge
certificates. Transfer criterion (as specified): every v1 row the certificate
uses — `basis_rows` for (E), `basis_rows` ∪ `supp(ω)` for (W) — must lie in the
unchanged block 0..35 and be maintained under the v2 break set.

> **0 of 224 certificates transfer.** The reason is not clerical:
> **`rank(A₂ over the unchanged rows 0..35) = 32`, not 34.** The two dropped
> dist rows supplied exactly the 2 missing dimensions, so *every* (E)
> certificate's 34-row square subsystem must use row 36 or 37. And every (W)
> certificate's ω lives in v1's 4-dimensional self-stress space, which is not a
> subspace of v2's 8-dimensional one.

**M2 delta queue = the entire 25 050-element union work queue** (stored in
`task4.union_true_survivors`). Nothing is inherited. Caveat: this is a syntactic
transfer test — certificates that fail it may still be *repairable* cheaply by
re-deriving ω on the v2 self-stress space, so 25 050 is an upper bound on the
re-derivation effort, not a proof that each needs fresh work.

---

## 6. Candidate new-contact table — **unchanged, confirmed**

v2 has 14 contact pairs (A22's 13 + `(1,3)`). The non-contact set is
**bit-identical** to v1's 41-pair list, and all 41 `[IV]` gaps agree with M1 to
< 1e-12. So M1's Lipschitz constants and the whole R ∈ {0.005 … 0.1} candidate
table carry over verbatim; the corner-wall side is untouched (no v2 row is a
wall row).

Why `(1,3)` fell through the crack: A22 listed it under `flush_upright_pairs`
(alongside (0,1) and (0,3)) but gave it **no row**, and simultaneously excluded
it from `noncontact_pairs` — so it appeared in neither list that M1 consumed.

---

## 7. New caveat: selection ties at the jam itself

All six new rows sit at a **dominance tie** at z-hat — the alternative corner of
the same owner edge has dominance margin 0 to within 1e-61 and is equally valid.
The two tied corners give **different θ-gradients** (e.g. +1/2 vs −1/2 for the
(0,1) rows). This is theory.md's **G5 biting at the jam**, not only along routes
as M4 §5(b) found. The cone results are unaffected (both selections are in the
possibly-active menu and `cone(conv) = cone`), but any (C) continuation
certificate must carry both selections at its faces. The alternatives are stored
in `meta.basis_v2_definition.tie_alternatives`.

---

## Delta summary

| quantity | v1 | v2 | verdict |
|---|---|---|---|
| rank | 34 | 34 | unchanged |
| self-stress dim | 4 | 8 | grew |
| nonneg self-stress | none | **none** | **alarm clear** |
| λ* floor | 0.047644047 | 0 (all) / **0.047644047** (40 load-bearing) | constant intact, statement needs repair |
| forced-zero rows | — | **{0, 2}** | new |
| K | 6 | **13** | worse |
| cone-alive break sets | 223 | **70 499** | worse |
| survivors after all tests | 81 → 0 (M4 wedge) | **25 050** | **much worse** |
| M2 certificates transferable | — | **0 / 224** | total re-derivation |
| candidate-pair table | — | — | **unchanged** |

**Bottom line.** The repair is sound and necessary, and it costs a lot. The good
news is contained: no nonnegative self-stress, the ascent constant 0.047644
survives verbatim on the load-bearing rows, and the gained-contact analysis is
untouched. The bad news is that the first-order kill-tests no longer close the
complex — 25 050 strata survive, all descended from two first-order-flat
single-square pivot mechanisms that only a second-order argument can kill, and
every existing M2 certificate must be re-derived because the unchanged row block
is rank-32.

## Gaps / caveats

* Everything is at z-hat; no interval extension along strata (M3's job).
* dof > 0 (mechanism) claims remain `[NUM]`; only dof = 0 is `[RFP]`-certified.
* The wedge and cone tests use retained rows only — gained contacts can re-feed
  the cone (§6 bounds which pairs, unchanged from M1).
* `conj` is a reference variant only; its strata are partly geometrically
  meaningless (maintaining a non-dominant branch as an equality). `selx`/`sely`
  are the meaningful ones.
* The two seed mechanisms are expected to die at second order but this is
  **not** demonstrated here.
* The M2 transfer test is syntactic and conservative in one direction only.

## Files

* `attempts/A35-escape-complex/code/strata_lib.py` — v2 basis (opt-in;
  `geo_rows_v2`, `jacobian_v2`, `v2_variant_rows`, `contact_edges_v2`), v1 path
  unchanged and asserted intact.
* `attempts/A35-escape-complex/code/m1b_enum.py` — tasks 0–6 + self-check.
* `attempts/A35-escape-complex/results/m1b_strata.json`
* `attempts/A35-escape-complex/results/m1b_report.md` — this file.

---

## ERRATUM (lead, 2026-08-27, after M3b)

Section 3's minimal excludable list (22 singletons + 11 pairs) is **incomplete**: the search
stopped at size 2. There are also **4 minimal dead TRIPLES** — {4,38,39}, {12,36,37}, {36,37,40},
{38,39,41}, each "both rows of a flush contact + one more row", a shape only possible on a basis
with multi-row contacts. The complete family is **37 sets** (M3b recomputation, independently
spot-verified by the lead: all 4 triples dead with all 2-subsets alive; the 37 predict the LP
verdict on 2000 random break sets with 0 mismatches). The ALIVE counts (70,499, K = 13) are
unaffected — m3b reproduces them level-by-level. `m1b_enum.py` is patched at source
(`minimal_dead_sets_complete`); downstream consumers must use the 37-set family, not the 33.
