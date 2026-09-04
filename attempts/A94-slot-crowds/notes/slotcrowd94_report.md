# A94 slotcrowd94 -- SLOT-CROWD certificates for k5_11 / k5_16 (Opus compute chore)

Implements `attempts/A94-slot-crowds/notes/chore_slot_cert.md`.  Everything is written under
`attempts/A94-slot-crowds/`; nothing under A57/A60/A61/A86/A92/A93 was written (A92's code and
notes were read to copy from), and the frozen `verify_case.py` was copied byte-identical
(sha256 `521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`) and never edited.

Generated 2026-09-04 08:52:47 (done); 23 LP records, 3 certification records.

## HEADLINE

**no certified (1 + r_max)-run PASS in this chore's wall budget**

LP-passing (tau < budget) nodes, per class x window: smallest / largest delta

| class | window | smallest LP delta | largest LP delta | smallest CERTIFIED delta |
|---|---|---|---|---|
| k5_11 | s0_G2 | 0.2 | 0.3 | none |
| k5_11 | G4_lo | 0.02 | 0.1 | none |
| k5_16 | s0_G2 | 0.2 | 0.3 | none |
| k5_16 | G4_lo | 0.1 | 0.1 | none |

## 0. Constants and the objects, as implemented

| quantity | value |
|---|---|
| s0 | 969271/250000 = 3.877084 |
| G2 / G3 / G4 | 965601/250000 / 192389/50000 / 958303/250000 |
| window floor | 191/50 = 3.82 |
| lambda | s / m_lo |
| rho (pin slack) | (lambda - 1) * A_S rounded UP to 1e-5, then + 1e-5; A_S = 3/2 for both classes |
| a_w(p, delta) | lambda (1-delta) + (lambda-1)(7072/10000 + max(i,j)), rounded UP to 1e-5 |
| budget | N + 2 m_u e = n - k with n = 11 + 2 m_u e; N = 6, k = 5, m_u = 4 |
| e order | 1/2, 1/4, 1, 1/8 -> n = 15, 13, 19, 12; budget 10, 8, 14, 7 |

The certificate is ONE measure mu and 1 + r_max = 5 runs of the frozen verifier:

* **run A** `certs/runA_<tag>.json` -- n = 11 + 2 m_u e, budget = n - k, cores = the k pin
  cores (axis-aligned, centre = slot_j(s) exactly, tm = 0, a = 1/2 - rho), nofams = [].
  PASS certifies mu(Q) >= 1 for every admissible closed unit square Q in [0,s]^2 meeting NO
  pin core, and mu(total) < budget = N + 2 m_u e.
* **run B_r** `certs/runB<r>_<tag>.json` (r = 1..m_u) -- the SAME atoms, weights w/(1 + r e)
  exactly, the SAME cores, n = 1000 (budget 1000 - k, a dummy), nofams = E_r.  PASS certifies
  mu(Q) >= 1 + r e for every core-free Q not provably in E_r, hence for every core-free Q
  lying in >= r of the widened slot families.

Composed (Lemma CW-S): a packing of the class at side m in [m_lo, s) whose every usable slot
is met at depth >= delta by >= 2 non-pin squares dilates (lambda = s/m, centres only) to a
disjoint family at side s whose k pin images contain the cores and whose N non-pin images
carry sum r >= 2 m_u incidences, so sum mu >= N + 2 m_u e > mu(total): contradiction.

## 1. Phase 0 canaries (all BEFORE any LP)

### Trump slot canary (`results/trump_canary94.json`, exact Trump, this chore's slot frames)

Verdict: **PASS**, max deviation from the lead's depths = 0.000e+00 (tolerance 1e-9).

| slot of trump5 | free meeters (ref) | d1 | d2 | ref d2 | |err| |
|---|---|---|---|---|---|
| BL(0,2) | 2 (2) | 0.967442 | 0.016049 | 0.016049 | 0.0e+00 |
| BL(1,1) | 2 (2) | 0.542145 | 0.280083 | 0.280083 | 0.0e+00 |
| BL(2,0) *(pin-clipped)* | 1 (1) | 0.432354 | 0.000000 | 0.000000 | 0.0e+00 |
| BR(0,1) | 2 (2) | 0.524494 | 0.252050 | 0.252050 | 0.0e+00 |
| BR(1,0) *(pin-clipped)* | 1 (1) | 0.432354 | 0.000000 | 0.000000 | 0.0e+00 |
| TR(0,1) | 2 (2) | 0.542145 | 0.264033 | 0.264033 | 0.0e+00 |
| TR(1,0) | 2 (2) | 0.451358 | 0.305293 | 0.305293 | 0.0e+00 |
| TL(0,0) | 2 (2) | 0.168321 | 0.155475 | 0.155475 | 0.0e+00 |

### Image gate (no D4 Trump image realises the PIN hypothesis of the class at side s)

| class / window | per-image count of pin slots hit (g0..g7) | realising |
|---|---|---|
| k5_11/G2_G3 | 2 3 2 2 2 3 2 2 | NONE |
| k5_11/G3_G4 | 2 3 2 2 2 3 2 2 | NONE |
| k5_11/G4_lo | 0 0 0 0 0 0 0 0 | NONE |
| k5_11/s0_G2 | 4 3 2 2 4 3 2 2 | NONE |
| k5_11/s0_lo | 4 3 2 2 4 3 2 2 | NONE |
| k5_16/G2_G3 | 3 3 3 3 3 3 3 3 | NONE |
| k5_16/G3_G4 | 3 3 3 3 3 3 3 3 | NONE |
| k5_16/G4_lo | 0 0 0 0 0 0 0 0 | NONE |
| k5_16/s0_G2 | 4 3 3 3 4 3 3 3 | NONE |
| k5_16/s0_lo | 4 3 3 3 4 3 3 3 | NONE |

Every image misses at least one pin slot (Trump's TL corner is clear), so no image
realises the node's pin hypothesis at any rho used here.  Re-checked after every
certified PASS; a PASS on a realisable node exits 9.

### e = 0 exact-pin regression LP (reproduces the class root tau at s0)

| class | budget | tau | target (A54/A57) | |d| | verdict | rows | LP s |
|---|---|---|---|---|---|---|---|
| k5_11 | 6 | 5.874007 | 5.9064 | 0.0324 | OK | 11690 | 505 |
| k5_16 | 6 | 5.959885 | 5.9731 | 0.0132 | OK | 12283 | 518 |
| k5_11 | 6 | 5.874007 | 5.9064 | 0.0324 | OK | 11690 | 505 |
| k5_16 | 6 | 5.959885 | 5.9731 | 0.0132 | OK | 12283 | 518 |

### A57 consistency

A57's G1 records are s0 slack-core tree kills of the SAME classes.  No A57 file was read or
written by this chore.  Nothing certified here claims anything at any side > the window's s;
in particular the s = s0 windows say nothing about sides above s0 = 3.877084.

## 2. The LP tables (one row per (class, window, delta, e) attempt)

Node = the class's k pin Boxes as cores (half-width h = rho/sqrt2), no NO-families, C1
quotient (a pinned class is not D4-symmetric), warm pool = A53/A54 nodes of the class
rescaled to the side plus this campaign's own solved nodes.  PASS criterion: tau < budget.

### k5_11, window (s0, G2] = [3.862404, 3.877084)

| delta | e | n | budget | rho | a_w | tau | eta | minmass | maxcov | rows | atoms | LP s | verdict | certified |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.3 | 1/2 | 15 | 10 | 0.00572 | 0.70915/0.70915/0.70915/0.70535 | 9.198135 | -0.801865 | 0.9458 | 1.1244 | 13593 | 211 | 1021 | LP-PASS (tau < budget; certificate not attempted yet) | - |
| 0.2 | 1/2 | 15 | 10 | 0.00572 | 0.80953/0.80953/0.80953/0.80573 | 9.750000 | -0.250000 | 0.6182 | 1.1789 | 11595 | 185 | 997 | LP-PASS (tau < budget; certificate not attempted yet) | FAIL(eps_geo 0.004) |
| 0.1 | 1/2 | 15 | 10 | 0.00572 | 0.90991/0.90991/0.90991/0.90611 | 10.596091 | +0.596091 | 0.6830 | 1.1307 | 11325 | 89 | 368 | refused (tau 10.596091 >= budget 10) | - |
| 0.1 | 1/4 | 13 | 8 | 0.00572 | 0.90991/0.90991/0.90991/0.90611 | 8.061735 | +0.061735 | 0.7647 | 1.1640 | 9138 | 133 | 362 | refused (tau 8.061735 >= budget 8) | - |
| 0.1 | 1/8 | 12 | 7 | 0.00572 | 0.90991/0.90991/0.90991/0.90611 | 7.007122 | +0.007122 | 0.9081 | 1.1893 | 10039 | 157 | 1010 | refused (tau 7.007122 >= budget 7) | - |
| 0.05 | 1/2 | 15 | 10 | 0.00572 | 0.96010/0.96010/0.96010/0.95630 | 10.847700 | +0.847700 | 0.5946 | 1.2467 | 8575 | 121 | 337 | refused (tau 10.847700 >= budget 10) | - |
| 0.05 | 1/4 | 13 | 8 | 0.00572 | 0.96010/0.96010/0.96010/0.95630 | 8.431688 | +0.431688 | 0.6881 | 1.1761 | 9011 | 146 | 337 | refused (tau 8.431688 >= budget 8) | - |
| 0.05 | 1/8 | 12 | 7 | 0.00572 | 0.96010/0.96010/0.96010/0.95630 | 7.084300 | +0.084300 | 0.8100 | 1.2406 | 8619 | 124 | 318 | refused (tau 7.084300 >= budget 7) | - |
| 0.02 | 1/2 | 15 | 10 | 0.00572 | 0.99022/0.99022/0.99022/0.98642 | 11.000000 | +1.000000 | 0.7755 | 1.1835 | 10574 | 144 | 357 | refused (tau 11.000000 >= budget 10) | - |
| 0.02 | 1/8 | 12 | 7 | 0.00572 | 0.99022/0.99022/0.99022/0.98642 | 7.115700 | +0.115700 | 0.8534 | 1.4360 | 9037 | 186 | 320 | refused (tau 7.115700 >= budget 7) | - |

### k5_11, window (G4, 3.82] = [3.82, 3.833212)

| delta | e | n | budget | rho | a_w | tau | eta | minmass | maxcov | rows | atoms | LP s | verdict | certified |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 1/2 | 15 | 10 | 0.00520 | 0.90902/0.90902/0.90902/0.90556 | 10.433333 | +0.433333 | 0.7667 | 1.5000 | 11557 | 142 | 322 | refused (tau 10.433333 >= budget 10) | - |
| 0.1 | 1/8 | 12 | 7 | 0.00520 | 0.90902/0.90902/0.90902/0.90556 | 6.750000 | -0.250000 | 1.0000 | 1.0313 | 12111 | 39 | 1006 | LP-PASS (tau < budget; certificate not attempted yet) | - |
| 0.04 | 1/2 | 15 | 10 | 0.00520 | 0.96923/0.96923/0.96923/0.96577 | 10.265625 | +0.265625 | 0.6966 | 1.3333 | 8871 | 55 | 308 | refused (tau 10.265625 >= budget 10) | - |
| 0.04 | 1/8 | 12 | 7 | 0.00520 | 0.96923/0.96923/0.96923/0.96577 | 6.777778 | -0.222222 | 0.8800 | 1.2000 | 13760 | 86 | 942 | LP-PASS (tau < budget; certificate not attempted yet) | - |
| 0.02 | 1/2 | 15 | 10 | 0.00520 | 0.98930/0.98930/0.98930/0.98584 | 10.545455 | +0.545455 | 0.7500 | 1.3691 | 10440 | 77 | 341 | refused (tau 10.545455 >= budget 10) | FAIL(rc=1) |
| 0.02 | 1/8 | 12 | 7 | 0.00520 | 0.98930/0.98930/0.98930/0.98584 | 6.786765 | -0.213235 | 0.9023 | 1.1176 | 14901 | 128 | 976 | LP-PASS (tau < budget; certificate not attempted yet) | FAIL(rc=1) |

### k5_16, window (s0, G2] = [3.862404, 3.877084)

| delta | e | n | budget | rho | a_w | tau | eta | minmass | maxcov | rows | atoms | LP s | verdict | certified |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.3 | 1/2 | 15 | 10 | 0.00572 | 0.70915/0.70915/0.70915/0.70915 | 9.050586 | -0.949414 | 0.8321 | 1.1676 | 12540 | 180 | 976 | LP-PASS (tau < budget; certificate not attempted yet) | - |
| 0.2 | 1/2 | 15 | 10 | 0.00572 | 0.80953/0.80953/0.80953/0.80953 | 9.423534 | -0.576466 | 0.9418 | 1.1906 | 10497 | 225 | 1001 | LP-PASS (tau < budget; certificate not attempted yet) | FAIL(eps_geo 0.004) |
| 0.1 | 1/2 | 15 | 10 | 0.00572 | 0.90991/0.90991/0.90991/0.90991 | 10.644197 | +0.644197 | 0.7395 | 1.2021 | 12363 | 126 | 384 | refused (tau 10.644197 >= budget 10) | - |
| 0.1 | 1/4 | 13 | 8 | 0.00572 | 0.90991/0.90991/0.90991/0.90991 | 8.312968 | +0.312968 | 0.7683 | 1.4118 | 12213 | 133 | 356 | refused (tau 8.312968 >= budget 8) | - |
| 0.1 | 1/8 | 12 | 7 | 0.00572 | 0.90991/0.90991/0.90991/0.90991 | 7.145716 | +0.145716 | 0.8319 | 1.2248 | 10768 | 135 | 348 | refused (tau 7.145716 >= budget 7) | - |

### k5_16, window (G4, 3.82] = [3.82, 3.833212)

| delta | e | n | budget | rho | a_w | tau | eta | minmass | maxcov | rows | atoms | LP s | verdict | certified |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 1/2 | 15 | 10 | 0.00520 | 0.90902/0.90902/0.90902/0.90902 | 10.785714 | +0.785714 | 0.6667 | 1.2383 | 11063 | 86 | 327 | refused (tau 10.785714 >= budget 10) | - |
| 0.1 | 1/8 | 12 | 7 | 0.00520 | 0.90902/0.90902/0.90902/0.90902 | 6.839286 | -0.160714 | 0.9156 | 1.1429 | 15607 | 322 | 964 | LP-PASS (tau < budget; certificate not attempted yet) | - |

## 3. Certification (5 frozen-verifier runs per node)

`certify94.py`, depth 56, jobs 1 (VERIFY_JOBS_CAP = 1), 2 witness-feedback rounds (witnesses
of EVERY failing run fed back into the SAME slot-crowd-weighted re-solve), auto scale capped
at 1.4 and chosen against the BUDGET (not n), A85 eps_geo 0.002 / 0.004 repair on a FAIL.
`<tag>.PASS` is written only if ALL 1 + r_max runs pass.

| tag | class | window | delta | e | budget | verdict | run A | runs B_r | cert s | eps_geo | sha256 A (16) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `k5_11_G4_lo_d0.02_e1o8` | k5_11 | G4_lo | 0.02 | 1/8 | 7 | **FAIL(rc=1)** | PASS | B1=PASS B2=FAIL B3=FAIL B4=FAIL | 1203 | None | df4fd6c627912ceb |
| `k5_11_s0_G2_d0.2_e1o2` | k5_11 | s0_G2 | 0.2 | 1/2 | 10 | **FAIL(eps_geo 0.004)** | FAIL | B1=FAIL B2=FAIL B3=FAIL B4=FAIL | 3725 | None | 9b9b47157812ec3f |
| `k5_16_s0_G2_d0.2_e1o2` | k5_16 | s0_G2 | 0.2 | 1/2 | 10 | **FAIL(eps_geo 0.004)** | FAIL | B1=FAIL B2=FAIL B3=FAIL B4=FAIL | 3110 | None | c4e1d9f732f5b6b6 |

## 4. Family statistics

| class | window | delta | lambda | rho | a_w per slot | G cells per slot | E_1..E_4 boxes | overshoot of G over F | max r on the grid |
|---|---|---|---|---|---|---|---|---|---|
| k5_11 | s0_G2 | 0.3 | 969271/965601 | 143/25000 | 0.70915/0.70915/0.70915/0.70535 | 62871/29102/29102/12461 | 417/597/14/14 | 5.5%/8.9%/6.9%/11.3% | 1 |
| k5_11 | s0_G2 | 0.2 | 969271/965601 | 143/25000 | 0.80953/0.80953/0.80953/0.80573 | 69888/34356/34356/15928 | 297/546/72/88 | 3.7%/7.0%/6.6%/6.9% | 2 |
| k5_11 | s0_G2 | 0.1 | 969271/965601 | 143/25000 | 0.90991/0.90991/0.90991/0.90611 | 77211/39941/39942/19749 | 111/470/160/212 | 4.8%/6.5%/5.1%/6.6% | 2 |
| k5_11 | s0_G2 | 0.1 | 969271/965601 | 143/25000 | 0.90991/0.90991/0.90991/0.90611 | 77211/39941/39942/19749 | 111/470/160/212 | 4.8%/6.5%/5.1%/6.6% | 2 |
| k5_11 | s0_G2 | 0.1 | 969271/965601 | 143/25000 | 0.90991/0.90991/0.90991/0.90611 | 77211/39941/39942/19749 | 111/470/160/212 | 4.8%/6.5%/5.1%/6.6% | 2 |
| k5_11 | s0_G2 | 0.05 | 969271/965601 | 143/25000 | 0.96010/0.96010/0.96010/0.95630 | 81054/42811/42811/21832 | 63/438/272/254 | 3.1%/5.9%/6.7%/9.7% | 4 |
| k5_11 | s0_G2 | 0.05 | 969271/965601 | 143/25000 | 0.96010/0.96010/0.96010/0.95630 | 81054/42811/42811/21832 | 63/438/272/254 | 3.1%/5.9%/6.7%/9.7% | 4 |
| k5_11 | s0_G2 | 0.05 | 969271/965601 | 143/25000 | 0.96010/0.96010/0.96010/0.95630 | 81054/42811/42811/21832 | 63/438/272/254 | 3.1%/5.9%/6.7%/9.7% | 4 |
| k5_11 | s0_G2 | 0.02 | 969271/965601 | 143/25000 | 0.99022/0.99022/0.99022/0.98642 | 83323/44662/44662/23057 | 41/406/337/271 | 2.6%/5.8%/5.3%/6.1% | 4 |
| k5_11 | s0_G2 | 0.02 | 969271/965601 | 143/25000 | 0.99022/0.99022/0.99022/0.98642 | 83323/44662/44662/23057 | 41/406/337/271 | 2.6%/5.8%/5.3%/6.1% | 4 |
| k5_11 | G4_lo | 0.1 | 958303/955000 | 13/2500 | 0.90902/0.90902/0.90902/0.90556 | 77149/39940/39940/19961 | 90/458/212/232 | 4.1%/5.9%/6.4%/6.8% | 2 |
| k5_11 | G4_lo | 0.1 | 958303/955000 | 13/2500 | 0.90902/0.90902/0.90902/0.90556 | 77149/39940/39940/19961 | 90/458/212/232 | 4.1%/5.9%/6.4%/6.8% | 2 |
| k5_11 | G4_lo | 0.04 | 958303/955000 | 13/2500 | 0.96923/0.96923/0.96923/0.96577 | 81708/43455/43455/22438 | 38/405/336/273 | 3.3%/6.3%/5.6%/7.8% | 4 |
| k5_11 | G4_lo | 0.04 | 958303/955000 | 13/2500 | 0.96923/0.96923/0.96923/0.96577 | 81708/43455/43455/22438 | 38/405/336/273 | 3.3%/6.3%/5.6%/7.8% | 4 |
| k5_11 | G4_lo | 0.02 | 958303/955000 | 13/2500 | 0.98930/0.98930/0.98930/0.98584 | 83257/44656/44656/23291 | 30/394/375/283 | 4.1%/6.6%/4.8%/8.2% | 4 |
| k5_11 | G4_lo | 0.02 | 958303/955000 | 13/2500 | 0.98930/0.98930/0.98930/0.98584 | 83257/44656/44656/23291 | 30/394/375/283 | 4.1%/6.6%/4.8%/8.2% | 4 |
| k5_16 | s0_G2 | 0.3 | 969271/965601 | 143/25000 | 0.70915/0.70915/0.70915/0.70915 | 28923/29102/29189/29189 | 387/236/21/14 | 7.3%/8.9%/6.7%/7.0% | 2 |
| k5_16 | s0_G2 | 0.2 | 969271/965601 | 143/25000 | 0.80953/0.80953/0.80953/0.80953 | 34188/34356/34428/34428 | 301/280/121/14 | 7.5%/7.0%/5.1%/6.2% | 3 |
| k5_16 | s0_G2 | 0.1 | 969271/965601 | 143/25000 | 0.90991/0.90991/0.90991/0.90991 | 39761/39941/40027/40027 | 218/292/272/14 | 6.1%/6.5%/6.7%/6.1% | 3 |
| k5_16 | s0_G2 | 0.1 | 969271/965601 | 143/25000 | 0.90991/0.90991/0.90991/0.90991 | 39761/39941/40027/40027 | 218/292/272/14 | 6.1%/6.5%/6.7%/6.1% | 3 |
| k5_16 | s0_G2 | 0.1 | 969271/965601 | 143/25000 | 0.90991/0.90991/0.90991/0.90991 | 39761/39941/40027/40027 | 218/292/272/14 | 6.1%/6.5%/6.7%/6.1% | 3 |
| k5_16 | G4_lo | 0.1 | 958303/955000 | 13/2500 | 0.90902/0.90902/0.90902/0.90902 | 39699/39940/40080/40080 | 209/284/301/14 | 6.1%/5.9%/5.8%/4.3% | 3 |
| k5_16 | G4_lo | 0.1 | 958303/955000 | 13/2500 | 0.90902/0.90902/0.90902/0.90902 | 39699/39940/40080/40080 | 209/284/301/14 | 6.1%/5.9%/5.8%/4.3% | 3 |

`G_p` is built on the ABSOLUTE 0.02 grid of [0.45, s-0.45]^2 per theta bin (A92's seven,
edges at multiples of 1/4 deg, overlapping), as the set of cells NOT provably disjoint from
`F_p(a_w(p))`; the test is exact (Fractions, 193-point t-grid with the sqrt2/2 Lipschitz pad,
inflated by 1e-8 to absorb `caselp.q`'s 1e-9 outward rounding) and is evaluated at each
cell's FRAME lower-left corner, which for a reflected frame is a different absolute corner.
`N(cell)` = the slots whose `G_p` contains the cell; `E_r` = the cells with |N| <= r-1.

## 5. Resource discipline actually used

BLAS pinned to 1 thread (`blas1` imported before numpy in every entry point).  At most 2
processes: this driver (which runs the LP in-process) plus ONE `certify94`/`verify_case`
subprocess, never concurrently.  `free_commit_mb()` (MEMORYSTATUSEX.ullAvailPageFile) polled
every 60 s before every LP and before every certify launch; the gate requires TWO CONSECUTIVE
readings above 6144 MB.  `verify_case --jobs 1` everywhere.  Nothing under A57/A60/A61/A86/
A92/A93 was written; A92's chore held the other LP slot throughout.

Campaign terminal status: **done**, 397.1 min wall, 2026-09-04 08:17:44.

## 6. Deviations from the spec / engine surprises

1. **U_S and m_u.**  The spec's sec 2 table fixes m_u = 4 for both classes, including the slot whose extension is k6_23 (k5_11 TR(0,0); k5_16 BL(1,0)), which the A56 scoreboard has as PARTIAL on [3.82, 3877/1000] rather than FULL -- while `results/slots94.json`'s `usable` field (the spec's sec 0 wording) lists only the FULL ones, i.e. m_u = 3.  The chore ran the spec's sec 2 table (m_u = 4).  This is exactly sound for the three windows with s <= G2 = 3.862404 (< 3877/1000), where k6_23 is dead over the whole window.  For the two windows with s = s0 the composed statement is sound for m in [m_lo, 3877/1000] and leaves the 8.4e-5 sliver [3877/1000, s0) to slot_crowds.md sec 5 or to A57's G1 tree; the certificates themselves are conditional statements about the DECLARED U_S and are unaffected.  A56's scoreboard was read at start-up (mtime recorded above): k6_27 was still OPEN, so k5_16 did NOT gain BR(1,0)/TL(1,0) and m_u stayed 4.
2. **a_w uses the exact per-slot max(i,j)**, not the spec's permitted blanket max(i,j) = 1.  The blanket value is the conservative simplification; the per-slot value is the formula itself and is the one implemented (it differs only for k5_11's TR(0,0), where max(i,j) = 0).
3. **`G_p` is built on the ABSOLUTE grid, not on the frame grid [-1, a_w + 3/4]^2.**  The spec builds G_p on a frame grid (sec 3) and classifies E_r's cells on the absolute grid (sec 3, E_r).  Two different grids would make the LP's `r_G` and E_r's `N(cell)` inconsistent: run B_r needs `Q not in E_r  =>  r_G(Q) >= r`, which holds only if the same cells define both.  Both are therefore built on the absolute 0.02 grid of [0.45, s-0.45]^2 (which contains every admissible centre, and whose frame image is inside [-1, a_w+3/4]^2 for every slot used, all of which have i, j <= 1).  With that, `r_G(Q)` computed by the LP hook is EXACTLY 'the cell of Q is in G_p', so the bridge is an identity (smoke test [3] checks it on 2000 random poses per r).
4. **E_r is merged by the UNION of N, not only between cells with IDENTICAL N.**  A run of cells is merged while the union of their N still has <= r - 1 slots.  This is exactly as sound as the spec's rule -- the merged box's FRAME lower-left corner is the corner of one of its cells, and that cell is provably disjoint from every slot outside its own N, hence outside the union -- and it also merges along y (identical x-range, same rule).  It roughly halves the box count (e.g. E_3 goes from 934 to 272 boxes), which matters because the verifier tests every NO-family against every box.  Every emitted box is re-asserted EXACTLY, slot by slot.
5. **Reflected frames take the EXACT image of the emitted t-interval**, not a re-derived `t_lo(90-T1) .. t_hi(90-T0)`.  The certificate writes the absolute interval [t_lo(T0), t_hi(T1)]; its image under t -> (1-t)/(1+t) is computed exactly and used as the frame t-grid.  Re-deriving t_lo/t_hi at 90 - T rounds outward in the WRONG place and need not contain that image (both are within ~2/2^24 of the true endpoint, in an uncontrolled order).
6. **Speed: f(cx, cy, t) = f(cx - cy, 0, t) + cy** (because max(x+d, y+d) = max(x,y) + d).  Every exact disjointness test is therefore a lookup in a cached one-parameter table; the whole family build touches ~5x10^3 table entries instead of ~10^6 f-evaluations, and one (class, window, delta) builds in ~90 s.
7. **The LP cores are strictly smaller than the certificate cores.**  `caselp.Box.core()` derives a = (1/2 - hd)/(1 + (t1-t0)) with hd >= h*sqrt2 >= rho and t1 - t0 = 2^-24, so the LP's core is contained in the emitted core (a' <= 1/2 - rho, asserted): the LP sees at least every row the certificate exempts, which is the sound direction.  The emitted cores are exactly the spec's (kx, ky) = slot_j(s), tm = 0, a = 1/2 - rho.
8. **G dilation 0.02 / 1 deg** for the LP row rhs instead of the spec's EPS_ZONE = 2e-3 / EPS_TH = 0.3 deg -- the same conservative direction (a pose counts as in G unless it is outside by the margin: more rows at the higher rhs, never fewer), and one centre-grid cell, exactly as A92 argued (the exact verifier resolves a box straddling the boundary of E_r only by covering it, which needs the box smaller than the dilation).
9. **`sym_kind = "C1"`** everywhere (the spec's choice): a pinned class is not D4-symmetric, and `Hyp.is_symmetric_D4` returns False as soon as there are core boxes, so there is no silent D4 quotient.  k5_11's transpose symmetry is NOT exploited.
10. **`lpbox94.py` / `caselp94.py`** are the A92 `lpbox92`/`caselp92` copies (the rhs hooks unchanged in kind), renamed for self-containment; the only addition is `caselp94.make_certificate94`, which writes the k pin CORES into every file and sets budget = n - #cores (A92's `make_certificate92` always wrote `cores: []`).
11. **`certify94` picks the weight scale against the BUDGET, not n** (A92's node had no cores, so budget = n there).  A scale chosen against n would emit a certificate with total >= budget and the frozen verifier would refuse it outright.
12. **`smoke94.py`, `canary94.py`, `report94.py`** are extra files (not named in the spec): the pre-flight tests, the two canaries, and the report generator that runs in-process at the end of the campaign (also on a crash).
13. **The delta sweep runs DOWNWARDS and stops at the first failure.**  The spec's sec 7 order is 0.05, 0.02, 0.03, 0.10, 0.20, 0.30 (smallest first).  But eta(delta) is monotone DECREASING in delta: a_w(p, delta) = lambda(1-delta) + (lambda-1)(...) strictly decreases as delta grows, every F_p and hence every G_p shrinks, so tau falls, while the budget N + 2 m_u e does not depend on delta at all.  The LP-passing set is therefore upward-closed in delta, and scanning downwards until the first failing delta finds exactly the same SMALLEST passing delta the spec's order would, without paying for the deltas below it.  (The spec's order was run first and its results for the small deltas are in the tables; the cached nodes are reused.)
14. **The campaign was killed externally after 66 min of its first 480 min run** (no `CAMPAIGN_DONE`, no report) and was resumed from its node/family caches for the remaining budget.  The report is now rewritten after EVERY record, so a hard kill always leaves a current report on disk.
15. **Every LP is two-stage (probe then full), and the e-sweep is model-guided.**  The spec's run order sweeps e in 1/2, 1/4, 1, 1/8 for each of 6 deltas x 2 classes x up to 5 windows at lp_time 900 s -- more than 12 h for Phase 1 alone, against a 480 min budget.  Two wall-budget devices were used, neither of which can turn a FAIL into a PASS: (a) every LP first runs a `--probe_time` (300 s) stage, and a probe whose tau is already >= budget refuses the node without spending the rest of lp_time (tau only rises as the row oracle keeps finding violated poses); a probe below budget is continued, warm-started, for the remaining lp_time.  (b) after a failing e, the remaining e values are reordered by the one-parameter model eta(e) = (tau_0 - N) + (c - 2 m_u) e with c = (tau - tau_0)/e measured on that run and tau_0 the class's e = 0 root tau, and at most `--max_e` (3) values of e are tried per (class, window, delta).  Both are recorded per run in `slotcrowd94_runs.jsonl` (`tau_probe`, `probe_s`).
16. **A verifier timeout** (`--verify_timeout`, default max(600, 2 x cert_time) seconds per run) was added so that a single pathological frozen-verifier run cannot consume the whole wall budget; a timeout is recorded as a FAIL of that run, never as a PASS.

## 7. Files

| what | path |
|---|---|
| engine copy (A92's, verbatim) | `attempts/A94-slot-crowds/code/` |
| frozen verifier | `code/verify_case.py`, sha256 `521cb01f...cbef7af` |
| rhs-hooked LP / certificate builder | `code/lpbox94.py`, `code/caselp94.py` (`make_certificate94`) |
| slot families, E_r, rhs hooks | `code/slotfam94.py` |
| canaries | `code/canary94.py` |
| driver | `code/slotcrowd94.py` |
| (1 + r_max)-run certifier | `code/certify94.py` |
| pre-flight tests / report generator | `code/smoke94.py`, `code/report94.py` |
| families | `results/fams/fam_<cls>_<window>_d<delta>.json` |
| run records | `results/slotcrowd94_runs.jsonl` |
| Phase 0 record | `results/phase0.json` |
| node LPs (resumable) | `results/nodes/<tag>.json` |
| certificates | `certs/runA_<tag>.json`, `certs/runB<r>_<tag>.json` (+ `.report.json`, `.witnesses.json`, `<tag>.certify.json`, `<tag>.PASS`) |
| logs | `logs/slotcrowd94.log`, `logs/cert_<tag>.log`, `logs/smoke94.out` |
| terminal marker | `results/CAMPAIGN_DONE` |

## 8. Resuming

    cd attempts/A94-slot-crowds
    python code/slotcrowd94.py --minutes <wall> --reserve_min 150 --lp_time 900 --cert_time 300

Solved node LPs are cached in `results/nodes/<tag>.json` and reused on a restart (delete one
to force a longer LP rather than a re-certify of the same measure); families are cached in
`results/fams/`.  Every attempt appends one record to `results/slotcrowd94_runs.jsonl`.
