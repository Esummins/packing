# A232 -- the SWAP leaf on the eleven converged-alive k0_00 cells

The leaf, its soundness and what it closes: `docs/proofs/swap_leaf.md`.  Verifier
`code/verify_swap232.py` (`swap-leaf-certificate-v1`, stdlib + exact Fractions, a NEW file --
the frozen `verify_case.py` / `verify_case_v4.py` are untouched).  Lean
`lean/.../Statements/SwapLeaf.lean` (`swap_leaf_dead`, a theorem from `cells_swap` + k1-a).
Resume: `bash attempts/A232-swap-leaf/code/run232.sh`.

`need` = |X| = the number of unit cells the leaf must place at that corner (every UNBOXED role
is forced into X -- its reach set is the whole container -- plus every boxed role whose reach
meets the corner slot).  `found` = the best family the search placed and the verifier's exact
tests accepted.  A row is DEAD only on a `verify_swap232` PASS.


## The cells

| cell | n | boxed roles | unboxed | need (min over corners) | found (best) | best corner | split children / best | verdict | s |
|---|---|---|---|---|---|---|---|---|---|
| `l1_071` | 11 | H | 10 | 10 | 7 | BL | 16 / 7 | UNDECIDED (best 7 of 10 cells, corner BL) | 203 |
| `l1_104` | 11 | H | 10 | 10 | 7 | TR | 16 / 7 | UNDECIDED (best 7 of 10 cells, corner TR) | 206 |
| `l1_124` | 11 | H | 10 | 10 | 9 | TR | 16 / 9 | UNDECIDED (best 9 of 10 cells, corner TR) | 207 |
| `l1_148` | 11 | H | 10 | 10 | 9 | TR | 16 / 9 | UNDECIDED (best 9 of 10 cells, corner TR) | 206 |
| `l1_153` | 11 | H | 10 | 10 | 9 | TR | 16 / 9 | UNDECIDED (best 9 of 10 cells, corner TR) | 202 |
| `l1_158` | 11 | H | 10 | 10 | 9 | TR | 16 / 9 | UNDECIDED (best 9 of 10 cells, corner TR) | 200 |
| `l1_159` | 11 | H | 10 | 10 | 9 | TR | 16 / 9 | UNDECIDED (best 9 of 10 cells, corner TR) | 197 |
| `l2_p114_001` | 11 | H | 10 | 10 | 9 | TR | 16 / 9 | UNDECIDED (best 9 of 10 cells, corner TR) | 200 |
| `l2_p65_101` | 11 | H | 10 | 10 | 7 | BL | 16 / 7 | UNDECIDED (best 7 of 10 cells, corner BL) | 204 |
| `l2_p65_111` | 11 | H | 10 | 10 | 7 | BL | 16 / 7 | UNDECIDED (best 7 of 10 cells, corner BL) | 201 |
| `l2_p74_001` | 11 | H | 10 | 10 | 7 | BL | 16 / 7 | UNDECIDED (best 7 of 10 cells, corner BL) | 205 |

## Per corner (need / found; reach area of the roles outside X inside [0, 3.82]^2)

| cell | BL | BR | TR | TL | roles outside X | reach area |
|---|---|---|---|---|---|---|
| `l1_071` | 10 / 7 | 10 / 7 | 10 / 7 | 10 / 7 | H | H 1.583 |
| `l1_104` | 10 / 6 | 10 / 6 | 10 / 7 | 10 / 6 | H | H 1.640 |
| `l1_124` | 10 / 6 | 10 / 6 | 11 / 9 | 10 / 5 | H | H 1.633 |
| `l1_148` | 10 / 6 | 10 / 6 | 11 / 9 | 10 / 6 | H | H 1.631 |
| `l1_153` | 10 / 7 | 10 / 7 | 11 / 9 | 10 / 6 | H | H 1.647 |
| `l1_158` | 10 / 6 | 10 / 6 | 11 / 9 | 10 / 6 | H | H 1.649 |
| `l1_159` | 10 / 7 | 10 / 7 | 11 / 9 | 10 / 7 | H | H 1.649 |
| `l2_p114_001` | 10 / 5 | 10 / 5 | 11 / 9 | 10 / 5 | H | H 1.346 |
| `l2_p65_101` | 10 / 7 | 10 / 7 | 10 / 7 | 10 / 7 | H | H 1.319 |
| `l2_p65_111` | 10 / 7 | 10 / 7 | 10 / 7 | 10 / 7 | H | H 1.320 |
| `l2_p74_001` | 10 / 7 | 10 / 7 | 10 / 7 | 10 / 7 | H | H 1.372 |

## Controls (n = 5 -- the geometry and the verifier end to end)

An |X| = 2 control CANNOT exist at n = 11 inside the window: a passing leaf there is
exactly the theorem s(11) >= s-hat.  The controls are therefore stated at n = 5 and
carry NO k1-a claim.

| control | |X| | cells found | verifier |
|---|---|---|---|
| `control_X1` | 1 | 1 | PASS |
| `control_X2` | 2 | 2 | PASS |

## Verdict

**0 of 11 cells DEAD by SWAP-LEAF.**  The leaf does not fire on any of them, and the reason is structural, not a search failure: the k0v4 cells box ONE of the eleven squares, so ten roles are unboxed and every one of them must go into X.  |X| = 10 asks for a ten-square packing of [0, 3.82]^2 (s(10) = 3.7071, slack 0.113) with one member at the corner slot and all of them avoiding the conditioned square's reach set -- see docs/proofs/swap_leaf.md s.3 for the price of getting |X| down to the PI's 2.
