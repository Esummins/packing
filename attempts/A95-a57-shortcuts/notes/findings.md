# A95 findings (recorded by the coordinator from the chore's final report, 2026-09-04)

## T1 — parametric re-emission of 20 A57 k5_11 G1 level-1 leaves
Frozen verifier A56 verify_param.py, window [191/50, s0], depth 48, margin 0, 1500 s cap; emitter A57 to_param.py.
Ratio (parametric wall) / (4 x fixed-side wall) over 20 nodes = **0.083** (9,550 s vs 4 x 28,716 s).
**10 of 20 cover the whole window in one pass.**

| group | n | fixed | parametric | ratio / 4x | full-window |
|---|---|---|---|---|---|
| easy PASS | 10 | 3,133 s | 2,636 s | 0.210 | 5 |
| marginal PASS (eps_geo-repaired) | 5 | 11,146 s | 1,050 s | 0.024 | 5 |
| failed certification | 5 | 14,436 s | 5,865 s | 0.102 | 0 (foregone) |

Origin predicts the 4-D verdict, atom count does not (Y0049 passes at 128 atoms, Y0271 fails at 4): A57's T25
hypothesis holds. The 7 completed FAILs still certify 99.2-99.95% of the window; 36 undecided boxes, 3 holes;
the slivers recur at the same s across unrelated nodes: [3.82708, 3.827135] (13 witnesses), the endpoint
[3.82, 3.820056] (11), one at [3.876917, 3.876945] (Y0720) — fixed-s boundary degeneracy, not per-node hardness.
Timeouts: Y0211, Y1086 (failed-cert), Y0048 (easy, 16 atoms) at the 1500 s cap.

## T2 — k5_11's diagonal reflection
Stabilisers (symbolic, all 8 D4 elements): k5_11 {e, sigma_d}; k5_16 trivial. tree57.py passes sym_kind="C1"
everywhere; no orbit/mirror logic. As emitted the reduction removes 0 nodes: the t-uniform theta ladder is not
sigma-closed (t -> (1-t)/(1+t) fixes only {0,1} of {k/8}); 0 of 1,152 boxes have their mirror in the cover.
Sound reduction: sigma-symmetric ladder (nth = 10, uniform in t on [t*, 1] mirrored, t* = sqrt2 - 1), a_min >=
the deployed cover's at every side (0.3591/0.3599/0.3527/0.3536 vs 0.3566/0.3574/0.3503/0.3511), 1,440 boxes ->
720 orbits, no self-mirror boxes; mirrored certificate = rewrite (atom x<->y, cores swapped, tm -> (1-tm)/(1+tm),
rational) re-verified by verify_case; the tree obligation on the mirrored box holds by symmetry but must be
C-checked. Removed LP children: 316/315/276/270 per side (1,177 total; 861 over sides 2-4). nth = 8 halves exactly
but drops a_min below A24(iii)'s 0.35. Net ~548 s per removed child (LP + eps_geo saved 635.5 s; verify paid 87.8 s).
Cross-check: ok/contradictory counts reproduce A57's C-check table exactly (821/331, 816/336, 704/264, 695/273).

## T3 — where A57's wall goes
k5_11 G1 (296 rows): LP 54.1%, certify 23.3%, eps_geo retries 22.6%; free logic kills 29.4%; mean 635.5 s/node
(median 373); descent to level 2: 23.0%. k5_16 G1 (353 rows): LP 69.9%, certify 20.0%, eps_geo 10.2%; mean 452.6 s;
descent 26.9%. The eps_geo tail: 31 nodes = 8% of rows, 49% of wall (2,519 s / 1,701 s mean vs 307 s direct PASS).
Projection: level 1 remaining 35.8 process-days (k5_11 19.9, k5_16 15.9); level 2 ~16,400 children at 216 s
(thin: 34 D2 rows, all delta = 0) = 41.4 process-days; combined **15.4 wall-days at 5 workers, 25.7 at 3** vs T23's
6.4-day level-1-only estimate.

## Caveats
- Level-2 rate rests on 34 rows at delta = 0; one deepen.py shard at delta = 1e-2 is the cheapest next measurement.
- Nine T1 nodes were initially lost to 0xC0000142 on subprocess spawn (launcher shell torn down while the python
  driver survived); discarded and re-run; no table row is a spawn artefact. Launchers must be detached from the
  agent's shell (A96 note).
- The chore was blocked from writing this file itself; this is the record.
