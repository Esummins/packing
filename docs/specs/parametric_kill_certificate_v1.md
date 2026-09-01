# parametric-kill-certificate-v1 — frozen spec (A62, checklist C2)

**Verifier:** `attempts/A56-sparametric/code/verify_param.py` (793 lines, sha256 `0c58485c…`).
It **imports the audited A53 `verify_case.py` integer core unmodified** (`imul4`, `trig_int`,
`box_trig`, `vacuous_int`, `clip_int`, the Fraction reference predicates); the only new exact
predicates replace a point by an outward interval, so enclosures can only grow.
**Soundness argument:** `attempts/A56-sparametric/notes/soundness.md` P0–P7 (prose).
**Status:** written from behaviour + code at commit `c9980bf` (2026-09-01) by A62. The format
string `"parametric-kill-certificate-v1"` is **mandatory** and checked by the loader.

## 1. The mathematical claim a PASS establishes

The certificate declares an s-window [s_lo, s_hi] (run inputs `--slo`, `--shi`; the lab
window is [191/50, 969271/250000]) and s-**affine** data: atoms
pᵢ(s) = (axᵢ + bxᵢ·s, ayᵢ + byᵢ·s) with s-free weights wᵢ ≥ 0, and cores K_j(s) centred at
(akx_j + bkx_j·s, aky_j + bky_j·s) with s-free half-side a_j and tilt tm_j. NO-families are
**rejected** by the loader (unsupported in v1). A PASS on the root
[0,1] × [½, s_hi − ½]² × [s_lo, s_hi] establishes:

> **(P1)** Σᵢ wᵢ < budget (s-free), and
> **(P2)** for **every** s ∈ [s_lo, s_hi] and every closed unit square Q ⊆ [0,s]² that meets
> no core K_j(s): μ_s(Q) ≥ 1 + margin.

By the fixed-s bridge of `case-lp-certificate-v1` §1 (A13/A53-L5), this is the kill of the
pin-hypothesis stratum **at every side s in the window simultaneously** — the object
checklist item H6 demands per stratum. The S4/boundary-discipline caveat of the fixed-s spec
applies verbatim (disjoint-closed vs interior-disjoint; findings F9); the window form is what
makes the λ-scaling bridge available, since nearby sides are inside the certified window.

**Anchoring.** The s-affine form expresses each pin's anchor: a wall-anchored pin has
b-coefficients ±1 or 0 (it rides the wall of [0,s]²), a fixed pin has b = 0. The `anchoring`
field documents the choice; anchoring affects **completeness only** (which strata can be
expressed), never soundness — the claim quantifies over the declared affine family, whatever
it is (soundness.md P4; the "gap-anchoring lesson").

## 2. Certificate fields (JSON; exact rational strings as in the fixed-s spec)

| field | type | meaning |
|---|---|---|
| `format` | `"parametric-kill-certificate-v1"` | mandatory, checked |
| `name` | string (opt) | human label, echoed in reports |
| `n` | int (opt, default 11) | family size |
| `budget` | int | b; PASS requires Σ w < b |
| `atoms` | `[{"ax","bx","ay","by","w"},…]` | s-affine atoms, rational strings |
| `total` | rational string | must equal Σ w (warning on mismatch; computed value governs) |
| `hypotheses.cores` | `[{"akx","bkx","aky","bky","tm","a"},…]` | s-affine cores |
| `hypotheses.nofams` | must be absent/empty | loader raises otherwise |
| `anchoring` | string (opt) | documentation of the affine anchor convention |

## 3. Decision procedure (normative)

4-D branch-and-bound over B = [t0,t1] × [x0,x1] × [y0,y1] × [a,b] (a,b are s-endpoints).
Discharge rules, each evaluated with the container at the **most permissive** end s = b:

* **(V) vacuous** — `vacuous_int` with wall at s = b (largest container of the cell);
* **(CL) clip** — `clip_int` with wall at s = b: centre bounds floor(w_min/2), ceil(b − w_min/2),
  outward-rounded; the clipped box still contains every admissible placement for every s ∈ [a,b];
* **(E) exempt** — `core_exempt_frac_iv`: the fixed-s core-overlap test with core centre
  widened to the interval [α + β·a, α + β·b] per coordinate — exempt only if Q meets the core
  for **all** (t, c, s) in B;
* **(C) covered** — Σ of wᵢ over atoms whose **whole s-interval position box**
  [axᵢ+bxᵢ·a, axᵢ+bxᵢ·b] × (same in y) lies inside Q for every (t,c) ∈ B, compared with
  ceil((1+margin)·WD) in integers.

Else split the widest of t (×`--tscale`, default 2), x, y, s (×`--sscale`, default 8);
undischarged boxes at `--depth` (default 48) are FAIL witnesses **recording their s-range**
(so a FAIL localises which part of the window is unproven).

**Integer grid:** one grid for x, y and s: D = 250000·2^(depth+2) (250000 = den(s0);
den(191/50) = 50 divides it), so every s-bisection point is exact; t on 2^K, K = depth+1,
exactly as the fixed-s verifier. Witness sampling uses floats; every accept decision is
integer/Fraction.

**Cross-check convention (not part of the format, but the lab's discipline):** every PASS is
accompanied by fixed-s runs of the **unmodified** A53 `verify_case.py` on the specialisations
at s_lo, midpoint, s0 (canary C2 in `sweep.py`) — a cheap independent consistency test that
the affine data specialises to passing fixed-s certificates.

**Exit codes:** 0 = PASS, 1 = FAIL, 2 = malformed.

## 4. Settings that MUST appear in a PASS report (C7)

`--report` writes JSON including: `slo`, `shi`, `depth`, `sscale`, `tscale`, `split`,
`strict-margin`, `anchoring`, and stats `boxes / covered / vacuous / exempt / split /
s_splits / s_cells / max_depth / max_s_depth`. The claimed window is [slo, shi] **as run**,
not as intended; a report without `slo`/`shi` is not citable (the `eps_geo`-style silent
default reversion of A56's own bug history is exactly what this rule prevents).

## 5. Float / numpy audit (C5-lite, A62)

Raw hits in `attempts/A62-trust-ledger/results/tcb_raw.md`. Classification: float atom-
position arrays (lines 222–227, 270) and `core_exempt_float_iv` feed the shortlist only;
witness construction (396–434) is FAIL-path reporting; line 271 `fneed − 1e-9` is the
conservative shortlist target. No accept decision reads a float.

## 6. Known limitations

* NO-families unsupported (v1): strata whose fixed-s kill uses NO-families cannot yet be
  window-transferred by this format.
* s-affine data only: pins whose window motion is not affine in s cannot be expressed
  (completeness limit; A56 found none needed among the 52 strata).
* One implementation (C3 open); the fixed-s specialisation cross-check mitigates but does
  not replace a second implementation.
