# A45 agent B — census code (soundness classes, and what over-accepts where)

Everything here imports `attempts/A43-spine-census/code/h1/` READ-ONLY (`lib0.py`,
`level1_ao.py`, `run_level0_h1.py`) and writes only under `attempts/A45-interface-charge/`.

| file | what | soundness class |
|---|---|---|
| `ruler.py` | Lemma R + Lemma Q as an interval CSP per flush component | **EXACT**, one-sided |
| `mub.py` | the Sec 6.4 crude `m_ub(theta)` guard, 3-deg bins of [0,45] | **EXACT** upper bound |
| `charge.py` | Theorem A45.1 charge lookup + the table-independent ceiling | **EXACT** given the table |
| `census_b.py` | A43-H1 Level-1 fan-out re-run with the A45 columns | measurement |
| `canary_b.py` | Trump canaries C1–C4 | soundness gate (any FAIL = STOP) |
| `audit_ruler.py` | classifies every RULER kill into a named mechanism | audit |
| `spot_h2.py` | the 10 A43-H2 k=3 spine survivors | measurement |
| `regress_b.py` | Level-0 regeneration vs A31 **and** A43 | regression gate |
| `report_b.py` | assembles `results/census_report.json` | — |

## RULER [EXACT]

Kills a decoration only when **every** (normal family, sign) assignment of its flush links is
infeasible. Constraint set = exactly Sec 6.3: per FL link the normal-family projection changes by
exactly ±1 and the other by a slide in [-1,1]; per family `max proj - min proj <= s0(cos+sin) - 1`;
zero-pinned components (component carries a WF contact ⇒ phi = 0) additionally get absolute
containment `proj in [1/2, s-1/2]` with the container side `s` a shared unknown in `[3.80, s0]`,
and WF anchors pinned to `1/2` / `s-1/2`. All exact rationals scaled to integers over 500000;
feasibility by negative-cycle detection; the only rounding is `s0(cos+sin)` rounded UP, which
only weakens the cap.

Two columns, both sound:
* `RULER_kill` — the decoration dies.
* `RULER_refined` — A31's gauge multiplicity `4` per flush edge (which *is* the (family, sign)
  pair) replaced by the number of feasible assignments. Strictly stronger, same soundness.

**Over-accepts (never over-kills):**
1. slides relaxed to their interval hull;
2. no interior-disjointness between squares of one component (Sec 6.3 licenses none, and the
   brief forbids going beyond it);
3. non-zero-pinned components use `cos+sin <= sqrt2`, the widest window an H1 decoration carries;
4. components with `> CAP_M = 12` FL links skip the enumeration: the kill test falls back to the
   **path relaxation** (a sub-system of the full system, so infeasibility still implies
   infeasibility) and the refined count falls back to the unrefined `4^m`. Counted and reported
   as `capped_components` (0 at every k measured).

### Where the kills come from (`results/ruler_kill_audit.json`, k = 3..5)

411 killed component signatures, **411 of them zero-pinned**, classified with nothing left over:

* **M1 Lemma-Q path bound** (392) — opposite-wall WF anchors at FL-graph distance ≤ 2. That
  projection must equal `s - 1` in `[2.80, 2.877084]`, and a path of `m` links moves it by ≤ `m`.
* **M2 odd-cycle parity** (16) — a same-wall pin set equalises one family across the component,
  forcing every link into the *other* family; an odd cycle of ±1 steps cannot close.
* **M3 Lemma Q verbatim** (3) — same forcing, plus an opposite anchor pair in the forced family:
  the difference is then an **integer**, and `[2.80, 2.877084]` contains none.

Lemma R's pure *length* cap contributes **zero** kills: a decoration fixes neither the normal
family nor the sign, so a ruler is never forced to be long.

## CHARGE [EXACT given the table]

`results/charge_table.json` if it exists, else the **STUB** in `charge.py` (labelled everywhere).
The final run used agent A's **CERTIFIED** table (rho_min = 1/16, R = 1/32, 25 kept / 50 dropped
bins, largest entry `41/65536 = 6.256e-04`); an earlier stub run of the whole pipeline gave the
same verdicts, which is the point — the outcome does not depend on the table.
Census-side semantics is min-over-reachable-bins (Sec 4 remark 1), and three separate rules push
that min to 0:

* a non-flush square-square contact of a *decoration* is not resolved into CE vs CC, and **CC is
  uncharged by design** (lead addendum) — so it contributes 0;
* a square with wall-degree 2 may realize the corner-at-container-corner case (**WCC**, one
  uncharged interface, lead addendum) — so all its wall contacts contribute 0;
* a class tilt window spanning any dropped or uncovered bin contributes 0.

`CHARGE_ceforced` prices every non-flush square-square contact as CE anyway. **That column is a
magnitude probe, NOT a sound kill**, and is never composed.

The verdict does not depend on the table: `charge(K) <= area B(p, rho_min/2) = rho_min^2 <= 1/16`
and `E <= 3k+2`, so the maximum possible sum at k=11 is `35/16 = 2.1875 < B0 = 4.031780343056`.

## ZERO-CHARGE / Theorem A45.2 [EXACT for branch (b)]

A zero-charge decoration is all-FL / all-WF. In MAIN, L3 forbids wall-less components, so every
component is zero-pinned and **all k loaded squares sit at class 0**; A26 caps that at 9. Hence
`k >= 10` zero-charge cores are dead — universally, no k=11 join needed. Branch (e) is empty in
this census (L3 already removes floating components); branch (f), the rattler caveat, is the
entire residue at `k <= 9`.

## m_ub(theta) [EXACT upper bound]

Centres of same-tilt squares are pairwise `>= 1` apart in the theta-rotated sup-norm and lie in a
theta-rotated square of side `A = s0 - (cos+sin)`. Columns of width `< 1` each hold at most
`1 + floor(Y)` centres (`Y` = the column's y-extent in the region). Per 3-deg bin, evaluated with
exact-rational tan-half enclosures (floats widened 1e-9 outward, the A43-G4 convention),
sub-binned 12x and maximised, and minimised over several column partitions. `B = w(s0-w)` is
evaluated as a **monotone function of `w = cos+sin`** — using independent intervals for `a` and
`b` inflates it enough to lose the mandated `[0,3) -> 9` sanity value.

**Deviation from the brief:** the eroded region is a rotated **square**, not an octagon (the
Minkowski erosion of a square by a square is a square). The count is done on the exact region.

## Level-0 inertness (why there is no `+RULER` orbit column)

A Level-0 orbit dies only if *every* decoration dies. The all-corner decoration always exists (a
strict tilt digraph on k singleton classes; every graph has an acyclic orientation), has no flush
component, and carries charge 0. So neither filter can move the cumulative orbit counts at any k.
This is a proof, not a measurement; the sample check in `census_b.py` confirms it numerically.
