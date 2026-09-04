# A92 crowd92 — the CROWD-WEIGHTED root certificate (Opus compute chore)

Implements `attempts/A92-blocked-side/notes/chore_crowd_cert.md`. Everything is written under
`attempts/A92-blocked-side/`; nothing under A57/A60/A61/A85/A86/A89 was written, and the frozen
`verify_case.py` was copied byte-identical (sha256 in section 9) and never edited.

Generated 2026-09-04 04:12:18 (status=done, 290 min); 10 LP records, 3 certification records.

## HEADLINE — largest delta with a CERTIFIED two-run PASS

**delta = 0.30 at e = 1 (n = 19)** — `certs/runA_S_d0.3_e1_v2.json` + `certs/runB_S_d0.3_e1_v2.json`, both PASS under the frozen verifier at depth 56

---

## 0. Constants

| quantity | value |
|---|---|
| s0 | 969271/250000 = 3.877084 |
| window floor | 3.82 |
| lambda_max = s0/3.82 | 969271/955000 = 1.0149434554 |
| a_w(delta) | lambda_max (1-delta) + (lambda_max - 1) * 7072/10000, rounded UP to 1e-5 |
| budget n | 11 + 8e; e in {1/4, 1/2, 1, 2} -> n = 13, 15, 19, 27 |

| delta | a_w (exact) | a_w (float) | spec's printed value |
|---|---|---|---|
| 0.30 | 72103/100000 | 0.721030 | 0.72103 |
| 0.20 | 82253/100000 | 0.822530 | 0.82252 (spec truncates; see Deviations) |
| 0.10 | 46201/50000 | 0.924020 | 0.92402 |
| 0.05 | 97477/100000 | 0.974770 | 0.97477 |

## 1. The certificate (Lemma CW), as implemented

ONE measure mu on [0,s0]^2, TWO runs of the frozen verifier:

* **run A** `certs/runA_<tag>.json` — n = budget = 11 + 8e, atoms + weights w, hypotheses
  {cores: [], nofams: []}. PASS certifies mu(Q) >= 1 for EVERY admissible closed unit square
  Q in [0,s0]^2, and mu(total) < 11 + 8e.
* **run B** `certs/runB_<tag>.json` — the SAME atoms, weights w/(1+e) (exact rationals),
  n = budget = 1000 (its "total < 1000" clause is a dummy), hypotheses {cores: [], nofams: E}.
  PASS certifies mu(Q) >= 1+e for every Q not provably in E; every E box is exactly certified
  disjoint from F_c(a_w) for all four corners c, so this covers every admissible Q that meets the
  closed box [0,a_w]^2 at some corner.

Composed (Lemma CW): a packing with 2 such squares at each corner (8 distinct, CC-1(ii)) plus 3
others has sum_i mu(Q_i) >= 8(1+e) + 3 = 11 + 8e > mu(total) — contradiction.

The hypothesis is carried entirely by the LP right-hand sides: rhs(Q) = 1 + e*[Q in G], G an
outer cover of F_c(a_w) at every corner. The node itself has NO cores and NO NO-families.

## 2. Families (`code/crowdfam92.py`, `results/fam_d<delta>.json`, `results/crowd92_fams.json`)

Method, all exact in Fractions. `f(u,v,t) = corner85.f_min_max` is nondecreasing in u and in v and
(sqrt2/2)-Lipschitz in theta, so a cell `[x_i,x_{i+1}] x [y_j,y_{j+1}] x [T0,T1]` is PROVABLY
DISJOINT from `F(a) = {f <= a}` iff `min over a 193-point exact t-grid of f(x_i,y_j,t) - pad > a`
with `pad = (sqrt2/2)*dtheta/2`. Centre grid 0.02 on `[0.45, a_w+3/4]^2` (a pose meeting
`[0,a_w]^2` has corner-frame centre coords <= `a_w + sqrt2/2 < a_w + 3/4`); every test is inflated
by 1e-8 so the 1e-9 outward rounding of `caselp.q` on the emitted NoFam corners cannot break it.
G = every cell NOT provably disjoint (a DOWN-set = staircase per theta bin, run-length merged
LOSSLESSLY, so the merge adds no overshoot). Theta bins are o3fam's seven, edges at multiples of
1/4 deg, sigma-closed and overlapping by 1 deg (so no verifier box straddles a bin forever).
E = the exact complement of G in `[0.45, s0-0.45]^2 x [0,90]`, decomposed into horizontal strips
(lower band, upper band, one middle rect per bin), each EXACTLY certified disjoint from
`F_c(a_w)` at all four corners.

| delta | a_w | a_w float | grid | G boxes / corner | E boxes | overshoot of G over F | in F but not G | D4 defect | build s |
|---|---|---|---|---|---|---|---|---|---|
| 0.30 | 72103/100000 | 0.721030 | 52x52 | 145 | 413 | **11.16 %** | 0 / 6000 | 2.2e-16 | 35.8 |
| 0.20 | 82253/100000 | 0.822530 | 57x57 | 145 | 413 | **9.67 %** | 0 / 6000 | 2.2e-16 | 39.2 |
| 0.10 | 46201/50000 | 0.924020 | 62x62 | 151 | 425 | **8.69 %** | 0 / 20000 | 2.2e-16 | - |
| 0.05 | 97477/100000 | 0.974770 | 64x64 | 148 | 419 | **7.62 %** | 0 / 20000 | 2.2e-16 | - |

## 3. Canary (checked FIRST, before any LP)

Per-image, per-corner count of Trump placements with `f_c <= a_w` (exact). An image REALISES the
crowd hypothesis iff every corner has >= 2. Counts printed as `[BL BR TL TR]`.

| a_w | g0 | g1 | g2 | g3 | g4 | g5 | g6 | g7 | realising |
|---|---|---|---|---|---|---|---|---|---|
| 0.721030 (d 0.30) | 1101 | 1110 | 0111 | 1011 | 1011 | 1110 | 0111 | 1101 | **NONE** |
| 0.822530 (d 0.20) | 1101 | 1110 | 0111 | 1011 | 1011 | 1110 | 0111 | 1101 | **NONE** |
| 0.924020 (d 0.10) | 1121 | 1112 | 2111 | 1211 | 1211 | 1112 | 2111 | 1121 | **NONE** |
| 0.974770 (d 0.05) | 1121 | 1112 | 2111 | 1211 | 1211 | 1112 | 2111 | 1121 | **NONE** |

Reading: three corners of every image hold exactly ONE slot square (f = 0 exactly, the square with
a vertex at the container corner); the fourth is Trump's TL 2-crowd (f = 0.831679 / 0.844500), so
it contributes 0 below a_w = 0.72/0.82 and 2 above a_w = 0.92. No image ever reaches 2 at all four
corners, so no image realises the hypothesis at any a_w < 1 — **CANARY PASS**, exactly as the spec
predicted. The engine also re-checks after every PASS and exits 9 on a realisable node.

**Out of scope, logged and not checked:** the certified K0-BLOCKED packings of d2front87 at
4.03-4.36 and s0115 at 3.985 have side > s0 and are not touched by this certificate.

## 4. Phase 1 — (S), the D2^4 pattern: the LP table

Node = the k0_00 ROOT at s0, no pins, no cores, no NO-families, D4 quotient, warm pool = A38's
root_s0 + A07's 3.82/3.83 columns rescaled (<= 1600 columns), lp_time 900 s, LP-ONLY.
PASS criterion: tau < n = 11 + 8e; eta = tau - n.

| delta | e | n | a_w | tau | eta | minmass | maxcov | rows | LP s | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.30 | 1 | 19 | 0.721030 | 16.445919 | -2.554081 | 0.8426 | 1.1009 | 10725 | 968 | LP-PASS (tau < n; certificate not attempted yet) |
| 0.20 | 1 | 19 | 0.822530 | 18.104218 | -0.895782 | 0.9005 | 1.0315 | 13232 | 983 | LP-PASS (tau < n; certificate not attempted yet) |
| 0.10 | 1 | 19 | 0.924020 | 21.046610 | 2.046610 | 0.9532 | 1.0221 | 20869 | 980 | refused (tau 21.046610 >= n = 19) |
| 0.10 | 1/2 | 15 | 0.924020 | 16.056524 | 1.056524 | 0.9564 | 1.0158 | 22569 | 950 | refused (tau 16.056524 >= n = 15) |
| 0.10 | 2 | 27 | 0.924020 | 31.056696 | 4.056696 | 0.9146 | 1.0244 | 23418 | 929 | refused (tau 31.056696 >= n = 27) |
| 0.10 | 1/4 | 13 | 0.924020 | 13.585106 | 0.585106 | 0.9360 | 1.1424 | 26726 | 973 | refused (tau 13.585106 >= n = 13) |
| 0.05 | 1 | 19 | 0.974770 | 22.000000 | 3.000000 | 1.0000 | 1.0010 | 21550 | 581 | refused (tau 22.000000 >= n = 19) |
| 0.05 | 1/2 | 15 | 0.974770 | 16.500000 | 1.500000 | 1.0000 | 1.0000 | 21626 | 813 | refused (tau 16.500000 >= n = 15) |
| 0.05 | 2 | 27 | 0.974770 | 33.000000 | 6.000000 | 0.9903 | 1.0000 | 23878 | 993 | refused (tau 33.000000 >= n = 27) |
| 0.05 | 1/4 | 13 | 0.974770 | 13.750000 | 0.750000 | 0.9813 | 1.0000 | 27512 | 979 | refused (tau 13.750000 >= n = 13) |

## 5. Phase 1 — certification (two frozen-verifier runs per node)

`certify92.py`, depth 56, jobs 1, 2 witness-feedback rounds (witnesses of BOTH runs fed back into
the same crowd-weighted re-solve), auto scale capped at 1.4, A85 eps_geo 0.002 / 0.004 repair on a
FAIL. `<tag>.PASS` is written only if BOTH runs pass.

| tag | delta | e | n | verdict | run A | run B | cert s | sha256 A (16) | sha256 B (16) |
|---|---|---|---|---|---|---|---|---|---|
| S_d0.3_e1 | 0.30 | 1 | 19 | **FAIL(eps_geo 0.004)** | PASS | FAIL | 2678 | `9e240dadbfa24783` | `e1143f244e1356c9` |
| S_d0.2_e1 | 0.20 | 1 | 19 | **FAIL(eps_geo 0.004)** | FAIL | FAIL | 3409 | `c804d414e1abca54` | `340839c90c0ca09b` |
| S_d0.3_e1_v2 | 0.30 | 1 | 19 | **PASS** | PASS | PASS | 845 | `257f267bfd9d50a2` | `bd78ce089f7a0978` |

### 5.1 The E-seam bug found by the first campaign, and the fix (`_v2` tags)

The first campaign certified run A but never run B. Every run-B hole sat EXACTLY on a shared
y-edge of two ABUTTING E strips (delta 0.3 witnesses at y = 0.530, 1.090, 1.430, 2.447084), deep
inside the exempt region:

* the frozen verifier exempts a box only if the box is contained in ONE NO-family
  (`nofam_exempt` is a per-family containment test, not a union test), so a box straddling the
  shared edge of two abutting families can never be exempted, however deep it is split;
* and that seam is far from G, where the measure carries only 1, not 1+e, so the box can never be
  covered either. Result: guaranteed holes at max depth, at every seam, forever.

The G-dilation of deviation 3 protects E's OUTER boundary (against G) but does nothing for E's
INTERNAL seams. Fix (one hunk in `crowdfam92.build`): each strip is extended ONE grid cell further
in y, so consecutive strips OVERLAP by a full cell (0.02) instead of abutting. The extension moves
only the strip's MAX corner, and the exact F-disjointness certificate depends only on its MIN
corner, so the soundness proof of E is untouched — and `E-sound = True` is re-asserted on the
rebuilt families. Effect on run B at delta 0.3, same measure, same LP node:

| | boxes | covered | exempt by NO-family | holes | verdict |
|---|---|---|---|---|---|
| abutting strips (first campaign) | 32427 | 13350 | 2796 | 23 | FAIL |
| overlapping strips (`_v2`) | 596274 | 32295 | **265874** | **0** | **PASS** |

This is the single most useful engineering finding of the chore: **a caselp NO-family cover that
has to discharge a REGION (rather than exempt a few boxes) must be built with overlapping members,
because the verifier's exemption test is per-family containment.** A89's o3fam covers never hit
this because their staircase rects are all anchored at the same corner and are therefore nested,
so every box inside the union lies inside a single rect.

## 6. Phase 2 — mixed patterns for (N)

NOT REACHED in this chore's wall budget (it is gated on Phase 1 finishing and on free-commit
headroom; see section 7). The general certificate is architected but not coded: families
`G_c^(k)` with weight `e_k` and multiplicity `m_k` per corner, run A with `n = 11 + sum_c m_c e_c`
(floored to an integer, which is the sound direction), one run B per DISTINCT weight (weights
`w/(1+e_k)`, NO-families = the complement of the union of the weight-`e_k` families), and the S
corners' SHALLOW families added to run A as caselp nofams. Two things must be added to the code:
(i) `crowdfam92.build_E` must take the set of active corners and a per-corner delta (the current
builder assumes all four corners at one delta); (ii) `crowd92` must force `sym_kind="C1"` — the
mixed patterns are NOT D4-symmetric, and `Hyp([],[]).is_symmetric_D4` returns True vacuously, so
the D4 quotient would be silently wrong. A89's experience says the C1 quotient needs 5-10x the LP
time of the D4 one to reach a certifiable minmass.

## 7. Resource discipline actually used

BLAS pinned to 1 thread (`blas1` imported before numpy in every entry point). At most 2 processes:
this driver (which runs the LP in-process, as A89's `o3run` did) plus ONE `certify92`/`verify_case`
subprocess, never concurrently. `free_commit_mb()` (MEMORYSTATUSEX.ullAvailPageFile) polled every
60 s before every LP and before every certify launch; the gate requires TWO CONSECUTIVE readings
above 6144 MB before proceeding. Nothing under A57/A60/A61/A86 was read or written. The LP sweep
stops early if it would eat the certification reserve (default 80 min) — a certified two-run PASS
is the deliverable, an extra LP row is not.

## 8. Deviations from the spec / engine surprises

1. **`lpbox92.py` exists.** The spec says "add `caselp92.py` / `certify92.py` (copies with the ONE
   change below)", but the row right-hand side is set in `lpbox.Model.add_row` (`h.addRow(al,...)`)
   and the row-oracle threshold in `lpbox.RowOracle.search`, not in `caselp.py`. So the one change
   lives in a third copy, `lpbox92.py` (`lpbox.py` itself is left byte-identical to A89's), and
   `caselp92.py` imports it. The whole diff is 3 hunks:
   * module globals `RHS_MULT / RHS_MAX / RHS_CELL` (defaults `None / 1.0 / None` = A85 behaviour);
   * `Model.add_row`: `al = al * RHS_MULT(centre, theta)`;
   * `RowOracle.search`: two passes per theta (see 2) and the per-pose rhs in slot 4 of each
     violation tuple — so `lpbox.run`'s existing `minmass = viol[0][3] / viol[0][4]` is exactly the
     mass/rhs ratio with no further edit and `converged` keeps its meaning; plus one line in
     `exact_theta` for the `cell_keep` filter.
2. **The row oracle needs a second pass, not just a widened threshold** (engine surprise, and the
   one real trap). Simply raising the oracle threshold from `alpha` to `alpha*(1+e)` makes almost
   EVERY cell of `exact_theta`'s O(K^2) arrangement a candidate: a memory blow-up, and the existing
   20000-cell cap then keeps the LOWEST-mass cells (the uninteresting mass ~1 ones in the middle of
   the container) and hides the genuine 1+e violations in the corner regions — the LP would report
   convergence while run B still had holes. Fix: pass 1 = the unmodified A85 oracle at threshold
   `alpha` over the whole domain (any pose with mass < alpha is violated whatever its rhs); pass 2
   = threshold `alpha*(1+e)` with the cells pre-filtered by `RHS_CELL` to those meeting the dilated
   G. Cost: the row oracle runs twice per theta.
3. **G dilation 0.02 / 1 deg instead of the spec's EPS_ZONE = 2e-3 / EPS_TH = 0.3 deg.** The spec
   fixes the conservative DIRECTION (a pose counts as in G unless it is outside every G-rect by the
   margin — more rows at 1+e, never fewer); any larger margin is the same direction and strictly
   more conservative (it only raises tau). 0.02 (one centre-grid cell) is used because the exact
   verifier can only discharge a box straddling the boundary of E by COVERING it (mass >= 1+e on
   the whole box), which needs the box smaller than the dilation: 0.02 costs ~8 bisections per
   axis, 2e-3 would cost ~11 and roughly 60x the boundary boxes.
4. **`a_w(0.2) = 0.82253`, not the spec's printed 0.82252.** The spec's formula says "rounded UP at
   the last step"; `lambda_max*0.8 + (lambda_max-1)*0.7072 = 0.822520766...`, whose round-UP to
   1e-5 is 0.82253. The other five printed values match round-up exactly, so 0.82252 is a
   truncation in the spec text. Round-UP is also the sound direction (a_w must be large enough for
   the depth->reach transfer), so it is what is implemented.
5. **E is certified by a stronger property than "E n G_c = empty".** Every E box is exactly
   certified (Fractions, all four corners, all inflated by 1e-8 to absorb `caselp.q`'s 1e-9 outward
   rounding of the emitted NoFam corners) to be provably DISJOINT FROM `F_c(a_w)` itself — which is
   what run B's soundness actually needs and which implies interior-disjointness from G. E and G
   are exact complements by construction, so they do share boundary faces; every point of such a
   face lies in a cell proved disjoint from F, so no pose of F is ever exempted.
6. **G's D4-closure is by construction, not by a rect-list match.** The LP's G test maps the centre
   into each of the four corner frames and tests the ONE stored BL staircase, so the multiplier is
   D4-invariant identically. The materialised per-corner rect lists (o3fam `corner_fams`-style) are
   also produced and their D4 mismatch measured (2.2e-16, one ulp of `s0 - u`); a 4000-pose
   randomised D4-invariance test of the multiplier passes with 0 failures (`smoke92.py`).
7. **`format` / `symmetry` fields.** The files carry `"format": "case-lp-certificate-v1"` as asked;
   the frozen verifier does not read that field. `"symmetry": "D4"` is deliberately NOT set:
   `caselp.solve_node` already returns `atoms_all` with every D4 image expanded, so setting it
   would double every atom.
8. **Run A and run B really are one measure.** Identical atom lists, and run B's weights are
   EXACTLY run A's divided by (1+e) as rationals (asserted in `smoke92.py`).
9. `smoke92.py` and `report92.py` are extra files (not in the spec): the pre-flight test of the rhs
   hook / D4 invariance / two-run certificate format through the frozen verifier's loader, and the
   report generator that runs in-process at the end of the campaign (also on a crash).

## 9. Files

| what | path |
|---|---|
| engine copy (38 modules, verbatim from A89) | `attempts/A92-blocked-side/code/` |
| frozen verifier (byte-identical to A85's and A89's) | `code/verify_case.py`, sha256 `521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af` |
| the ONE engine change | `code/lpbox92.py` (56 diff lines vs `lpbox.py`) |
| certificate builder | `code/caselp92.py` (`make_certificate92`, 46 diff lines vs `caselp.py`) |
| two-run certifier | `code/certify92.py` |
| family builder | `code/crowdfam92.py` |
| driver | `code/crowd92.py` |
| pre-flight tests / report generator | `code/smoke92.py`, `code/report92.py` |
| families | `results/crowd92_fams.json`, `results/fam_d<delta>.json` |
| run records | `results/crowd92_runs.jsonl` |
| node LPs (resumable) | `results/nodes/<tag>.json` |
| certificates | `certs/runA_<tag>.json`, `certs/runB_<tag>.json` (+ `.report.json`, `.witnesses.json`, `<tag>.certify.json`, `<tag>.PASS`) |
| logs | `logs/crowd92.log`, `logs/crowd92.out`, `logs/fams.out`, `logs/cert_<tag>.log` |
| terminal marker | `results/CAMPAIGN_DONE` |

## 10. Resuming

    cd attempts/A92-blocked-side
    python code/crowd92.py --minutes <wall budget> --reserve_min 80 --lp_time 900 --cert_time 300

Solved node LPs are cached in `results/nodes/<tag>.json` and reused on a restart (delete them to
force a longer LP rather than a re-certify of the same measure); families are cached in
`results/fam_d<delta>.json`. Every attempt appends one record to `results/crowd92_runs.jsonl`.
