# The ASSIGNMENT cover of a gallery page — A180, 2026-09-09

Tags: [T] proved here or by the cited lemma, [S] supported, [M] measured, [F] false, [C] Lean
obligation.  Sources: `docs/proofs/forced_corners.md` (Theorem FC, FC-corner, FC-slot, FC-count),
`docs/proofs/sideband.md` (Lemma A1 `linf_sep`, Lemma A2 `distinct_cells`, Theorem B), A161's exact
miss test (`multibox.Node.misses_cell`), A171's multibox invariant (`notes/usage.md`), A168's
multi-box case LP (`lp168.py`; every box is a hypothesis for a DISTINCT square).

## 0. The statement

> **[T] Theorem ASSIGN.**  Let a page have pins P_S (five for the three pinned classes), conditioned
> square(s) H, budget b = 11 − |P_S| − #H free squares, and forced cells p_1..p_m (Theorem FC).  Let
> F = Δ_λ P be the dilate of any packing of the page's hypothesis.  Then there is an **assignment**
> A: {p_1..p_m} → unordered pairs of distinct elements of R := {H} ∪ {the b free squares of F} such
> that for every cell p both members of A(p) have interiors meeting the widened box B_p⁺, and a
> member is H only if H's page box does not provably miss B_p⁺.  Every constraint below is a
> NECESSARY condition on (F, A), so a search that (i) enumerates the assignments up to the labelling
> of the free squares, (ii) prunes only by necessary conditions verified on the node, and (iii) finds
> every node dead, proves the page DEAD.  A node with an open cell and NO admissible option is dead.

*Proof.*  By Theorem FC each B_p⁺ is met by two distinct non-pin squares of F; the non-pin squares
are H and the free squares (FC-count); choose any two for A(p).  If H ∈ A(p) then H meets B_p⁺, so
A161's exact separating-axis test on H's box cannot certify a miss.  ∎

## 1. The labelling (free squares are unlabelled)

The free squares of F carry no names.  The search names them in the order it INSTANTIATES them:
F_1 is "the free meeter it first commits to a cell", and so on.  At an open cell p the options are

  (a) an EXISTING role r ∈ {H, F_1, .., F_k} meets p,  or  (b) a NEW free square meets p (only
      while k < b: FC-count's global constraint, five free squares on a trump5/k5 page).

[T] These are exhaustive: the second meeter of p is a non-pin square of F; it is either one of the
already-named squares (case (a) for that name) or an as-yet-unnamed free square (case (b); the name
F_{k+1} is then assigned to it).  In case (b) the new square is DISTINCT from every named role by
construction, which is exactly what the multibox mutual clip and the pair leaf assume (A171
`usage.md` line 1; A168's LP bridge).  Two new squares at one cell ({new, new}) are distinct from
each other; their centres are ℓ∞ ≥ 1/√2 apart (Lemma A1), and at a CORNER cell they lie in
different Lemma-A2 cells (FC-corner) — the split of `geo178b` / `A2_PAIRS`, an exact partition.

## 2. The role box of a named square, and the tests

[T] If F_i is assigned to cells p, q, .. then its centre lies in the intersection of the meeter
windows W_p ∩ W_q ∩ .. (`classes178.meeter_window`: a unit square meeting an open box has its
centre within ℓ∞ 1/√2 of the box, and inside [1/2, s0 − 1/2]²), tilt in [0, 90].  Tightening a role
to a window ("update s1 so all its placements touch BL11") is therefore sound, and so is replacing a
role's box by the HULL of its surviving pieces (a superset) before the next normalisation.

[T] Candidate test for an existing role r at cell p (`Search.can_reach`, `test_members`):
 * the √2 rule: r assigned to q with dist(B_p⁺, B_q⁺) ≥ √2 cannot meet p (FC-count's distinctness
   argument: a unit square's interior has diameter < √2);
 * A161's exact miss test on r's current box against the closed widened box;
 * the node {pins, H, F_1..F_k with r restricted to W_p (+ lonely clip at a forced corner)} is not
   dead (EmptyBox), and r's surviving hull still does not provably miss B_p⁺.
A failure of any of these certifies "r ∉ A(p)".  For a NEW square: the node with F_{k+1} ∈ W_p.
For a pair {a, b} of existing roles or {a, new}: the joint node.  For {new, new}: the A2 / grid
split of §1, each sub-case a node; no alive sub-case = the pair is impossible.

[T] The lonely clip: at a forced CORNER both meeters are non-lonely poses (Theorem B, FC-corner),
so `corners={role: corner}` is sound for H, F_i and new roles alike.  At a SLOT there is no lonely
clip (forced_corners.md §5(f)).

## 3. Unit propagation, then branching (the PI's order)

At every stage the options of every open cell are computed; a cell with ONE option is FORCED
(applied, the node re-normalised, the options recomputed) until no cell is forced; a cell with NO
option kills the node; otherwise the search branches on the cell with the fewest options, with
{new, new} sub-options LAST.  [T] DEAD iff every branch is dead (the options are exhaustive, §1).
A node budget or deadline stops the search with verdict UNDECIDED [P], never ALIVE.

## 4. The leaf at a complete assignment

All cells closed: the roles are pins + H + F_1..F_k (k ≤ b), pairwise distinct squares; the multi-
box case LP with budget 11 − #roles on the role HULLS (A168 `lp168` pattern, A170 exact-core
certificate, frozen `verify_case.py` sha 521cb01f) kills the node when it certifies.  Budget 0 (all
five free squares named) has no LP: the geometry (pair leaf) is the only leaf and an alive node is
[P].  A role hull without an exact core is not handed to the LP ([P], recorded).

## 5. What is sharper than A178, and what is not

Sharper: the global count (at most five free squares in total across the six cells), the mutual
clips between the meeters of DIFFERENT cells inside one node (A178 kept √2-separated groups in
separate rounds), the tightening of a role to every cell it must meet, and the forced order.  Not
sharper: every test is still A171's clip (a pose is removed only when it certifiably meets a K′), so
"alive" at a node is a failure to kill, not a witness; the verdict ALIVE(geometry) means only that.
