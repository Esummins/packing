# A76 - grain discharge near Trump: findings (Fable lead, 2026-09-02)

Labels: [T] proved, [M] measured (exact unless "float"), [C] open. Theory: docs/proofs/grain_discharge.md
(G-R, K, DF, D2'', the wall, size law); P-B(R): docs/proofs/pair_kill.md sect 6.8. Registry/LOG carry the
one-paragraph versions.

1. WALL [T+M]: no radius beyond A22/A36/A40 is certified for stuck minimisers of the exact strata, and none
   is cheaply reachable. Every grain discharge is a box-wide nonsingularity statement whose radius is set by
   kappa_eff; hinge grains (a strip flush pair degraded to a single-corner contact) have drain-flex ratio
   10.7 at (1e-3,1e-3) and 48 at (1e-2,2e-3); all-pass box ~1e-4.
2. SIZE LAW [M float, exact half-widths]: k4_08 = 1.7e7 grains; 143 370 at codim <= 4; hard = 113 / 335 /
   658 / 13 702 at (1e-3,1e-3) / (2e-3,2e-3) / (5e-3,1e-3) / (1e-2,2e-3); ratio decreases with codim.
   Residue ~ratio^d per hard grain: ~1e7 Krawczyk steps for (1e-2,2e-3). Same families for every pin set.
3. LOCAL COMPLETENESS [T, M exact]: 78 of 1936 candidate rows on the target box (36 Trump + 20 upright
   coincidences + 22 contact-type switches); 56 = Trump's rows up to rc + 1.4 rt ~ 6e-3.
4. DICHOTOMY [T]: rigid (=> z-hat, removed by the exact stratum) or s-flexible (=> drain-flex curve); no
   positive dependency at z-hat; 21 necessary FJ rows, smallest multipliers on the ring flush pairs.
5. PINS [M exact]: 10% in the uniform Krawczyk radius; 2x in the centre radius (anisotropic); tilt cap ~4e-3.
6. LP [M float]: basin-row margin saturates in r_z (-1.40 -> -1.51 from 1e-3 to 1e-2 at gamma = 0.1):
   reserve, not lever; the fronts do not meet.
7. A40 basin EXACT-rechecked (2930 certs, 0 failures): P-B(R) per coordinate (6.55e-3 - sqrt2 rho_B,
   3.27e-3); rBasin raisable to 27/10000. Trivial radii: k4_05 0.4365, corners4 0.8445.
8. By-product: t-native exact Krawczyk enclosure of z-hat (E.COORD rung); certs/verify_grain.py.

Canary: Trump = the rigid grain's unique solution in every class lattice, identified never excluded;
appears exactly once per lattice (the full state); D2'' satisfied by his strip chain. SAFE.

Pointers: code/{grainlib,explore1,pa_scan,census,emit_grain,images,run_basin76,a40_check_exact}.py;
results/{z0_t,images,pa_scan2,explore1_uniform,a40_exact_report}.json, census_*.json,
pairlp_k4_08_basin_rz*.json; logs/*; certs/grain_k4_08_rc1e-2_rt2e-3.json, grain_trump_tnative_r{5e-4,4e-3}.json.
