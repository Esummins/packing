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
    alivewitness, D4 reduction — all Lean theorems. Corpus replays: measure (3.82), Theorem U, P1, K61
    (in progress), TRAP (in progress); A57/A60 corpora priced multi-day.

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
