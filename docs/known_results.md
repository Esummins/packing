# What is actually established (human-maintained ledger — checklist R5)

Status key: **LEAN** = Lean theorem (axioms at most propext/Classical.choice/Quot.sound + native_decide) ·
**CERT** = exact certificate checked by an exact verifier (verifier soundness Lean-proved where noted) ·
**PROSE** = written proof in docs/proofs/ or attempt notes, not yet formalised.
Kill certificates are at s0 = 969271/250000 unless "window" is stated; window = [3.82, s0].
Maintained by the advisor at close-out commits; last update 2026-09-03. Corrections welcome — this
file is the record of truth for claims, LOG.md is the record of events.

## A. The number
1. LEAN  s(11) >= 3.82 (`s_eleven_ge_382`: measure certificate + formalised bridge).
2. LEAN  s(11) <= s-hat: Trump's packing exists at side s-hat exactly (`trump_packs_at_shatA22`, `basin`
   theorems; modulo the single axiom `a22_exact_structure` = A22's certified contact structure, derived
   in Lean from the structure alone by A79).
3. LEAN  s-hat is the SECOND real root of s^8-20s^7+178s^6-842s^5+1923s^4-496s^3-6754s^2+12420s-6865;
   the octic has exactly two real roots (Sturm certificate; `shat_spec`).
4. CERT  Every coordinate of Trump's configuration z-hat lies in Q(t-hat), degree 8; minimal polynomials
   derived (A69). A03's "degree-7 coordinate" annotations were junk.
5. LEAN  s_A22 = s-hat (CIDL cofactor identity, `shatA22_eq_shat`).

## B. Near Trump
6. LEAN  BASIN: every packing within rBasin = 3/2000 (t-coords; universal certificate radius 3689/10^6
   theta-coords) of Trump mod symmetry has sigma >= s-hat, equality only at Trump (`a36_basin`).
   Stratum-blind. ("Close enough to Trump IS Trump.")
7. LEAN  Krawczyk: unique contact solution in the A22 box; Trump is a strict local optimum (`krawczyk_sound`,
   `a22_optimal`).
8. CERT  THEOREM U: remove any one of Trump's squares; the other ten force it into its slot (11 certificates,
   Sigma w = 0; verifier soundness LEAN; certificates replayed in Lean).
9. CERT  Trump's contact structure is rigid with pins out to (1e-2 centre, 2e-3 tilt) (A76); the hinge grains
   (strip flush pair degraded to a single-corner contact) are the first flexible neighbours.
10. PROSE/CERT  Grain lemmas G-R (local completeness by construction), K, DF (drain-flex), D2'' (A76).

## C. Stratification by simple squares
11. LEAN  Census: exactly 1110 skeleton tuples / 163 D4 classes under the Young-form definition
    (`Census.lean`; two independent enumerations A53/A72 agree exactly; kernel-checked).
12. LEAN  Every selected (k-maximal, slide-stuck) minimiser's skeleton lies in exactly one class (`stratify`);
    K1: kills climb containment, aliveness descends.
13. CERT  AT MOST 5 SIMPLE SQUARES: all 33 k=6 classes killed at s0 (hence all k >= 6 by K1). Window
    coverage: 41/52 scoreboard rows full-window, 9 converting (A61), 2 slivers.
14. CERT  k=5: 19 of 22 classes killed; alive: trump5 (Trump's own), k5_11, k5_16 — the latter two killed at
    s0 by sub-stratification trees (A57), window grid G1 in progress.
15. LEAN+CERT  k<=4: 8 of 14 k=4 classes killed, 1 of 6 k=3 (k3_00); the 16 survivors (6 k4 + 10 k<=3)
    are exactly the sub-skeletons of trump5 and are PROVABLY unkillable by single-square certificates
    (A55 sharpness + K1): Trump is a feasible point of each monotone hypothesis.
16. LEAN  Verifier soundness: measure checker + driver, case-LP checker, 4-D parametric checker,
    alivewitness, D4 reduction — all Lean theorems. Corpus replays COMPLETE for the fixed corpora
    (A78 T5, 2026-09-03): measure (3.82), Theorem U (11/11), P1 (1/1), K61 (61/61), TRAP (6/6) — 73
    certificates by native_decide, 9.79 h Lean wall, axiom audit clean; A57/A60 corpora priced multi-day.
16b. LEAN  ADDENDUM (A126, 2026-09-07): the LOCAL certificate joins the replayed corpora, arithmetic half
    first. `SatInterior.sat_selection_thm` retires A119's ONE project axiom (Lemma SAT for INTERIORS is now a
    theorem from `CaseSat.sat_squares` by an EXPLICIT shrink `λ = (M/B+1)/2` — no limit, no subsequence);
    `LocalCert.checkLeaf_sound` is a reflected weak-duality checker over a certificate leaf, proved once, and
    `LocalCertS07`/`LocalCertS02` run it by ONE `native_decide` each on ALL the dead leaves of two of A119's
    neighbourhoods — S07 (0.1, 40°): 2 302 leaves / 746 infeasibility rays / 27 363 rows / 101 629 nonzero
    coefficients, 22 s + 19 s; S02 (0.2, 10°): 32 570 / 5 782 / 504 404 / 1 977 332, 40 s + 67 s. `localDead_s07`
    / `localDead_s02` are Theorem LOCAL for those `N` modulo ONE named hypothesis, `CertCover` (Lemma COVER +
    Lemma RELAX), whose whole residue is a certified rational-interval kernel for cos/sin/π — A119's
    `exactiv.py` in Lean — or, cheaper, a certificate re-emitted in `t = tan(θ/2)`, where cos and sin are
    RATIONAL. The leaf data is emitted as ONE STRING PER LEAF: at 10⁵–10⁶ coefficients the ELABORATOR, not the
    kernel, is the wall.
16b'. LEAN  ADDENDUM to 16b (A133, 2026-09-07): the local certificate RE-EMITTED with the tilt in
    `t = tan(θ/2)`, Lean's own tilt parameter — A126's Route B, carried out. `cos θ = (1−t²)/(1+t²)` and
    `sin θ = 2t/(1+t²)` are RATIONAL, so every enclosure a local certificate needs is the exact range of a
    rational function over a rational cell: **no π, no Taylor series, no dyadic interval kernel anywhere in
    the pipeline**, and `w = |cos Δ| + |sin Δ|` is bounded below by its two SMOOTH branches `cos Δ ± sin Δ`
    on the whole cell, which retires the one step (`exactiv.kink_in`, locating the `π/2` kink) where a
    rigorous `π` was unavoidable. All SEVEN of A119's neighbourhoods and THREE of A125's S33 re-emit DEAD and
    re-check VALID under an independent rational checker with no early return — S07 (0.1, 40°) 2 140 leaves
    against A119's 2 302, S02 (0.2, 10°) 16 406 against 32 570; 10 certificates, 25.4 MB, 8.5 min of
    generation, and every one of the 610 000 emitted rows verified IMPLIED by a row the checker derived
    itself. The Lean side (`LocalCertT.lean`, axiom-clean, `lake build` 18.5 s) has the exact `cosT`/`sinT`
    enclosures, the kink-free `w` branches, a decidable POSITIVITY CERTIFICATE
    (`p = Σ c_k (X−a)^k (b−X)^{n−k}`, `c_k ≥ 0`) that replaces the trigonometric kernel outright, and (C1)
    of `CertCover` — the tilt cover — DISCHARGED. `CertCover` itself is NOT yet discharged: (C2) the
    selection cover, (C3) Lemma RELAX and (C4) the variable map remain, but they are now pure reflection over
    rational data with no transcendental content, priced in
    `attempts/A133-tan-half-emission/notes/lean.md`. Second effect, easy to miss: the certificate's LP tilt
    variable is now Lean's own `t`, so the `arctan` step that would have sat between `LocalHyp` and any
    θ-certificate — whatever the quality of the trig kernel — is gone.
16b''. LEAN  ADDENDUM to 16b' (A134, 2026-09-07): **all three remaining pieces of `CertCover` are now
    theorems**, and the certificate carries the positivity certificates the kernel needs.
    `LocalCertT2.lean` (36 theorems, `lake build` 19.5 s, roster `[propext, Classical.choice, Quot.sound]`
    on every one — no project axiom, no `native_decide`, no `sorry`) adds: **(C2)** `selectionOk_sound`, the
    selection cover, decided by an exact rational interval enclosure of `g_σ` on the cell (in `t` the only
    widening is one interval multiplication — `cosT`/`sinT` ranges are the ENDPOINT values, and `w` is
    bounded below by the maximum of its two smooth branches, so the `π/2` kink and hence `π` never appear);
    **(C3)** Lemma RELAX for both row families — `relax_wall` from `set_subset_container_iff` and
    `relax_selection` from the chain `1/2 + W_lb/2 ≤ 1/2 + w/2 ≤ Proj = P·C + Q·S ≤ (P + corr) + U`, with
    every ingredient proved (`axis_decomp_t` is in `t` an ALGEBRAIC IDENTITY, one `linear_combination`
    against `cos²+sin²=1` — the angle, and any `arctan`, are gone from the derivation as well as from the
    variable); **(C4)** `localHyp_bodies`, one square per body with box membership, container containment,
    tilt range and PAIRWISE INTERIOR-DISJOINTNESS. On the generator side `gen_local_t2.py` emits format
    `local-cert-t-v2` = A133's plus a `pcert` field: per envelope, the nonnegative Bernstein coefficient
    lists `posCheck` consumes, as a CHAIN of pieces (`posChain` / `posGrid`, with `substX0`/`substY0` for a
    pin's collapsed tilt cell). Measured cost of replacing the checker's Sturm argument by the same
    Bernstein form the kernel can run: **zero** — every envelope of all four families certifies at depth 0,
    one piece, on both re-emitted certificates, so trees, leaves, rows and certified minima are IDENTICAL to
    A133's. One gap was found and closed on the CERTIFICATE side: Lemma RELAX also needs `S_lo`, `S_hi` (the
    McCormick corners) and `K = max(1 − cos φ)`, which A133's Python checker recomputed and Lean cannot —
    now emitted with certificates. Both re-emitted certificates are VALID under an independent checker that
    runs A133's whole checker unchanged AND verifies the new field from the LEAN definitions (S07 (0.1, 40°)
    7.2 s, S02 (0.2, 10°) 76 s), and Lean's own `posChain`/`posGrid` accept the emitted `pcert` by
    `native_decide` (36 s and 81 s). **`certCover_s07` and hence `localDead_s07_t` are still NOT obtained**;
    the residue is bookkeeping of four named kinds (the reflected tree walk, the reflected ROW BUILDER with
    the outward-quantisation step, the variable INDEX map, the leaf data) and — the point of the audit —
    **no missing library lemma**: `attempts/A134-certcover-close/notes/lean.md`. A126's elaborator wall
    recurs verbatim (one 336-entry list literal times out at `isDefEq`) and A126's batching fixes it.
16a. CAVEAT (A88, 2026-09-03): A31's contact-type menu omits same-class corner-corner point kisses (Trump
    has one); planarity (L4) is FALSE on the ACTIVE contact graph when squares kiss at a point. Counts over
    the kiss-free SUPPORT graph stand; no proof step may assume planarity of the active graph. The
    flush-ruler cap (Lemma R) is side-dependent: apply the cap for the side in question, not s0's.

## D. Structure of minimisers
17. LEAN  Attainment: s(11) is a minimum.
18. PROSE Wall-to-wall contact chain: every minimiser has a chain of contacts from one wall to the opposite
    wall (L6 / D2''); hence >= 2 wall contacts on a pair of opposite walls, loaded (L7). Flushness NOT forced.
19. CERT  Corner-zone occupancy: every 11-packing at side <= 3.84 has a corner-zone square (A13/A14);
    corner-zone and side-zone squares exist at <= 3.88 (A21).
20. PROSE Near-flush exclusion (A50): no spanning chain has all tilts strictly in (0, theta*) with
    theta* = 1.73465 deg (root of 1969271t^2 + 2000000t - 30729); flush rulers have length <= 5; a 5-ruler
    forces the remaining tilts into [20.77, 69.23] deg; tilt pinning yields finite algebraic menus.
21. CERT  Thin flush-free branch (A47): spans quantise to o*sqrt2 + r; the only window value 2*sqrt2 + 1 is
    killed by an exception certificate.
22. LEAN  Teleport/exchange lemma CC-2 (`teleport_packing`); PROSE clear-corner crowding (A58): every clear
    corner of a k<=3 minimiser has >= 2 non-simple squares meeting its corner box; k=0: >= 8 of 11 squares
    corner-tied; Trump is teleport-extremal.
23. LEAN  Zone-assignment collapse N1; single-corner transfer M1; logic-kill rules T5/T11.
24. PROSE Index identity m = 3k + 1 + sigma - d; rigid => Maxwell (A44).
25. CERT  Trump saturates his own class's crowd threshold exactly (load 2.00; A65) — the mechanism of
    protection.
26. LEAN  lambda-dilation bridge (interior-disjoint minimisers vs closed-disjoint certificate families) incl.
    the NO-family clause; theta<->t transfer with sharp constant; cover invariance (PROSE, A63).
26a. EXACT The second-best known packing (A108, 2026-09-06): 11 unit squares fit in side exactly
    s* = 2 + 4*sqrt(2)/3 = (6 + 4*sqrt(2))/3 = 3.885618083164 = s-hat + 0.0085345, with every coordinate in
    Q(sqrt 2) and all five tilted squares at exactly 45 deg; class k6_07 = trump5 + BL(0,2) (Trump with its
    disturbed upright placed in its slot). Proof: 99 SAT/containment gaps as a + b*sqrt2, 0 violations, 24 exact
    zeros; interval endpoint certificate (250-bit, eps 1e-9). Separate local minimum from Trump (straight-segment
    barrier +0.032; best common-tilt path crests at 41.60 deg, +0.0011 over s*); not first-order rigid (one
    rattler, 3 flexes); Fritz-John fails at first order structurally (a 45-deg square on a wall has zero
    first-order torque) so minimality is second order. Found by drawing the LP dual support at A57/A60's alive
    nodes (docs/shadows.md S07). Not in the window: irrelevant to the proof, relevant to the paper and to
    higher n (a closed-form 45-degree grain family). Figure docs/residue_map/s07_vs_trump.svg.
26b. PROSE+EXACT The chain menu (A110, docs/proofs/grain_flood.md): with u = cos(theta) + sin(theta), the four
    wall-to-wall chain formulas Lambda = 2 + 4u/(u^2+1) (ladder), Y (column), D = 2 + (2 + cos theta)/u (diagonal),
    F_T = 2 + (2 + sin theta)/u (gap) give the side of the corresponding grain as a function of the common tilt.
    Trump, S07 and S02 are kink minima of this menu: S07 = Lambda meets Y at 45 deg (2 + 4 sqrt2/3); S02 = Lambda
    meets D at sin cos = 2 sin - 1 (48.43512 deg, 3.886746029); Trump = the gap chain, Corollary TRUMP-GAP:
    s-hat = 2 + (2 + sin theta_T)/(cos theta_T + sin theta_T) at Trump's tilt, verified to 40 digits against A22's
    exact data. S07's boundary into Trump's grain is at sin cos = 2 cos - 1 (41.56488 deg), crest exactly S02's
    value. Lemmas GRAIN-LP (side minimum at fixed tilts/selection is an LP whose dual is a load path), INHERIT
    (formula survives unloaded contact changes), CONT (s_min continuous in the tilts). GRAIN-FLOOD as a box kill is
    circular (the hypothesis is the class kill); the sound consumer is a conflict row (GRAIN-ROW) inside the node LP.

26c. PROSE Lemma TC, tilt coherence (PI, 2026-09-06; verified numerically to 1e-4 over 0-45 deg): two interior-
    disjoint unit squares with centre distance c and tilt difference D (mod 90 deg) satisfy (1 + cos D + sin D)/2
    <= c, i.e. centres within 1.05 force |D| <= 6.06 deg, within 1.10 force |D| <= 13.05 deg, within 1.207 force
    |D| <= 44 deg; equality is edge-to-edge flush at D = 0. Consequences: (i) a grain's touching members share a
    tilt to within D(c) — the common-tilt structure of Trump, S02, S07 is forced, not incidental; (ii) an LP row
    within c of every pose of a conditioned box with tilt outside the box's bin +- D(c) overlaps every pose and is
    inadmissible (a strictly stronger row filter than the inscribed-core test); (iii) a mid-tilt conditioned box
    within 1.2 of an axis-aligned pin is dead at every tilt outside D(c) (tilt trimming in closed form).
    n-general and elementary. Measurement of (ii)/(iii) on A57's open boxes in progress (A96).

26d. EXACT Three more local minima on Trump's skeleton (A122, 2026-09-07, `4e8eecc8`), each with an interval endpoint
    certificate at eps 1e-9 (400-bit re-check): S33 = S34 = K19 at 3.916930865713920563..., S35 at 3.917417657814610628...
    (a distinct minimum, +4.9e-4, 6.9 deg apart in one square), and S38 at 3.928914685222977527... whose side is
    algebraic of degree 9 (root of x^9 - 16x^8 + 105x^7 - 360x^6 + 663x^5 - 518x^4 - 297x^3 + 1064x^2 - 992x + 358).
    S33/S35 are SMOOTH interior critical points (16 active rows of rank 14/15: a 2-/1-parameter family; Fritz-John
    closes at first order, unlike S07's kink) with no closed form found by PSLQ at 170 digits; all eleven squares
    load-bearing, no rattler (the PI's "fully loaded" reading confirmed); two flexes at fixed side, both blocked at
    second order. Same k6_07 skeleton as Trump and S07; differs from S07 in one square (f0 upright, flush against
    the BL column at x = 3/2) and is a third separate minimum (relaxed tilt paths crest +0.038 over it toward both).
    S38 (class k6_21) is a kink minimum of two chain formulas NOT in the A110 menu; its crest lies on the far side
    (42.794 deg, 3.934378) and it contributes no wall to Trump's basin; S07's wall is at 41.5649 deg, 3.886746029.
    The local certificate (A116) applies to S33 and S38 without any Trump cut out to r = 0.205 / 0.677.

## E. What cannot work (proved or measured)
27. PROSE Collapse theorem (A34): any sparse SDP relaxation whose cliques carry <= m squares is capped at
    s(m) <= 3.71.
28. LEAN+CERT Single-square guard-field certificates cannot kill any protected class (item 15).
29. PROSE Canary theorem (A66): dilated Trump saturates trump5's pair threshold exactly — no sound pair
    certificate kills him.
30. CERT  corners4 cannot be killed by occupancy counting: exact 7-point witnesses exist at every window
    side; its obstruction is orientation coupling (A66).
31. CERT  Bottom-up grain discharge cannot extend the certified radius beyond the basin theorems (hinge-grain
    wall, A76); the basin-exclusion LP row gains ~0.1 margin per decade of radius.
32. CERT  Any valid corners4 pair certificate is a necessarily-tight measure whose complete verification
    tree is ~1e9-1e11 nodes (frontier retention 0.75-0.86 per level, flat; Lemma W''', A77).
33. CERT  The enumeration-certificate mismatch law, seven+ faces (A30-A52): certificates price placements;
    enumerable objects quotient placement away.
34. CERT  s(12) >= 3.90 (A33).

## F. NOT established (frequently misremembered)
- "Every packing at or below s-hat has an axis-aligned square": NOT proven — k=0 (no simple squares) is a
  protected open class; item 19 gives corner-zone occupancy, not alignment.
- "Every packing at or below s-hat has a flush contact": NOT proven — I-L19 ("flush-mandatory") is a
  CONJECTURE, off the proof tree. Nearest theorems: items 18, 20, 21.
- A minimum number of FLUSH contacts against walls: NO theorem. Item 18 gives >= 2 wall CONTACTS on
  opposite walls (possibly corner-on-wall); in any k >= 1 stratum the simple square is flush to two walls by
  definition; a k=0 minimiser could a priori touch walls only with corners.
- Global confinement ("every near-optimal packing is near Trump"): TRUE EMPIRICALLY (A04: of 702 local
  optima exactly one, Trump's, has s <= s0) but NOT PROVEN — proving it is what the protected-tier
  campaign amounts to.

## G. Open (owned)
- trump5 residual tree -> basin (A60): cover j0 0.781 kill rate, deepen/ladders/confinement/window pending.
- Window coverage stragglers (A61), k5_11/k5_16 window grid G1 (A57).
- The 16 protected classes (C.K4TIER): pair route walled (32), grain route walled (31), U-ladder verdict
  pending (A80); likely next = A60-style conditioning trees on each exact protected stratum.
- TopLevel axioms remaining: `stratum_kill`, `trump_residual`, `a22_exact_structure`.
