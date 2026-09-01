# case-lp-certificate-v1 — frozen spec (A62, checklist C2)

**Verifier:** `verify_case.py` (canonical copy: `attempts/A53-simple-strata/code/verify_case.py`,
957 lines, sha256 `521cb01f…`; sixteen byte-identical copies exist across attempts A13–A60).
**Lineage:** the A13 extension of `certs/verify_measure.py` (format `measure-certificate-v1`,
frozen in `certs/README.md`); a plain measure certificate is the special case with no
hypotheses and `budget = n`.
**Status of this spec:** written from behaviour + code at commit `c9980bf` (2026-09-01) by A62;
freezes what the deployed verifier actually checks. Existing certificates carry **no** `format`
field; this spec identifies the format by content. (Recommended for new certificates:
`"format": "case-lp-certificate-v1"`; the verifier ignores unknown fields.)

## 1. The mathematical claim a PASS establishes

Let the certificate declare a side `s`, a count `n` (default 11), an atomic measure
μ = Σᵢ wᵢ δ_{pᵢ} (wᵢ ≥ 0), core squares K₁…K_r (closed squares of half-side `a_j ≥ 0`, centre
`(kx_j, ky_j)`, orientation θ_j with tan(θ_j/2) = `tm_j`), NO-families F₁…F_m (each a centre
rectangle `[x0,x1]×[y0,y1]` with a list of closed t-intervals), and a `budget` b (by convention
b = n − r). A PASS at strict-margin μ₀ (default 0) establishes, as one theorem:

> **(P1)** Σᵢ wᵢ < b, and
> **(P2)** every closed unit square Q ⊆ [0,s]² (any orientation) that
>   (i) does **not** meet any core K_j (closed intersection), and
>   (ii) is not NO-exempt — i.e. its (centre, t) does not lie in any F_k —
> satisfies μ(Q) ≥ 1 + μ₀.

**Bridge (one paragraph of mathematics outside the program, stated in the verifier header):**
if n **pairwise-disjoint** closed unit squares lie in [0,s]² such that for every K_j some
square of the family contains K_j, and no square is NO-exempt, then the ≥ b = n − r squares
that own no core are pairwise disjoint and non-exempt, so μ(total) ≥ b, contradicting (P1).
Hence **no such family exists** — the pin-hypothesis stratum is empty at side s.

**Boundary discipline (S4) — what a PASS does NOT establish by itself.** The bridge needs
*pairwise disjoint closed* squares. A packing in the lab's sense (pairwise disjoint
**interiors**, contacts allowed — every minimiser has contacts) is not literally covered:
touching squares may share an atom. Every downstream use on a minimiser at its own side
routes through a λ-scaling-with-pin-slack argument (scale to a nearby rational side, where
the scaled packing is strictly disjoint and small/point cores are still contained). That
argument is applied implicitly at every kill and **is written nowhere** — A62 findings F9;
it must become a lemma before any kill is cited in the paper.

Two structural soundness notes a referee should verify by reading §3:
* every discharge rule errs conservative: interval arithmetic **over**-approximates u, v, so
  "atom inside Q for the whole box" is under-approximated (mass under-counted); exemption is
  granted only when it holds for **all** parameters of a box;
* a missing float-shortlist hit can only lose mass / fail to exempt — floats can cause
  spurious FAIL, never spurious PASS (see §5).

## 2. Certificate fields (JSON)

All numbers are **exact rational strings** (`"19/5"`, `"3.877084"` — decimal strings are read
exactly as the rational they denote; JSON floats are rejected).

| field | type | meaning |
|---|---|---|
| `s` | rational string | container side; claim is about [0,s]² |
| `n` | int (opt, default 11) | number of squares in the hypothetical family |
| `atoms` | `[["x","y"],…]` or `[{"x","y","w"},…]` | atom positions (D4 images expanded unless `symmetry`) |
| `weights` | `["w",…]` | same length as `atoms`, all ≥ 0 (omit when weights inline) |
| `total` | rational string (opt) | must equal Σ weights; mismatch is a warning, computed value governs |
| `symmetry` | `"D4"` (opt) | expand every atom to its distinct D4-orbit images under the symmetries of [0,s]², each with the listed weight |
| `budget` | int | b; the PASS requires Σ w < b |
| `hypotheses.cores` | `[{"kx","ky","tm","a"},…]` | core squares; `a = 0` (point core) is legal and used by A53-lineage pin certificates |
| `hypotheses.nofams` | `[{"x0","x1","y0","y1","t_intervals":[[t0,t1],…]},…]` | NO-family zones (centre box × closed t-intervals) |
| `provenance` | any (opt) | ignored by the verifier |

Conventions: t = tan(θ/2) ∈ [0,1] parametrises orientation (θ ∈ [0°, 90°];
cos θ = (1−t²)/(1+t²), sin θ = 2t/(1+t²) — exact rationals for rational t).

## 3. Decision procedure (normative — a clean-room implementation must reproduce PASS/FAIL)

Branch-and-bound over boxes B = [t0,t1]×[x0,x1]×[y0,y1], root [0,1]×[½, s−½]², first split
into 4^k boxes in (cx,cy) (`--split k`, default 3). A box is **discharged** iff one of:

1. **VACUOUS** — no admissible placement in B: centre ranges clipped to
   [w_lo/2, s − w_lo/2] with w_lo = min(w(t0), w(t1)) ≤ w(t) = cos θ + sin θ on [t0,t1]
   (w unimodal in t), rounded **outward** to the integer grid; empty clip ⇒ vacuous,
   otherwise the clipped box (which still contains every admissible placement of B) replaces B.
2. **EXEMPT-core** — for every (t,c) ∈ B, Q(c,θ) meets some single core K_j: proven by
   overlap of projections on all four edge-normal axes (two of K_j, two of Q) with interval
   enclosures; sufficient conditions `|proj centre offset| ≤ a + g/2` on K-axes and
   `≤ ½ + a·g` on Q-axes, where g lower-bounds |cos(θ−θ_j)| + |sin(θ−θ_j)| on the t-interval.
   (SAT for convex polygons: non-separation on all edge normals ⇒ intersection.)
3. **EXEMPT-nofam** — B's centre box inside F_k's rectangle **and** [t0,t1] inside one of its
   t-intervals (all closed, exact comparisons).
4. **COVERED** — Σ { wᵢ : pᵢ ∈ Q(c,θ) for **every** (t,c) ∈ B } ≥ 1 + μ₀, atom membership by
   exact integer interval arithmetic on u = C·(p−c) + S·(p−c)⊥ coordinates (|u|,|v| ≤ ½).

Else bisect along the widest dimension (t-width weighted by `--tscale`, default 2); children
inherit the parent's certified atom mass and drop atoms provably outside. A box undischarged
after `--depth` bisections (default 48) is a FAIL **witness**.

**Integer scheme** (shared with the Lean `checkMeasureI` port of the plain-measure case):
lengths ×D = den(s)·2^(depth+2); t ×2^K, K = depth+1; atoms over their own denominator PD;
weights over common denominator WD with NEED = ceil((1+μ₀)·WD); all comparisons
cross-multiplied integers, no gcds. A `fractions.Fraction` reference implementation of every
predicate is kept in-file; `--selftest` cross-checks them on random inputs.

**Exit codes:** 0 = PASS, 1 = FAIL (witnesses written), 2 = malformed / Σw ≥ budget
(certificate proves nothing).

## 4. Verifier settings that MUST appear in a PASS report (C7)

`--report` writes `<cert>.report.json`. A citable PASS must record (and the report does
record): `depth`, `strict-margin`, `tscale`, `split`, `scale-weights` (≠1 must be stated —
it multiplies every weight and re-derives the total; the claim is then about the scaled
measure), `jobs`, and the run statistics `boxes / covered / vacuous / exempt(core,nofam) /
split / exact_atom_checks / max_depth`. A PASS at settings weaker than the ones cited in a
composition (e.g. lower depth) is not that PASS. The lab's re-verification convention for
composed results is a cold single-invocation run at `--depth 60`.

## 5. Float / numpy audit (C5-lite, A62)

All hits classified (raw grep: `attempts/A62-trust-ledger/results/tcb_raw.md`):
* **shortlist only** (lines 263, 318–341, 392–457, 473 first conjunct, 514–515): numpy mask
  `f_mass_mask` picks candidate atoms; each candidate is then decided exactly; a missed
  candidate loses mass ⇒ conservative. `core_exempt_float` pre-filters the exact
  `core_exempt_frac`; line 473 requires float **and** exact — exemption never granted on
  float evidence alone.
* **witness reporting only** (546–575, 616–631, 947): float renderings, hole/tight/undecided
  classification of FAIL witnesses — never on the PASS path.
* **`self.fneed = float(need) − 1e-9`** (line 395): float lower target for the shortlist;
  conservative direction.
No float value reaches an accept decision. Decision path: Python ints + `fractions.Fraction`.

## 6. Known limitations (inherent, by design)

* Tangency: an admissible placement needing an atom **exactly on ∂Q** for mass 1 can never be
  certified (box methods); certificates must be robust (positive-margin placements only).
* PASS is at the single declared `s` only. Window validity is a separate obligation —
  see `docs/specs/parametric_kill_certificate_v1.md`.
* One implementation. The C3 second implementation must be written from **this document**;
  the Lean `checkMeasureI` covers only the hypothesis-free special case.
