# A109 -- node-level SLOT-CROWD rows in A57's tree (Opus chore, measurement)

> **VERDICT.  Node-level crowd rows kill 0 of 18 genuinely-alive A57 nodes at every depth the window licenses (delta_sound = 0, delta = 0.05, delta = 0.1) and 18 of 18 at delta = 0.3, certify 0 of 10, cost 128 s per node per delta, and are worth -0.4 wall-days.**  The mechanism is real but its threshold sits at delta ~ 0.2-0.3, and Theorem N-S licenses a delta-certificate only for sides m <= s-hat' - delta = 3.577 -- 0.24 BELOW the window floor 3.82.  On the window itself the only licensed pad is `a_w = 1` ("two non-pin squares MEET the slot box"), and there the LP's own fractional packing realises c = 6.23 incidences against a guaranteed budget of B = 4.37, so the crowd rows make eta WORSE by +0.77 on average.

## T3 -- price, composition, verdict

### price (measured)

| item | value |
|---|---|
| crowd re-solve per (node, cfg), mean / median / max | 128 / 92 / 392 s |
| the same node's ORIGINAL A57 LP wall, mean / median | 396 / 321 s |
| A57's measured LP+certify wall per level-1 node (block96 sec 3) | 581 s |
| certification (1 + r_max frozen runs incl. one witness-feedback round), mean | 72 s |
| certified | 0 of 10 |

### kills per level and what they would remove from A57's remaining schedule

Baseline (LOG.md 2026-09-05, A96 core96 accounting): **66.53 CPU-days = 13.31 wall-days at 5 workers**, 1536 open boxes (L1 1096, L2 389, L3 39, L4 12), tail at levels 3-4.

| cfg | attributable kills L1 | L2 | rate | route (a) cost | route (a) gain | net wall-days at 5w |
|---|---|---|---|---|---|---|
| sound | 0/13 | 0/5 | 0.00 | 2.1 CPU-d | 0.0 CPU-d | -0.4 |
| d0.05 | 0/13 | 0/5 | 0.00 | 1.8 CPU-d | 0.0 CPU-d | -0.4 |
| d0.1 | 0/13 | 0/5 | 0.00 | 2.1 CPU-d | 0.0 CPU-d | -0.4 |
| d0.3 | 13/13 | 5/5 | 1.00 | 3.0 CPU-d | 66.5 CPU-d | +12.7 |

Route **(a)** = one crowd re-solve on every open box (cost above), harvesting the killed box AND its whole subtree.  Route **(b)** = crowd rows in every node LP from the start: the same per-node cost is paid on every child, and the rows only raise tau, so at the same kill rate it is never cheaper than (a); at the delta values the window licenses it is a pure 2.1-CPU-day loss.

### composition with the parametric window certificate

* **Run A rides.** `A96/code/verify_param.py` proves `mu_s(Q) >= 1 + margin` for every `s` in `[s_lo, s_hi]` and every core-free admissible `Q`, with the atoms and the pin cores affine in `s` and the budget clause `sum w_i < n - #cores` s-free.  The crowd run A is exactly that certificate with `n = 11 + eB`, so it goes through unchanged; and `--strict-margin r e` is exactly run `B_r`'s inequality.

* **Runs B_r do not.** `verify_param.py` line 529-530 raises `nofams unsupported`, and runs `B_r` are defined by the exempt cover `E_r`.  The extension is architecturally small -- the slot frame is anchored to a container corner, so `F_p(a_w)` is s-INDEPENDENT in the frame and every `E_r` box is an affine `alpha + beta s` rectangle with `beta in {0,1}` per side, the same affine form the file already uses for atoms and cores -- but it does not exist today.  **So crowd rows can only be run at the fixed side s0 as things stand.**

* At a fixed side `s0` the k6_23 slot is usable (its A54 fixed-`s0` certificate applies), so `m_u = 4`; on A57's G1 SLAB it is not, so `m_u = 3` (notes/method.md).

## T2 -- crowd rows at the node level

Window: A57's G1 slack-core slab (m_lo, s0] with m_lo = 3.8616375, lambda_max = 1.003999988.

`B` = 2 m_u - (crowd incidences the branched core may carry, bounded over B+); `bonus` = floor(e B); `c` = (tau_crowd - tau_node)/e = the incidences the LP's own fractional packing realises.  A kill needs c < B.

`eta - eta0 = c e - floor(eB) >= 0 whenever c >= B`: the crowd rows then move the node AWAY from death, whatever e is used.

**ATTRIBUTABLE** = the node was genuinely alive at the LP (eta0 = tau_node - budget_node >= 0) and the crowd rows drive eta < 0.  A node with eta0 < 0 was already dead-pending-convergence in A57 and its death is not the crowd rows' doing.

| cfg | m_u | a_w | nodes | eta0>=0 | **ATTRIBUTABLE kills** | mean B | mean bonus | mean c = dtau/de | c >= B | DEAD | dead-unconv | mean eta | mean eta-eta0 | mean LP s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SOUND (a_w = 1+1e-5, m_u = 3) | 3 | 100001/100000 | 46 | 18 | **0** (0 converged) | 4.37 | 1.00 | 6.23 | 43/46 | **8** | 15 | 0.258 | 0.769 | 119 |
| delta = 0.05 (m_u = 4) | 4 | 96063/100000 | 46 | 18 | **0** (0 converged) | 6.22 | 1.22 | 7.69 | 40/46 | **10** | 14 | 0.347 | 0.857 | 101 |
| delta = 0.1 (m_u = 4) | 4 | 91043/100000 | 46 | 18 | **0** (0 converged) | 6.35 | 1.52 | 7.04 | 38/46 | **11** | 18 | 0.133 | 0.643 | 120 |
| delta = 0.3 (m_u = 4) | 4 | 70963/100000 | 46 | 18 | **18** (11 converged) | 6.72 | 4.63 | 4.80 | 2/46 | **34** | 46 | -1.588 | -1.078 | 167 |

Re-scored with the TIGHTER incidence budget `B_tight` (r_max over the branch box itself rather than over B+):

| cfg | mean B_used | mean B_tight | c >= B_tight | DEAD (tight) | dead-unconv (tight) |
|---|---|---|---|---|---|
| sound | 4.37 | 4.57 | 41/46 | **8** | 15 |
| d0.05 | 6.22 | 6.50 | 40/46 | **10** | 15 |
| d0.1 | 6.35 | 6.59 | 37/46 | **11** | 18 |
| d0.3 | 6.72 | 7.15 | 0/46 | **34** | 46 |

### by stratum and level (DEAD / n)

| stratum | level | n | sound | d0.05 | d0.1 | d0.3 |
|---|---|---|---|---|---|---|
| control:unexplained | 1 | 9 | 2/9 | 3/9 | 2/9 | 9/9 |
| control:unexplained | 2 | 1 | 0/1 | 0/1 | 0/1 | 1/1 |
| shadow:S01 | 1 | 8 | 0/8 | 0/8 | 0/8 | 5/8 |
| shadow:S01 | 2 | 7 | 1/7 | 1/7 | 1/7 | 2/7 |
| shadow:S03 | 1 | 4 | 0/4 | 0/4 | 0/4 | 3/4 |
| shadow:S03 | 2 | 4 | 0/4 | 0/4 | 1/4 | 2/4 |
| shadow:S04 | 1 | 5 | 4/5 | 4/5 | 3/5 | 5/5 |
| shadow:S04 | 2 | 3 | 1/3 | 1/3 | 2/3 | 3/3 |
| shadow:S05 | 1 | 4 | 0/4 | 0/4 | 1/4 | 3/4 |
| shadow:S05 | 2 | 1 | 0/1 | 1/1 | 1/1 | 1/1 |

### per node (eta = tau - budget; DEAD iff converged and eta < 0)

| node | cls | lvl | stratum | budget | tau_node | eta sound | eta d0.05 | eta d0.1 | eta d0.3 | B(sound) | c(sound) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `k5_11_interior_Y0023` | k5_11 | 1 | control:unexplained | 5 | 4.0000 | -0.618 | -0.125 | -0.250 | **-0.500** | 4 | 5.53 |
| `k5_11_interior_Y0024` | k5_11 | 1 | control:unexplained | 5 | 4.0000 | **-0.750** | **-0.250** | **-0.250** | **-0.750** | 4 | 5.00 |
| `k5_11_interior_Y0059_D05` | k5_11 | 2 | shadow:S04 | 5 | 4.0000 | -0.500 | -0.000 | **-0.250** | **-2.000** | 4 | 6.00 |
| `k5_11_interior_Y0110` | k5_11 | 1 | control:unexplained | 5 | 3.5000 | -0.833 | -2.310 | -2.000 | **-4.500** | 3 | 3.33 |
| `k5_11_interior_Y0125` | k5_11 | 1 | shadow:S04 | 5 | 4.0000 | **-0.750** | **-0.625** | **-1.000** | **-1.250** | 5 | 5.00 |
| `k5_11_interior_Y0127_D03` | k5_11 | 2 | shadow:S03 | 5 | 4.5000 | +0.125 | +0.619 | +0.375 | -2.667 | 4 | 6.50 |
| `k5_11_interior_Y0133_D03` | k5_11 | 2 | shadow:S03 | 5 | 5.0000 | +0.083 | +0.750 | +0.121 | -2.500 | 4 | 4.33 |
| `k5_11_interior_Y0146` | k5_11 | 1 | shadow:S04 | 5 | 4.0000 | **-1.000** | **-0.750** | **-1.000** | **-1.250** | 5 | 4.00 |
| `k5_11_interior_Y0147` | k5_11 | 1 | shadow:S01 | 5 | 5.0000 | +2.250 | +1.000 | +1.000 | **-1.000** | 3 | 6.50 |
| `k5_11_interior_Y0186_D00` | k5_11 | 2 | shadow:S01 | 5 | 5.0000 | +0.500 | +0.625 | +0.500 | -2.500 | 4 | 6.00 |
| `k5_11_interior_Y0188` | k5_11 | 1 | shadow:S01 | 5 | 5.2791 | +1.150 | +1.671 | +1.536 | **-1.000** | 5 | 7.48 |
| `k5_11_interior_Y0203` | k5_11 | 1 | shadow:S03 | 5 | 4.5000 | +0.000 | +0.500 | +0.313 | -0.786 | 4 | 6.00 |
| `k5_11_interior_Y0217` | k5_11 | 1 | shadow:S05 | 5 | 5.0000 | +0.750 | +1.250 | +1.000 | -2.000 | 4 | 7.00 |
| `k5_11_interior_Y0241_D02` | k5_11 | 2 | control:unexplained | 5 | 3.5000 | -0.955 | -2.500 | -2.500 | **-5.000** | 3 | 3.09 |
| `k5_11_interior_Y0305` | k5_11 | 1 | shadow:S04 | 5 | 4.0000 | **-1.000** | **-0.750** | **-1.250** | **-1.250** | 5 | 4.00 |
| `k5_11_interior_Y0355` | k5_11 | 1 | shadow:S05 | 5 | 5.0000 | +0.250 | +0.750 | +0.500 | **-1.500** | 4 | 5.00 |
| `k5_11_interior_Y0391` | k5_11 | 1 | shadow:S03 | 5 | 5.0000 | +1.000 | +1.500 | +1.250 | **-1.000** | 5 | 8.00 |
| `k5_11_interior_Y0414` | k5_11 | 1 | shadow:S01 | 5 | 5.0000 | +0.792 | +1.250 | +1.000 | -2.000 | 4 | 7.17 |
| `k5_11_interior_Y0504` | k5_11 | 1 | control:unexplained | 5 | 3.7000 | -1.125 | -0.667 | -0.650 | **-1.125** | 4 | 4.70 |
| `k5_11_interior_Y0715` | k5_11 | 1 | control:unexplained | 5 | 4.0000 | **-0.750** | **-0.250** | -0.250 | **-0.500** | 4 | 5.00 |
| `k5_11_interior_Y0738_D06` | k5_11 | 2 | shadow:S01 | 5 | 4.3333 | -0.395 | +0.125 | -0.063 | -1.667 | 4 | 5.09 |
| `k5_11_interior_Y1015` | k5_11 | 1 | shadow:S01 | 5 | 5.0000 | +0.500 | +0.750 | +0.500 | **-2.000** | 4 | 6.00 |
| `k5_11_interior_Y1038_D06` | k5_11 | 2 | shadow:S01 | 5 | 5.0000 | +0.250 | +0.750 | +0.500 | **-0.375** | 4 | 5.00 |
| `k5_11_interior_Y1087` | k5_11 | 1 | control:unexplained | 5 | 4.0000 | +1.000 | **-0.500** | **-0.500** | **-0.750** | 3 | 6.00 |
| `k5_11_interior_Y1146_D02` | k5_11 | 2 | shadow:S01 | 5 | 5.0000 | +0.750 | +1.125 | +0.643 | -1.200 | 4 | 7.00 |
| `k5_16_interior_Y0004` | k5_16 | 1 | shadow:S04 | 5 | 4.0000 | +0.000 | +0.000 | -0.000 | **-0.750** | 6 | 8.00 |
| `k5_16_interior_Y0011` | k5_16 | 1 | control:unexplained | 5 | 4.0000 | +0.000 | +0.000 | +0.000 | **-0.750** | 6 | 8.00 |
| `k5_16_interior_Y0012` | k5_16 | 1 | control:unexplained | 5 | 4.0000 | +0.000 | +0.000 | +0.000 | **-0.750** | 6 | 8.00 |
| `k5_16_interior_Y0041_D03` | k5_16 | 2 | shadow:S03 | 5 | 4.8333 | +0.975 | +1.250 | +0.732 | **-2.000** | 6 | 8.57 |
| `k5_16_interior_Y0059_D03` | k5_16 | 2 | shadow:S01 | 5 | 4.6667 | +0.731 | +1.104 | +1.042 | -2.333 | 5 | 8.26 |
| `k5_16_interior_Y0059_D07` | k5_16 | 2 | shadow:S04 | 5 | 4.0000 | **-0.250** | +0.125 | +0.000 | **-0.750** | 5 | 7.00 |
| `k5_16_interior_Y0101_D03` | k5_16 | 2 | shadow:S01 | 5 | 4.0000 | **-0.750** | **-0.250** | **-0.375** | **-1.250** | 4 | 5.00 |
| `k5_16_interior_Y0101_D06` | k5_16 | 2 | shadow:S04 | 5 | 4.0000 | -0.583 | **-0.250** | **-0.500** | **-1.250** | 4 | 5.67 |
| `k5_16_interior_Y0143_D03` | k5_16 | 2 | shadow:S05 | 5 | 4.9167 | +0.125 | **-0.437** | **-1.000** | **-2.000** | 6 | 4.83 |
| `k5_16_interior_Y0149_D03` | k5_16 | 2 | shadow:S03 | 5 | 4.0000 | +1.000 | -0.000 | **-0.250** | **-1.000** | 3 | 6.00 |
| `k5_16_interior_Y0155_D07` | k5_16 | 2 | shadow:S01 | 5 | 5.0000 | +1.250 | +1.500 | +1.395 | -1.222 | 6 | 9.00 |
| `k5_16_interior_Y0179` | k5_16 | 1 | control:unexplained | 5 | 4.0000 | +0.000 | +0.000 | +0.000 | **-0.750** | 6 | 8.00 |
| `k5_16_interior_Y0186` | k5_16 | 1 | shadow:S03 | 5 | 5.1333 | +1.167 | +1.714 | +1.647 | **-1.000** | 5 | 8.13 |
| `k5_16_interior_Y0193` | k5_16 | 1 | shadow:S04 | 5 | 4.0000 | **-1.000** | **-0.500** | -0.500 | **-4.500** | 4 | 4.00 |
| `k5_16_interior_Y0485` | k5_16 | 1 | shadow:S01 | 5 | 5.0000 | +0.833 | +1.500 | +1.208 | -2.667 | 5 | 7.33 |
| `k5_16_interior_Y0590` | k5_16 | 1 | shadow:S01 | 5 | 5.0000 | +0.750 | +1.250 | +1.250 | **-1.000** | 4 | 7.00 |
| `k5_16_interior_Y0593` | k5_16 | 1 | shadow:S01 | 5 | 4.9091 | +0.656 | +0.875 | +0.800 | -2.028 | 4 | 6.99 |
| `k5_16_interior_Y0823` | k5_16 | 1 | shadow:S01 | 5 | 5.0000 | +2.500 | +1.250 | +1.000 | **-2.000** | 3 | 7.00 |
| `k5_16_interior_Y0865` | k5_16 | 1 | shadow:S03 | 5 | 5.0000 | +0.875 | +1.125 | +0.875 | **-1.000** | 4 | 7.50 |
| `k5_16_interior_Y1142` | k5_16 | 1 | shadow:S05 | 5 | 4.7297 | +0.368 | +0.750 | **-1.000** | **-2.000** | 5 | 6.55 |
| `k5_16_interior_Y1148` | k5_16 | 1 | shadow:S05 | 5 | 5.0000 | +2.500 | +1.000 | +0.500 | **-1.000** | 3 | 7.00 |

### certification of the DEAD nodes (frozen verify_case.py, A94's 1 + r_max form)

| node/cfg | result | runs | holes | wall s |
|---|---|---|---|---|
| `k5_11_interior_Y0146__sound__e1o4` | FAIL | A=PASS B1=FAIL B2=FAIL B3=FAIL | B1:5; B2:27; B3:32 | 82.2 |
| `k5_11_interior_Y0305__sound__e1o4` | FAIL | A=PASS B1=FAIL B2=FAIL B3=FAIL | B1:6; B2:32; B3:24 | 72.3 |
| `k5_16_interior_Y0193__sound__e1o4` | FAIL | A=PASS B1=PASS B2=FAIL B3=FAIL | B2:32; B3:26 | 88.5 |
| `k5_16_interior_Y0101_D03__sound__e1o4` | FAIL | A=PASS B1=FAIL B2=FAIL B3=FAIL | B1:5; B2:32; B3:32 | 62.8 |
| `k5_11_interior_Y0125__sound__e1o4` | FAIL | A=PASS B1=FAIL B2=FAIL B3=FAIL | B1:27; B2:23; B3:32 | 71.4 |
| `k5_11_interior_Y1015__d0.3__e1` | FAIL | A=PASS B1=FAIL B2=FAIL B3=FAIL B4=FAIL | B1:18; B2:32; B3:32; B4:32 | 64.6 |
| `k5_16_interior_Y0823__d0.3__e1` | FAIL | A=FAIL B1=FAIL B2=FAIL B3=FAIL B4=FAIL | A:1; B1:24; B2:32; B3:32; B4:8 | 102.1 |
| `k5_11_interior_Y0110__d0.3__e1` | FAIL | A=PASS B1=PASS B2=FAIL B3=PASS B4=FAIL | B2:32; B4:16 | 26.7 |
| `k5_16_interior_Y0193__d0.3__e1` | FAIL | A=PASS B1=FAIL B2=FAIL B3=FAIL B4=FAIL | B1:30; B2:32; B3:29; B4:24 | 36.4 |
| `k5_16_interior_Y0143_D03__d0.3__e1` | FAIL | A=PASS B1=FAIL B2=FAIL B3=FAIL B4=FAIL | B1:8; B2:32; B3:32; B4:8 | 116.5 |

### Trump canary

* exact Trump slot depths reproduce `docs/proofs/slot_crowds.md` sec 7 to 4.7e-07 -- PASS
* trump5 class root (slack pins rho = 1e-2, the exact Trump SATISFIES it), sound: budget 6 -> 9, tau = 10.3321, eta = +1.3321, converged False, **DEAD = False** (must not die: True)
* trump5 class root (slack pins rho = 1e-2, the exact Trump SATISFIES it), d0.05: budget 6 -> 10, tau = 11.2013, eta = +1.2013, converged False, **DEAD = False** (must not die: True)
* trump5 class root (slack pins rho = 1e-2, the exact Trump SATISFIES it), d0.1: budget 6 -> 10, tau = 11.0426, eta = +1.0426, converged False, **DEAD = False** (must not die: True)
* trump5 class root (slack pins rho = 1e-2, the exact Trump SATISFIES it), d0.3: budget 6 -> 10, tau = 9.4863, eta = -0.5137, converged False, **DEAD = True** (must not die: False)
* verdict: **PASS**

## T1 -- what the dual supports leave empty

Weight of the node's dual support inside each usable slot box (the crowd rows charge exactly this).  `viol` = at least one usable slot met with weight < 2, i.e. a support that Lemma SLOT-CROWD forbids.  U3 = the three FULL-window slots (the only ones licensed on the G1 slab); U4 adds the k6_23 slot (licensed only at a fixed side s0).

| shadow | nodes | classes | frac viol U3 d>0 | mean violated slots (of 3) | mean total incidence (need 6) | frac viol U3 d>=0.05 | d>=0.1 | d>=0.3 | frac viol U4 d>0 |
|---|---|---|---|---|---|---|---|---|---|
| S01 | 385 | k5_11 x221, k5_16 x164 | **0.943** | 1.92 | 4.89 | 0.992 | 0.995 | 1.000 | 0.984 |
| S03 | 76 | k5_11 x29, k5_16 x47 | **0.947** | 1.75 | 5.09 | 0.987 | 1.000 | 1.000 | 0.987 |
| S04 | 57 | k5_11 x10, k5_16 x47 | **0.965** | 2.07 | 3.60 | 1.000 | 1.000 | 1.000 | 1.000 |
| S05 | 34 | k5_11 x3, k5_16 x31 | **0.794** | 1.53 | 5.29 | 0.853 | 1.000 | 1.000 | 1.000 |
| ALL | 552 | k5_11 x263, k5_16 x289 | **0.937** | 1.89 | 4.81 | 0.984 | 0.996 | 1.000 | 0.987 |

Which usable slot the support leaves empty or singly met (U3, d > 0), over all 552 explained nodes: {'k5_11/BL(1,1)': 214, 'k5_11/BR(0,1)': 189, 'k5_16/TR(1,0)': 185, 'k5_11/TL(1,0)': 175, 'k5_16/BR(0,1)': 168, 'k5_16/TR(0,1)': 107}

**Why T1's 94 % upper bound collapses to a 0 % kill rate in T2.**  T1 measures the incidence of the dual support A57's LP happened to stop at; the crowd rows do not forbid that support, they re-price it, and the LP simply moves.  The measured slope `c = dtau/de` -- the incidences the RE-OPTIMISED fractional packing realises -- is 6.23 on average at `a_w = 1` against a guaranteed `B = 4.37`, i.e. the ghost buys the whole crowd and more.  The usable slot boxes of a class are 0.877 apart in each axis at s0 while a 45-degree unit square spans 1.414, so one fractional placement can sit in two or three of them at once; that is exactly the multiplicity Lemma CW-S has to pay for with the incidence budget `N + 2 m_u e`, and at the licensed pad it is a wash.  Depth is what breaks the multiplicity: at delta = 0.3 the same slope falls to 4.83 and every node dies.

## Pointers

* method, the `a_w = 1` derivation and the node-level incidence budget: `attempts/A109-node-crowd/notes/method.md`
* code: `attempts/A109-node-crowd/code/` (A94 engine copied verbatim + `a109lib.py`, `t1.py`, `plan109.py`, `t2.py`, `certify109.py`, `canary109.py`, `aw_check.py`, `t3.py`, `report109.py`)
* results: `results/t1_incidence.json`, `results/t1_summary.json`, `results/t2_plan.json`, `results/t2_runs_s*.jsonl`, `results/B_tight.json`, `results/t2_certs.jsonl`, `results/t3.json`, `results/canary109.json`, `results/nodes/` (every node json used, copied), `results/fams/` (the crowd families)
* certificates: `certs/runA_*.json`, `certs/runB*_*.json`, `certs/*.certify.json`
* logs: `logs/t1.log`, `logs/t2_s*.log`, `logs/certify109.out`, `logs/canary109.out`, `logs/aw_check.log`

