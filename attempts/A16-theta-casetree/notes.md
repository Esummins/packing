# A16-theta-casetree — ϑ′ as the node certificate of the case tree (decisive test on finite placement graphs)

Owner: SDP postdoc (A16). 2026-08-19. Status: **done-success** (~5 h; comparison pilot, not a bound on s(11)).

Question (PI). Is the strategy "A13/A14 case tree + ϑ′ (Lovász–Schrijver/Schrijver theta) node certificates" viable?
On ONE finite placement graph per node (comparison of relaxations, NOT a bound on s(11)): for a hypothesis node H,
nodes = grid placements that are admissible under H (A14's row filter: drop placements provably inside a NO-family or
penetrating a fixed core by SAT depth > 2e-3), edges = interior overlap; compute on the induced graph G_H
  ν*_H (point-clique LP = grid version of A14's node LP dual), ϑ′(G_H) (bracket), α(G_H);  budget = 11 − #cores;
node "dead" under a relaxation iff its value < budget.  α ≤ ϑ′ ≤ ν*_H always (same graph).

## 1. Machinery (files; A15's code generalised)

- `graph.py` — A15's grid (D4-invariant, h, Δθ) + seeds; CHANGES: near-duplicate merge (2e-5) so that the group action is
  well defined on seeded sets; seeds may be closed under a SUBGROUP of D4 only (`extra_group`); `d4_action(P, s, gl)` for a
  subgroup.
- `nodes.py` — node catalogue with A14's exact hypothesis semantics (imports A14's `caselp.Box/NoFam/Hyp`, `Hyp.ok_many`
  with EPS_CORE = 2e-3, EPS_ZONE = 2e-3, EPS_TH = 0.3°): N0 root; N1 one corner square fixed exactly (degenerate box
  (0.5,0.5,0°), core = [0,1]² up to 3e-8); N2 four corners fixed exactly; N3a/b/c = A14's alive depth-1 boxes
  [0.5,0.8]²×{[0,30],[30,60],[60,90]}° (A14 inner-core construction `Box.core()`); N4 = four corners + NO side0 zone
  [0.5,1.1]×[1.1,s−1.1]; N5 = NO all four corner zones [0.5,1.1]²; seeds = the node's own A14 LP fractional packing
  (`packing`/state rows with dual y ≥ 0.01; A14 results at 3.84, l1_385 at 3.85; stretched affinely when no run at
  that s exists) + A15's injected root structures (A12 ¼-structure images, A07 dual); LP initial points = A14's atoms.
- `theta_sdp.py` — A15's D4 block-diagonalised ϑ′ SDP generalised to an arbitrary subgroup H ≤ D4 of the node set: H =
  stabiliser of the admissible set inside D4 (computed, not assumed): D4 (root, N2, N5) → 5 blocks; Z2 (N1, N3b: diagonal
  reflection; N4: reflection y ↦ s−y) → 2 blocks; C1 (N3a, N3c) → one N×N block (= plain formulation).  Validated against
  cvxpy/Clarabel full-matrix ϑ′ on small graphs (D4 / Z2 / C1 all agree to 1e-8).  Brackets as in A15: lower bound =
  cleaned primal (+δI) feasible value, upper bound = dual certificate Z = λI − J − Y (+δI) ⇒ ϑ′ ≤ 1 + (λ′−1)/(1−ε).
- `lp_point.py` — A15's point-clique LP with an incremental (warm) HiGHS model and capped arrangement-vertex generation
  (the seeded node LPs are degenerate: the old cold-restart loop took > 3 min per iteration).
- `run_node.py` — driver: stage 1 pure grid → stabiliser H; stage 2 grid + H-closed seeds → admissible set → LP, SDP
  (SCS, time-limited), dual certificate, α (CP-SAT), support sub-SDP (exact ϑ′ on the H-closed support of the approximate
  primal ⇒ tight lower bound), json in results/<tag>.json, log in logs/<tag>.log.

## 2. Runs and results (filled in as they finish; `python table.py` prints the table from results/*.json)

### 2.0 Un-seeded grids are integral (LP = α = 10) — no information there

Pure grids (no injected structure) at s = 3.84/3.85, h = 0.2/Δθ = 10° (N = 1577), h = 0.15/7.5° (N = 3684), h = 0.1/10°
(N = 6049, s = 3.85): the point-clique LP is **10.000 exactly** (integral, support = 10 placements), hence ϑ′ = α = 10 and
nothing can be learned (runs `results/u384_lponly.json`, `u385_lponly.json`, `ulp_*.json`; the h = 0.1/5° grid, N = 12090,
31 M edges, was stopped — HiGHS needs > 10 min per LP solve there and the value was 10.000 as well).  The ¼-weight
fractional structures need exact wall contacts / unit distances that a generic grid cx = s/2 + k·h does not contain;
only seeded grids (A15's construction) show the LP cheat.  Consequently all node runs below are SEEDED (node's own A14
LP packing support + A15's root structures), and the "un-seeded root" rows of the task are reported as LP = ϑ′ = α = 10.

### 2.1 Smoke run (coarse seeded graph, N2 at 3.84, h = 0.4, Δθ = 30°, N = 1463): LP 7.000, ϑ′ ∈ [5.89, 6.60], α = 6
(`results/smoke_N2.json`; SDP 120 s only) — first sign that ϑ′ kills the four-corners node by ≳ 0.4 where the LP sits
exactly at the budget.

### 2.2 Grid LP values at the nodes (h = 0.2, Δθ = 10°, seeded; A14 continuum values in brackets)
3.84: N1 10.000 [10.000]; N2 7.000 [7.000]; N3a/b/c 10.054 / 10.039 / 10.026 [10.11 / 10.12 / 10.19]; N4 6.250 [6.36].
3.85: N1 10.000; N2 7.000; N3a/b/c 10.007 / 10.000 / 10.000 [10.115 / 10.000 / 10.063]; N4 6.333.
So the seeded grids reproduce A14's LP picture (alive exactly at / slightly above the budget at N1, N2, N3; dead by
0.67–0.75 at N4).

### 2.3 Main table (seeded grids h = 0.2, Δθ = 10°; `python table.py` regenerates results/table.md.  (`results/*_scs_xys.npz` etc. — 480 MB — are git-ignored; regenerate with run_node.py.)from results/*.json)

Columns: N = admissible placements (grid + seeds minus exempt), sym = stabiliser of the admissible set in D4 (SDP block
structure), ν*_G = point-clique LP on G_H (bracket ν/maxcov ≤ ν* ≤ ν), ϑ′_G bracket = [max(α, primal-feasible value,
ϑ′ of the support subgraph G[S]) , dual certificate of the big SDP], α_G by CP-SAT (all OPTIMAL).  "ub slack" = dual
certificate − budget (a certified — floating-point eigenvalues — upper bound on ϑ′_G, hence the node is ϑ′-DEAD on this
graph whenever it is < 0).  A15's seeded root values are quoted for N0.

| node | s | N | sym | edges | ν*_G (LP) | ϑ′_G bracket | α_G | budget | LP slack | ϑ′ ub slack | SDP (iters / s, s per iter) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| N0 root (A15 c384, seeded) | 3.84 | 2337 | D4 | 1.11M | 11.000 | [10.376, 10.392] | 10 | 11 | 0.00 | **−0.61** | (A15) |
| N0 root (A15 c385, seeded) | 3.85 | 2229 | D4 | 1.00M | 11.000 | [10.428, 10.483] | 10 | 11 | 0.00 | **−0.52** | (A15) |
| N0 root, UN-seeded (h=0.2/10°, 0.15/7.5°, 0.1/10°) | 3.84, 3.85 | 1577–6049 | D4 | – | 10.000 | = 10 (= α) | 10 | 11 | −1.00 | −1.00 | integral grid, no information (§2.0) |
| N1 one corner fixed | 3.84 | 1494 | Z2 | 0.50M | 10.000 | [9.383, 9.438] | 9 | 10 | 0.00 | **−0.56** | 7325 / 3009 (0.41) |
| N1 one corner fixed | 3.85 | 1494 | Z2 | 0.50M | 10.000 | [9.430, 9.491] | 9 | 10 | 0.00 | **−0.51** | 7175 / 3004 (0.42) |
| N2 four corners fixed | 3.84 | 2177 | D4 | 1.17M | 7.000 | [6.248, 6.617] | 6 | 7 | 0.00 | **−0.38** | 11475 / 2410 (0.21) |
| N2 four corners fixed | 3.85 | 2157 | D4 | 1.14M | 7.000 | [5.904, 6.591] | 6 | 7 | 0.00 | **−0.41** | 11450 / 2412 (0.21) |
| N2 four corners fixed, finer grid h=0.15/7.5° | 3.84 | 3152 | D4 | 2.65M | 7.000 | [see §2.4] | – | 7 | 0.00 | see §2.4 | |
| N3a box [0.5,0.8]²×[0,30]° | 3.84 | 1682 | C1 | 0.63M | 10.054 | [9.457, 9.664] | 9 | 10 | +0.05 | **−0.34** | 2000 / 3029 (1.5) |
| N3b box [0.5,0.8]²×[30,60]° | 3.84 | 1565 | C1 | 0.54M | 10.039 | [9.435, 9.667] | 9 | 10 | +0.04 | **−0.33** | 2400 / 3014 (1.26) |
| N3c box [0.5,0.8]²×[60,90]° | 3.84 | 1573 | C1 | 0.55M | 10.026 | [9.444, 9.608] | 9 | 10 | +0.03 | **−0.39** | 2375 / 3012 (1.27) |
| N3a, richer seeds (all of A14's n2 packing, y ≥ 5e-4) | 3.84 | 1876 | C1 | 0.81M | 10.080 | [see §2.4] | – | 10 | +0.08 | see §2.4 | |
| N3c, richer seeds | 3.84 | 1649 | C1 | 0.60M | 10.055 | [see §2.4] | – | 10 | +0.06 | see §2.4 | |
| N3a box [0.5,0.8]²×[0,30]° | 3.85 | 1603 | C1 | 0.57M | 10.007 | [see §2.4, 9.529] | 9 | 10 | +0.01 | **−0.47** | 2225 / 3032 (1.36) |
| N3b box [0.5,0.8]²×[30,60]° | 3.85 | 1515 | Z2 | 0.50M | 10.000 | [9.445, 9.520] | 9 | 10 | 0.00 | **−0.48** | see json |
| N3c box [0.5,0.8]²×[60,90]° | 3.85 | 1593 | C1 | 0.55M | 10.000 | [9.494, 9.640] | 9 | 10 | 0.00 | **−0.36** | see json |
| N3d off-corner box [0.5,0.8]×[0.8,1.1]×[30,60]° (A14 node 6, LP 10.04 cont.) | 3.84 | 1510 | C1 | 0.52M | 9.317 | [see §2.4] | – | 10 | −0.68 | see §2.4 | |
| N3e off-corner box [0.5,0.8]×[0.8,1.1]×[0,30]° (A14 node 5, LP 9.87–10.00 cont.) | 3.84 | 1557 | C1 | 0.55M | 9.761 | [see §2.4] | – | 10 | −0.24 | see §2.4 | |
| N4 four corners + NO side0 | 3.84 | 974 | Z2 | 0.29M | 6.250 | [6.000, 6.004] | 6 | 7 | −0.75 | **−1.00** (ϑ′ = α = 6) | 17950 / 3004 (0.17) |
| N4 four corners + NO side0 | 3.85 | 986 | Z2 | 0.29M | 6.333 | [6.000, 6.009] | 6 | 7 | −0.67 | **−0.99** | 17100 / 3005 (0.18) |

Notes. (i) The grid LP values reproduce A14's continuum picture (N1, N2 exactly at the budget with the ¼-structure;
N3 alive by a few hundredths on the grid, +0.11…+0.19 in the continuum; N4 dead by 0.7).  (ii) The big C1 SDPs
(N ≈ 1600, one 1600×1600 block) reach only 2000–2400 SCS iterations in 50 min (1.3–1.5 s per iteration, all in the
eigendecomposition); their PRIMAL is useless (lower bounds 5–7) but the dual certificate is already accurate (res_dual
≤ 1e-7; the support sub-SDP, exact to 1e-4 on 120–170 nodes, lands 0.15–0.2 below it).  (iii) α_G = budget − 1 at every
hypothesis node on these grids (9 / 6), i.e. the discretised graph does not even contain an integral packing meeting the
budget; the LP does not notice (fractional ¼-structures), ϑ′ sits ≈ 0.4–0.6 above α and ≈ 0.35–0.6 below the LP — the
same split as at A15's root (α 10 / ϑ′ 10.4 / LP 11).  (iv) Dual certificates Z at the nodes (n2_384: N = 2177, 7 / 30 /
327 eigenvalues > 10 % / 1 % / 0.1 % of max; n1_384: 9 / 41 / 832; non-edge entries: max −1.0000, mean −1.09, 75–82 %
strictly slack (< −1.01)) — same low-effective-rank structure as at the root (A15 §2.4).

## 3. Interpretation for the PI (a)–(e)

Standing caveat (as in A15): all numbers are relaxation values on FINITE induced subgraphs of the continuum conflict
graph; ϑ′_G ≤ ϑ′_cont and α_G ≤ α_cont (the seeded grids carry the LP's structures, so ν*_G ≈ ν*_cont, but a ϑ′_G below
the budget is evidence about the relaxation's strength, not a proof that the node is dead in the continuum).

**(a) Does ϑ′ kill N2 (four corners fixed exactly, LP = 7.000 = budget), and by how much?  YES.**  On the seeded grids
ϑ′ ≤ 6.617 (3.84) and ≤ 6.591 (3.85) by certified dual certificates, i.e. at least 0.38–0.41 below the budget (and below
the LP, which is exactly 7.000 on the same graphs); the tight value (support sub-SDP, 744–924 nodes, not fully converged)
is ϑ′_G ≈ 6.25–6.46 at 3.84, i.e. the margin is ≈ 0.5–0.75; α_G = 6.  The coarse smoke graph (h = 0.4, Δθ = 30°, N = 1463)
gives the same picture (ϑ′ ∈ [5.89, 6.60]), and the finer grid h = 0.15 / 7.5° (N = 3152): see §2.4.  So the node type that
stalls the LP tree (the ¼-weight structure with all corners fixed) is killed by ϑ′ with a margin of the same size as the
root gap (0.4–0.6 = about half of the LP's unit integrality gap).  Likewise N1 (one corner fixed exactly, LP = 10.000 =
budget): ϑ′ ∈ [9.38, 9.44] at 3.84 and [9.43, 9.49] at 3.85 — dead by ≥ 0.5.

**(b) N3 (A14's three alive depth-1 on-corner boxes, LP slack +0.1…+0.2 in the continuum, +0.03…+0.05 on the grids):
ϑ′'s slack IS negative: −0.34 / −0.33 / −0.39 (certified upper bounds) and −0.54 / −0.57 / −0.56 (tight support values) at
3.84; −0.47 / −0.48 / −0.36 (ub) at 3.85.**  With richer seeding (the whole A14 packing, grid LP 10.08 / 10.06) see §2.4.
The off-corner boxes N3d/N3e (LP dead by 0.0…−0.13 in the continuum at 1e-4, and 0.00 at the 3e-3 certification shrink —
the "not certifiable" leaves of A14) are LP-dead already on these grids (9.32, 9.76; the 3e-3-shrunk seeds overlap in the
exact graph) and ϑ′ is lower still (§2.4).  N4 (corners + NO side0): ϑ′ = α = 6 exactly (integral!) vs LP 6.25–6.33, i.e.
once a side zone is empty the SDP is integral on the grid — sanity confirmed (ϑ′ ≤ LP there too, by ≈ 0.3).

**(c) Extrapolated tree size with ϑ′ node certificates (A14 branching: NO child + 12 YES boxes per corner level).**
A14's first level at 3.84: NO(all corners) LP-dead by 1.4 (ϑ′ ≤ LP ⇒ dead); 9 off-corner/far boxes LP ≤ 10.04 (dead or
within 0.04 of the budget) ⇒ ϑ′ ≤ 9.7 on the grids (ϑ′ − LP ≈ −0.3…−0.6 at every node tested; N3d/N3e confirm, §2.4);
the 3 on-corner boxes: ϑ′-dead by 0.33–0.57.  So, IF the continuum ϑ′ at each node behaves like the grid ϑ′ (gap
ϑ′ − LP ≈ −0.3…−0.6 preserved; the grid LP is itself 0.06–0.15 below the continuum LP at N3, so an honest margin estimate
is 0.2–0.45 rather than 0.35–0.57), **the whole tree at 3.84 is root + 13 leaves, and at 3.85 the same 14 nodes** (first
level at 3.85: root 11.07, NO corners 9.56, on-corner boxes 10.00…10.12 LP vs ϑ′ ≤ 9.53–9.64).  Compare A14's estimate of
10⁵–10⁶ node LPs for the same job: the killing power that the LP finds only in empty side zones (≈ 0.6 per zone, reached
at depth ≥ 6) is available to ϑ′ at depth 1 (and at the exact-corner nodes where the LP can NEVER kill, A14 §3c).  Two
further remarks: (i) the root itself may not need a tree: A15's seeded-grid root values 10.38 / 10.45 / 10.45–10.64 at
3.84 / 3.85 / 3.87 are < 11 — if the continuum root ϑ′ stays below 11 the tree has one node; since α_cont = 10 for all
s < 3.877 and ϑ′ − α ≈ 0.4–0.6 on every graph tested, the decisive unknown is how fast the continuum ϑ′ − α gap grows as
s → 3.877 (no sign of growth between N = 2229 and 3750 at 3.85 in A15, nor between N = 2177 and 3152 at N2 here, §2.4);
(ii) the certification overhead of the LP tree (0.1–0.25 per node for the 3e-3 shrink + 3 % weight margin) has a kernel
analogue (robustness margins on K(x,x) ≤ λ−1 and K(x,y) ≤ −1) which would eat a similar share of a 0.3–0.6 margin — still
positive, unlike the LP's +0.04.  Where the tree is needed at all, its depth-1 branching factor 13 with ≈ 0 survivors
per level (instead of 9) makes depth 2 (≈ 170 nodes) the worst plausible case at 3.84/3.85; the number of nodes is
then 14–200, not 10⁵–10⁶.

**(d) Cost per node SDP and what would make it tractable.**  Measured (SCS, one core + 2 BLAS threads, h = 0.2/10° grids):
D4-symmetric nodes N ≈ 2200 (5 blocks ≈ 270–540, 0.3 M pair orbits): 0.21 s/iteration, 11.5k iterations in 40 min — the
dual certificate is then within ≈ 0.15 of the tight value (6.62 vs 6.25–6.46); Z2 nodes N ≈ 1500 (two ≈ 750-blocks, 1.1 M
pair orbits): 0.41 s/it, 7.3k it in 50 min, dual certificate within 0.06 of the tight value; C1 nodes N ≈ 1600 (one
1600×1600 block, 1.4 M pairs): 1.3–1.5 s/it (eigendecomposition-bound), only 2000–2400 it in 50 min, primal worthless
(5–7) but dual certificate within 0.15–0.2 of the tight value (9.66 vs 9.46); support sub-SDPs (120–900 nodes): 3–20 min to
1e-4 (C1 150-node graphs: 140k iterations in 20 min — SCS is slow even there); α by CP-SAT: ≤ 25 s.  Per node this is
1–1.5 h of wall time for a verdict with margin ≥ 0.3, dominated by the SDP; 14 nodes = one afternoon on 12 processes.
To scale (finer grids 10⁴ nodes, or many nodes): (1) the deliverable is the DUAL certificate, which SCS gets early
(res_dual 1e-8 after 2000 iterations) — a dual-side method (cutting planes on the pair constraints: 75–82 % of the
non-edge constraints are strictly slack, Z_ij mean −1.09, max −1.0000; or a low-rank dual ansatz Z = λI − J − Y with Y
supported on the ≈ 10–50-dimensional dominant eigenspace) would cut the cost by 10–50×; (2) the PSD projection is the
bottleneck at C1 nodes (N³): exploit the residual symmetry wherever it exists (N3b at 3.85 was Z2: 0.4 s/it vs 1.3) and
keep N ≲ 1500 by seeding only with the node's own LP support; (3) a better first-order/AL solver (SDPNAL+, or
Burer–Monteiro for the primal with rank ≈ 100–900 observed) for the big instances.

**(e) Rigorous version (if ϑ′ kills N2/N3 decisively — it does on the grids).**  Node certificate = PSD kernel K_H on the
placement space with (i) K_H(x,x) ≤ λ−1 for every ADMISSIBLE x (not provably exempt: disjoint from every core, not in a
NO-family) and (ii) K_H(x,y) ≤ −1 for every pair of DISJOINT admissible placements; then for a packing satisfying H the
≥ budget non-witness squares are pairwise disjoint, admissible, and 0 ≤ Σ_ij K(x_i,x_j) ≤ n′(λ−1) − n′(n′−1) gives
n′ ≤ λ < budget: contradiction (this is A13's node-death lemma with "μ(Q) ≥ 1" replaced by the kernel inequality; the
exemption semantics is exactly verify_case.py's: a parameter box is exempt iff provably inside a NO-family or provably
meeting a core, and K is constrained only on non-exempt boxes / pairs of non-exempt boxes).  Kernel class (A15 §4): the
node's LP measure atoms p (a few hundred) give indicator features 1[p ∈ Q(x)]/m(x) for which the LP certificate itself is a
kernel with λ = τ; add cross terms M_pq (the SDP variable is M ⪰ 0 over the atom set plus ≈ 50 smooth D4/C1 features — the
grid duals here have 30–40 eigenvalues > 1 % and 300–900 > 0.1 % of the maximum, so a few hundred features should
reproduce the grid certificate); the SDP is then over a matrix of size (#atoms + #smooth) ≈ 300–600 with cutting planes for
(i)–(ii) generated by the verifier's own box B&B (holes = violated boxes, as in the A07/A14 loop).  Verification: K is
piecewise constant in (x, y) on the cells of the atom arrangement (A07/A08 cell enumeration in (cx,cy,θ) with exact rational
cos/sin enclosures), so (i) is a 3-D exact B&B exactly like verify_case.py (with λ−1 in place of 1 and a quadratic form in
place of a sum — the smooth part needs interval enclosures), and (ii) is a finite check over PAIRS of cells restricted to
disjoint pairs (the A15 §4 reduction; the smooth part again by intervals, and the constant part exactly rational); exact
PSD of M by rational LDLᵀ.  Work estimate: kernel SDP with row generation 2–3 weeks (the SDP machinery is here; the
continuum row oracle is the A14 oracle with the kernel in place of the mass), exact verifier extension (cells + pairwise
table + exemptions) 1–2 weeks, then the 14-node tree at 3.84 (and 3.85) runs in days; the Lean bridge (kernel inequality ⇒
Theorem, cell checker) is a separate formalisation effort comparable to the one already done for the measure checker.
The two risks: (R1) the continuum ϑ′ at the nodes may sit higher than the grid ϑ′ (grid = lower bound) — mitigated by the
refinement tests (A15 f385, §2.4 here) showing no upward drift, but only a continuum kernel certificate settles it;
(R2) a kernel class of a few hundred features may not reach the continuum ϑ′ — the LP-atom indicator basis guarantees at
least λ = τ (the LP value), so the class can only improve on the LP; the question is by how much.

### 2.4 Robustness checks: finer grid, richer seeds, off-corner boxes, s = 3.87

| run | change vs §2.3 | N | LP | theta' bracket [tight lb, cert ub] | alpha | budget | theta' ub slack |
|---|---|---|---|---|---|---|---|
| n2_384_fine | N2 at 3.84, grid h = 0.15 / 7.5 deg | 3152 | 7.000 | [6.436, 6.674] | 6 | 7 | -0.33 |
| n3a_384_rich | N3a, seeds = ALL of A14's n2/n2_v3 packing (y >= 5e-4) | 1876 | 10.080 | [9.498, 9.756] | 9 | 10 | -0.24 |
| n3c_384_rich | N3c, richer seeds | 1649 | 10.055 | [9.447, 9.653] | 9 | 10 | -0.35 |
| n3d_384 | off-corner box [0.5,0.8]x[0.8,1.1]x[30,60] (A14 node 6: LP 10.04 at 3e-3, "not certifiable") | 1510 | 9.317 | [9.000, 9.140] | 9 | 10 | -0.86 |
| n3e_384 | off-corner box [0.5,0.8]x[0.8,1.1]x[0,30] (A14 node 5) | 1557 | 9.761 | [9.236, 9.413] | 9 | 10 | -0.59 |

Reading: (i) refining the N2 grid (2177 -> 3152 nodes, 2.65 M edges) does not move theta' up (tight 6.44-6.45 vs
6.25-6.46; cert ub 6.67 vs 6.62 only because 50 min of SCS converges less at the larger size) — same stability as
A15's f385 test at the root; (ii) richer seeding raises the grid LP (10.05 -> 10.08) but theta' stays ~0.5 below
budget (9.50 / 9.45 tight): the extra 1/4-structure mass is exactly what theta' refuses to carry; (iii) the A14
"not certifiable" off-corner leaves are theta'-dead by 0.6-0.9 — with theta' the certification-margin problem
(A14 §4a: slack 0.00 at the 3e-3 shrink) disappears at these nodes.

### 2.5 Consolidated final table (authoritative; generated from results/*.json — supersedes the running entries above)

theta' bracket = [max(alpha, feasible-B value, tight support-sub-SDP lower bound), certified dual-certificate upper
bound on the big SDP].  "ub slack" = certified upper bound - budget: node is theta'-dead on this graph iff < 0.
All graphs seeded (node's own A14 LP packing + A12 1/4-structures; h = 0.2, dtheta = 10 deg unless stated).

| node | s | N | sym | LP | theta' bracket | alpha | budget | LP slack | theta' ub slack |
|---|---|---|---|---|---|---|---|---|---|
| N1 one corner exact  | 3.84 | 1494 | Z2 | 10.0000 | [9.383, 9.438] | 9 | 10 |  0.00 | **-0.56** |
| N1                   | 3.85 | 1494 | Z2 | 10.0000 | [9.430, 9.491] | 9 | 10 |  0.00 | **-0.51** |
| N1                   | 3.87 | 1520 | Z2 | 10.0000 | [9.447, 9.480] | 9 | 10 |  0.00 | **-0.52** |
| N2 four corners exact| 3.84 | 2177 | D4 |  7.0000 | [6.248, 6.617] | 6 |  7 |  0.00 | **-0.38** |
| N2, finer h=0.15/7.5 | 3.84 | 3152 | D4 |  7.0000 | [6.436, 6.674] | 6 |  7 |  0.00 | **-0.33** |
| N2                   | 3.85 | 2157 | D4 |  7.0000 | [6.000, 6.591] | 6 |  7 |  0.00 | **-0.41** |
| N2                   | 3.87 | 2293 | D4 |  7.0000 | [6.370, 6.509] | 6 |  7 |  0.00 | **-0.49** |
| N3a [0,30]           | 3.84 | 1682 | C1 | 10.0544 | [9.457, 9.664] | 9 | 10 | +0.05 | **-0.34** |
| N3a, rich seeds      | 3.84 | 1876 | C1 | 10.0795 | [9.498, 9.756] | 9 | 10 | +0.08 | **-0.24** |
| N3a                  | 3.85 | 1603 | C1 | 10.0073 | [9.323, 9.529] | 9 | 10 | +0.01 | **-0.47** |
| N3b [30,60]          | 3.84 | 1565 | C1 | 10.0391 | [9.435, 9.667] | 9 | 10 | +0.04 | **-0.33** |
| N3b                  | 3.85 | 1515 | Z2 | 10.0000 | [9.445, 9.520] | 9 | 10 |  0.00 | **-0.48** |
| N3c [60,90]          | 3.84 | 1573 | C1 | 10.0264 | [9.444, 9.608] | 9 | 10 | +0.03 | **-0.39** |
| N3c, rich seeds      | 3.84 | 1649 | C1 | 10.0551 | [9.447, 9.653] | 9 | 10 | +0.06 | **-0.35** |
| N3c                  | 3.85 | 1593 | C1 | 10.0000 | [9.494, 9.640] | 9 | 10 |  0.00 | **-0.36** |
| N3d off-corner [30,60]| 3.84 | 1510 | C1 |  9.3172 | [9.000, 9.140] | 9 | 10 | -0.68 | **-0.86** |
| N3e off-corner [0,30] | 3.84 | 1557 | C1 |  9.7612 | [9.236, 9.413] | 9 | 10 | -0.24 | **-0.59** |
| N4 corners + NO side0| 3.84 |  974 | Z2 |  6.2500 | [6.000, 6.004] | 6 |  7 | -0.75 | **-1.00** |
| N4                   | 3.85 |  986 | Z2 |  6.3333 | [6.000, 6.009] | 6 |  7 | -0.67 | **-0.99** |

## 4. Structure of the SDP optimum at the nodes (what theta' refuses to carry)

- N2 (four corners fixed, 3.84): the SDP diagonal x = theta' diag(B) has NO tilted 1/4-pinwheel: wall uprights carry
  3.57 (200 placements smeared along the walls: e.g. (1.50, 3.34, 0), (2.34, 0.5, 0) at 0.125 each), interior tilted
  2.39, interior uprights 0.03 — total 6.72 (unconverged; tight 6.25-6.46) vs the LP's 28 x 1/4 structure (4 side pairs
  + 8-pinwheel + 4 uprights = 7.000).  As at the root (A15 §2.3), the SDP keeps the Trump-like shape but pays
  ~0.5-0.75 for the odd-cycle structure of the 1/4-cheat.
- N4 (corners + NO side0): x is INTEGRAL-like: 6 units split over symmetric pairs (2.34,0.5)+(2.34,3.34) 0.57+0.16,
  mid-tilt pair at (1.39,1.35,25)/(1.39,2.49,65) 0.36 each, etc. summing to 6.000 = alpha: theta' = alpha exactly.
- N3a: LP support is corner-anchored uprights (corners 1.0/0.95, wall 0.3-0.5); theta' support has wall mass 7.8 of
  10.2 — the missing ~0.5 vs the LP is again the side-zone 1/4 mass.
- Dual certificates: diag = lam - 1 exactly, non-edge entries max -1.0000 (tight), mean -1.09, 75-82 % strictly slack;
  spectra 7-10 eigenvalues > 10 % of max, 30-45 > 1 %: a kernel with a few hundred features reproduces the node
  certificates (input to (e)).

## 5. Files / reproduce

`python run_node.py --node N2 --s 3.84 --tag n2_384 --sdp_time 2400` (grid + admissible filter + LP + SDP + support
sub-SDP + alpha; `--unseeded`, `--a15_mode s`, `--ymin 5e-4`, `--h 0.15 --dtheta 7.5`); nodes.py = the catalogue
(N0 root, N1/N2 exact corners, N3a-c on-corner boxes, N3d/e off-corner boxes, N4(b) corners+NO sides, N5(s) NO zones);
`python table.py` regenerates results/table.md.  (`results/*_scs_xys.npz` etc. — 480 MB — are git-ignored; regenerate with run_node.py.)  Results: results/<tag>.json (all numbers incl. brackets, supports,
cert diagnostics), <tag>_graph.npz (P, subgroup action, kidx), <tag>_B_diag.npy, <tag>_scs_xys.npz (SCS warm-start
state), <tag>_lp_x.npy, <tag>_sub_nodes.npy; logs/<tag>.log (+ .out with raw SCS trace).  Independent verification of
two dual certificates (n2_384, n3a_384) by full-matrix reconstruction + Cholesky: PASS (see chat log / §2.3 note iv).
Dependencies as A15 (numpy/scipy/highspy/ortools/scs).
