# A51 seed design — MID-TILT flush-free seeds (2026-08-31)

Producer `code/seeds_a51.py`; data `results/seeds.json`. Conventions follow
A49 `notes/seed_design.md`: seeds are LOOSE basin selectors, not near-critical
points — `repair` guarantees feasibility, a tilt comb guarantees flush-freeness
as a STRATUM property (pairwise tilt-class gaps and class-from-axis all
>= eps_open), and the DESCENT forms the actual contact structure.

## Why new seeds

A49's honest sampling caveat: all 12 seed architectures lived in the
near-upright evasion world (tilt profiles 1-7 deg, one "midtilt" profile
capped at 20 deg), and all 252 drains landed on the s = 4 axis-aligned grid.
The MID-TILT non-thin flush-free world — where the real critical families
live (every A37 atlas family has 3-5 squares at 33-45 deg) — was never
sampled. A51 seeds there.

## The tilt comb as a flush-OPENER

`stratum_a49.comb_angles(x, eps)` combs the 11 tilt classes apart on the
circle R/90deg with the axis class 0 pinned, so after combing
class-from-axis(th_i) >= eps for every i and class-distance(th_i, th_j) >= eps
for every i < j. Applied to a critical family this is exactly an OPENING of
its flush structure: every flush pair contact (equal tilt classes) and every
wall-flush (tilt class 0) becomes a small-gap corner/edge contact, while the
mid-tilt values move by at most a few tenths of a degree. `repair` then
restores exact feasibility by scaling CENTRES only, so the comb — hence
flush-freeness — survives verbatim.

## The four families (19 seeds, 19 accepted)

| family | ids | construction |
|---|---|---|
| (i) atlas-opened | M01-M08 | A37 atlas families 0, 1, 6, 13, 26, 31 opened at eps = 0.50 deg; M07/M08 = families 0 and 13 opened WIDE at 1.75 deg |
| (ii) mid-tilt lattice | M09-M12 | compact 11-site blob of the unit-square TILING lattice at base tilt 22 / 30 / 38 deg (lattice vectors (cos t, sin t), (-sin t, cos t)); tilts combed apart by 0.6 deg (M12: 1.4 deg, pack_frac 0.94) so the perfect tiling breaks into a corner-on-edge network |
| (iii) [45,0,45] fattened | M13-M15 | A47's s* = 2sqrt2+1 thin chain D_L / U / D_R, DE-QUANTIZED (U given a genuine mid tilt tU = 8 / 20 / 32 deg instead of axis-aligned; diamonds combed off exactly 45) and FATTENED: 8 complement squares in 3 rows (3/3/2) pressed down onto the chain, so every chain square has H-degree >= 3 (non-thin) |
| (iv) random mid-tilt | M16-M19 | rejection-sampled: 11 tilts uniform in [15, 45] deg, centres a randomly oriented / permuted / jittered compact tiling-lattice blob; best (smallest repaired s) of 250 draws |

Atlas picks chosen for mid-tilt content and class variety: 0 = RIGID (the
Trump packing, five squares at 40.18 deg), 1 = VALLEY (five at ~45), 6 =
VALLEY (four at 41.56), 13 = VALLEY (five at 33.90), 26 = mixed
19.7/22.4/38.4/44.8, 31 = VALLEY (three at 42.06 + 44.33).

## Acceptance (all 19 pass)

repair feasible (max pair overlap and containment violation <= 1e-9 via
`a49_common.repair_ok`, the FIXED wrapper with lam_hi = 8), flush-free at
tol_f = 0.05 deg, min tilt-class gap >= 0.30 deg, s_repaired <= 6.20,
lam - 1 <= 3.00.

Seed spread: s_repaired 3.93-4.13 for (i), 4.51-4.78 for (ii), 5.27-5.49 for
(iii), 4.66-4.84 for (iv); mid-tilt content 4-5 of 11 for (i) (the atlas
families' own profile) and 10-11 of 11 for (ii)-(iv).

## Two construction facts recorded honestly

1. **All-mid-tilt configurations are intrinsically wide.** 11 squares with
   every tilt in [15, 45] have no axis-aligned sub-block to pack against the
   walls; the best compact seed the tiling-lattice constructor produces
   repairs to s ~ 4.5-4.8, versus s = 4.0 for the trivial grid and 3.877 for
   the Trump packing. A first attempt with row-based staggered lattices
   (4/4/3 rows at pitch 0.9 x bounding width) gave s ~ 5.6-6.0; the tiling
   lattice (which is the actual unit-square tiling, broken only by the comb)
   is the right constructor and buys ~1.1 in s.
2. **The fattened [45,0,45] chain cannot be compact.** A full-width chain
   band (height ~1.41 for 45-deg diamonds) plus 8 complement squares needs
   3 more rows of ~1.3, i.e. s >= ~5.2 — even before any contact structure is
   imposed. This is the seed-level shadow of A47's s* no-completion lemma
   (no 8 unit squares fit the complement AT s*), and it is why the (iii)
   seeds start ~1.3 above s0. The descent has the most work to do here.

## Roles = TILT REGIMES (not A49 decks)

A49 labelled squares by architectural deck (B binding chain / M presser /
T top deck) and `a49_common.role_pair_category` reads `role[0]`. A51's seeds
have no deck architecture; the meaningful classification of a flush event
here is the TILT REGIME of the participants, so the same one-letter slots are
reused with A51 meanings and `summary_a51.CATMAP` translates every label:

    B = UPRIGHT (tilt class < 12 deg)
    M = MID     (12 <= tilt class < 30 deg)
    T = HIGH    (tilt class >= 30 deg, diamond-ish)

so `B-wall` reads WALL UPRIGHT, `top T-T` reads pair HIGH-HIGH, and so on.
The report never prints the A49 deck names for A51 data. Independently of the
regime labels, every event also carries the primitive WALL vs PAIR split,
which is the regime-free form of A49's wall-termination law.
