# A115 — method, discipline, and the two pieces of new bookkeeping

## Discipline

* **READ-ONLY** on `attempts/A38-root-power/`, `attempts/A85-k0-route/`, `attempts/A92-blocked-side/`,
  `attempts/A99-k0-tree-v2/`, `attempts/A107-shadow-gallery/`, `attempts/A113-k0-manifold-distance/`
  and on every running campaign (A61, A96, A112, A114): every node json used here was **copied**
  into `attempts/A115-k0-corner-rows/results/nodes/<nid>.src.json` before anything touched it, and
  the whole A92 engine was **copied** into `attempts/A115-k0-corner-rows/code/` (so even
  `__pycache__` lands here). No campaign process was started, stopped or re-niced.
* `verify_case.py` byte-identical to the frozen one:
  `sha256 = 521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`
  (the same file as A53/A57/A85/A89/A92/A94/A109).
* At most **2** A115 python processes, BLAS pinned to 1 thread (`blas1` imported before numpy in
  every entry point); every LP and every certification is preceded by two consecutive readings of
  free COMMIT > 6144 MB **and** free physical > 3072 MB (`a115lib.gate`).
* Resumable: one record file per `(cell, δ, e)` in `results/rec/<tag>.json` and one LP result in
  `results/nodes/<tag>.lp.json`; a re-run skips anything already recorded.
* Writes confined to `attempts/A115-k0-corner-rows/**`, the registry row, `LOG.md` and one note
  line on the depgraph node `K0.CW`.

## What is added to the A92 engine

Nothing. `crowdfam92` (the exact outer cover `G` of `∪_c F_c(a_w(δ))`, the exactly-certified
complement cover `E`, the `RHS_MULT` row hook), `caselp92.solve_node`, `lpbox92` and
`verify_case.py` are used **verbatim**. A115 adds only

* `a115lib.py` — corner-frame `μ_c` (via `corner85.f_min_max`), the per-corner incidence counter
  `GCount` (crowdfam92's `GTest` split per corner instead of OR-ed), `core_plus` / `box_rmax`
  (A109's, verbatim) and the node incidence budget;
* `t1.py`, `plan115.py`, `t2.py`, `certify115.py`, `canary115.py`, `t3.py`, `report115.py`.

`certify115.make_certificate115` is `caselp92.make_certificate92` with the **node's own cores**
written into both files (and hence `budget = n − #cores`, which `verify_case.py` requires) — the
same one-line difference A109's `certify109` made to A94's root certifier.

## The three configurations, and what each is licensed to say

`a_w(δ) = λ_max (1 − δ) + (λ_max − 1)/√2` (`crowdfam92.a_w`, exact, rounded up to 10⁻⁵), with
`λ_max = s0/3.82 = 969271/955000`. This is Lemma B-YES (`k0_blocked_side.md` §2.3): a square of a
packing at side `m ∈ [3.82, s0)` with `μ_c ≤ 1 − δ` dilates to a square of `F = Δ_λ P` at `s0`
with `μ_c ≤ a_w(δ)`. So a certificate built at `a_w(δ)` speaks about the **whole window**.

| cfg | δ | a_w | what the crowd hypothesis is | licensed by |
|---|---|---|---|---|
| `d0` | 0 | 1.025520 | two squares of `F` meet the **widened** corner box `[0, 1+w]²`, `w = 0.025509` | Lemma K0-FREE′ + Lemma K0-WIDEN (`k0_route.md` §3, §4.1) — the hypothesis the k0 tree already carries at every node, for **every** side of the window |
| `d0.05` | 0.05 | 0.974770 | every corner's second intruder has depth ≥ 0.05 | Lemma CW + Theorem S(δ) — only the sub-window `m ≤ ŝ − δ` |
| `d0.1` | 0.1 | 0.924020 | … depth ≥ 0.1 | idem |

**`d0` is the only configuration that is licensed everywhere at s0**, and it is exactly the
"met by ≥ 2 squares" statement that makes the k0 tree exist at all. The δ > 0 ladder is a
mechanism measurement, as in A109: Theorem CEIL caps δ at 1 − 1/√2 = 0.292893 anyway.

**Consequence of `a_w(0) > 1` (measured, `results/trump_family_counts.json`).** All eight D4
images of Trump realise the `d0` crowd hypothesis — per-image corner counts
`g0[3,2,2,2] … g7[2,2,2,3]` — because Trump's tangent squares sit at `μ_c = 1` exactly, inside the
widened box. At `δ = 0.05` and `δ = 0.1` no image realises it (each has a corner with a single
meeter: `g0[1,1,2,1]`). Hence:

* the **root** LP can never pass at `δ = 0` (a genuine packing satisfies the hypothesis), so
  `d0` rows can only ever kill nodes whose hypothesis excludes every Trump image — the node level
  is the only level at which the question is even askable;
* the **canary** binds at `δ = 0`: the three Trump-image cells (A38 l1 idx 21/152/153) must
  survive there.

## The node-level incidence budget (new, and exact — unlike A109's)

Lemma CW at the **root** reads: 8 crowd squares, budget `11 + 8e`. At a **node** the hypothesis
has `k` conditioned free-square cores; the LP exempts their poses from its rows (they are charged
to the cores) and only pays for `budget₀ = 11 − k` squares. A conditioned square is one of the
eleven and may itself be one of the eight crowd squares, so

    budget = budget₀ + floor(e · B),      B = 8 − Σ_{cores} r_max(B⁺),
    n (in the certificate) = 11 + e·B,    budget = n − #cores.

`B⁺` is the set of poses of a *unit square containing* the core `K(B)` (`a115lib.core_plus`,
A109's bound verbatim) and `r_max(B⁺)` is the max of the **dilated** corner G-test over a
≤ 0.01 / 0.5° grid of `B⁺` with the sample half-cell added to the zone tolerance, so it can only
over-count — the sound direction.

**Why the budget is exact here and was not in A109.** The four widened corner boxes are
`s0 − 2 a_w = 1.826 > √2` apart, so a unit square meets **at most one** of them (CC-1(ii) with the
widening, `k0_route.md` §4.2). Therefore `r_G(Q) ∈ {0, 1}` for every pose, `r_max ∈ {0,1}`, and
`B ∈ {7, 8}`: the multiplicity that killed A109's slot rows (one placement meeting two or three
slot boxes at once, so the LP's fractional packing buys `c = 6.2` incidences against a guaranteed
`B = 4.4`) **cannot happen**. Whatever A115 measures, it is not that failure mode.

## The e ladder and the one-LP rule

`η(e) = τ(e) − budget(e) = η₀ + c(e)·e − floor(eB)` with `c(e) = (τ(e) − τ₀)/e` the corner
incidence count the LP's own fractional packing realises. `τ(e)` is the optimum of an LP whose
right-hand side is affine in `e`, hence convex and increasing in `e`, so `c(e)` is
non-decreasing. Therefore a kill at `e` needs `c(e) < B`, and if the smallest `e` that buys any
bonus (`e = 1/B`, `floor(eB) = 1`, `e·B = 1` exactly integral as the certificate needs) already
returns `c ≥ B`, no larger `e` can kill — one LP settles the cell. `t2.py --e auto` runs `e = 1/B`
and adds `e = 1` only when `c < B`.

## Protocol (PI, 2026-09-06)

* **stage 1** — LP at 240 s, with a 60 s probe. `τ` from a partially-generated row set is a LOWER
  bound that only rises as rows are added, so `τ ≥ budget` at the probe is a sound refusal and the
  run stops there (A94/A92's own rule; it can in principle discard a would-be kill, which is the
  conservative direction). Then `η = τ − budget`:
  `η ≤ −10⁻³` → **kill candidate**, goes straight to the two-run frozen certification, converged
  or not — the certificate is the verdict, never the LP value; `|η| < 10⁻⁶` → knife edge → stage 2;
  otherwise alive.
* **stage 2** — the knife-edge cells only, warm-continued to a 900 s cap.

## Known looseness (all conservative)

* the row oracle's dilated `G` (`EPS_ZONE_G = 0.02`, `EPS_TH_G = 1°`) charges the `1 + e` right-hand
  side to more poses than `F_c(a_w)` contains — more rows at the higher rhs, never fewer;
* `r_max(B⁺)` over-counts what a conditioned square can carry, so `B` is a lower bound on the
  incidences the LP must pay for;
* the probe refusal above;
* `τ₀` (and hence `c`) is read from the campaign's own LP result, which is itself unconverged for
  81 of the 84 K01 cells, so `c` is a diagnostic, not a certified quantity.
