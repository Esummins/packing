# A198 -- FASTPROP: what the engine proves, stated for any n

Page = a tree node at s0 with pins P_1..P_k (axis-aligned, centre within delta_pin of the slot centre), the
conditioned square(s) H (centre box x tilt bin) and n - k - #H FREE squares; forced cells p_1..p_m of the class
(Theorem FC, `docs/proofs/forced_corners.md`): each has TWO DISTINCT NON-pin meeters of its widened open box B_p+.

## The objects

* **Cells.**  A grid of closed cells of side w < 1/sqrt2 over the centre range [1/2, s-1/2]^2 (w = (s-1)/ceil((s-1)/0.70)).
  **[T] Lemma A1** (`sideband.md` s.2, Lean `linf_sep`): two interior-disjoint unit squares have centres at
  l-inf distance >= 1/sqrt2, so a closed cell holds the centre of at most ONE square of the packing.
* **Reach(g, S)** for a cell g and a set S of forced cells: the pieces (rational centre rect x tilt sub-bin) of
  g n (intersection of the meeter windows of S) that survive (i) the container clip at w_min (A171
  `container_clip`, strict=False), (ii) the exact dead test against every role's certified K' (A171
  `_clip_rect_obstacle` / `dead_poly`: a pose meeting int K'(R) meets R's square at EVERY pose of R's box, and R is a
  distinct square), (iii) A161's exact separating-axis MISS test against every B_p+, p in S (every pose of the piece
  misses the open box), (iv) at a CORNER cell, A173's lonely clip (Theorem B, `sideband.md` s.3: a lonely pose admits
  no second meeter of the corner box, so it cannot be a meeter in a packing where the corner has two).  **[T]** every
  free square of a packing of the page with centre in g meeting every B_p+, p in S, has its pose in Reach(g, S).
  Joint sets are seeded from the single-slot survivors (sound: Reach(g, S) subset Reach(g, {p}) for p in S).
* **Role reach(R, S)**: R's normalised pieces re-clipped against the other roles and MISS-tested for every p in S.
* **Chords.**  For a placement (g, S) the exact min OPEN chord of every pose of Reach(g, S) on a guard line
  (A190 `guardlines_v5.minchord`, open chords); for the pins the chord of the pin box.  **[T]** the open chords
  of the distinct squares of one packing on a line sum to <= s (the chord-sum lemma, A144/A190).

## The count (Theorem COUNT, [T])

Let each free square F_i of a packing have centre cell g_i and let S_i be the set of forced cells whose open
widened box int F_i meets; likewise (g_R, S_R) for every fixed role R (H, H_2.., instantiated meeters).  Then
(a) (g_i, S_i) has Reach(g_i, S_i) != {} and (g_R, S_R) has role reach != {} -- so they are rows of the OPTION
TABLE; (b) the cells g_i, g_R are pairwise distinct (A1), and any two hulls admit centres at l-inf distance
>= 1/sqrt2 (A1, `a1_compatible`); (c) for every forced cell p, #{i : p in S_i} + #{R : p in S_R} >= 2 (Theorem FC:
the meeters are non-pin, and the pins are the only other squares); (d) on every guard line, sum of the pins'
chords + sum over placed squares of minchord(row) <= s (chord-sum).  Hence: **if the exact search over the option
table finds no assignment satisfying (b)-(d), the page is DEAD.**  If it finds none with H's option barred from
p, then in every packing H meets B_p+ (H FORCED at p) and H's box may be replaced by the hull of role reach(H,
forced set) (**[T]** every pose of H in a packing lies in it; empty => DEAD).  A cell p that H provably misses
(no H option contains p) with fewer than 2 alive cells is DEAD by A1 + FC; with exactly 2 alive cells both are
forced meeters and are INSTANTIATED as roles (box = hull of Reach(g, {p}), a distinct square each by A1) so that
multibox's mutual clip carries them into H and the other cells; a role forced at a cell that already holds an
instantiated role IS that role (one centre per cell) and the role is clipped to role reach(R, S u {p}).
The search returns the first feasible cover as a WITNESS (an option-table row per square); a witness is a
failure to kill, not a packing -- `fig198.realise` tries to sample one pose per row pairwise interior-disjoint.

## What is NOT claimed

The option table is an over-approximation at the bisection depth used (depth 5 single / +2 joint, 4 tilt
sub-bins): a row survives when no piece is PROVED dead, so ALIVE means "not killed by these tests", never
"realisable".  Only kills are verdicts; each kill's certificate is the list of exact tests in
`certs/fp198_<nid>.json` (`tests`: REACH / ROLE-REACH rows with their rects, depths and surviving fractions;
A1-FC / COUNT / H-CLIP / H-JOINT / INSTANTIATE / EMPTYBOX rows with their verdicts), replayable from the page
record with the same library calls.  `check198.py` is a one-sided float sampler cross-check of an A1/FC kill
(a refuting pose would be a bug; none found).
