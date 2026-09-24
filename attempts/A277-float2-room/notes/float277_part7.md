# part 7 -- the search [M], the Lean file, the status of link 5d

## 7.1 float277: FLOAT2 in the P1 sense  [M]  (code/float277.py, results/float277.jsonl, logs/float277.log)
Objective t = min(local261.terms: pairwise gaps, containment (quadrant 3.2), box depths of C and D, X and Y miss the
open box, float distances, every drop of every floater blocked by some square present; and -J_F for every floater F,
J on A261's coarse any-pose grid (3 deg / 0.04; 3 900 wall cells)).  sup t > 0 <=> a FLOAT2 corner that neither a drop
nor a P1 cell lands, in the local model with the squares listed.  Nelder-Mead, 12 restarts per row (6 seeded from the
exact witness of part 2 with growing jitter, 6 random), BelowNormal, one process.  Rows finished at this writing:
| scenario | squares | seed | sup t | where the optimum sits (check_witness, exact) |
|---|---|---|---|---|
| F4 | C:F D:F X:V Y:H | 99 (1 restart, witness) | -0.0049 | D at h_v = 0.0001, J_D = +0.0049 (a flat floor cell lands D) |
| F4 | same | 1 | -0.0000000 | C at h_u = h_v = 0 (a corner square: not a floater), C's floor drop unblocked |
| F4 | same | 2 | -0.0000000 | D at h_v = 0.0 (a floor toucher: the corner is a JAM), Y's depth into T_v(D) = 0 |
**Reading:** the supremum is 0 and is attained only on the boundary where a floater becomes a toucher -- exactly the
degeneration FLOAT2 -> JAM (or -> corner square).  So [M]: **no FLOAT2 corner that P1 cannot land exists in the
4-square model {C, D, X, Y}**; the witness of part 2 (all four drops blocked) fails only P1's flat floor cells.
Pending in the jsonl / log (the process runs on, detached, resumable): F5 (+ a fifth floater K as an indirect blocker),
F3 (no floor toucher), F4b (X, Y free to meet the box).  Their rows are [M] for the local model only; an optimiser's
sup is never evidence a lemma is true -- here it says where a THEOREM should be looked for (7.3 (L6)).

## 7.2 Lean  (Statements/Open/Float2Room.lean; one import line in Statements.lean; AUDIT regenerated)
Theorems (std axioms only): `one_drop_core` (ONE-DROP / MUTUAL: a separating normal is not both (-,+) and (+,-)),
`cap2_count_core` (n <= 8 + cap, cap <= 2 => n <= 10), `cap2_of_diam` (two interior-disjoint unit squares with centres
in a set of pairwise squared distance < 1: impossible; from `inradius_sep`).  Opaque `Float2Corner`, `BLSectorMiss`.
Axiom [C] `bl_cap2_float2` (BL-CAP-2(C, D)).  Theorem `float2_ten` (from the axiom): m pocket squares, pairwise
disjoint, any three containing two BL-sector misses => n = 8 + m <= 10.  `lean/audit.py`: "No statement depends on
`sorryAx`" (AUDIT.md rows 114-118).  Not formalised: the sector reduction for two misses (prose, part 3.2), Lemma LOW
with a floating D (prose; the cores `low_core` etc. are reused unchanged).

## 7.3 Link 5d after A277
(L1) `pair3` (TL / BR) -- still not landed; every route here needs it for the PAIR corners of a non-PAIR ring.
(L2) 5b's drop tree cells c5_4 / c5_5 (theta 25-30 deg) capped; the corner theta, phi <= 5 deg is [T] (A276).
(L3) **5d = BL-CAP-2(C, D) [C, axiom `bl_cap2_float2`] and BL-CAP-2(A, C) [C, prose]**: certificates designed and
benched (cert277; 6 / 5 parameters, 0.02 s per box, 12/12 points CERT), priced 30-1000 / 3-100 CPU-h, NOT launched;
add a P1-aware PRUNE before any launch.  The cheap 4-parameter dropped pair (~3 CPU-h) closes only FLOAT2 corners whose
two blockers serve their far boxes (then also STRIP-C / STRIP-D = 5b).
(L4) [C] INDIRECT-FREE (part 5.5 / float2_room.md s.5.5): would leave middle touchers as the only indirect holders.
(L5) Lean `jam_count` stays; `bl_cap2_float2` is new; the [T-prose] items of this note have no Lean statement beyond the cores.
(L6) [C] "no normal-form FLOAT2 corner exists": [M] sup 0 at the boundary; the theorem would be P1 on the flat floor
cells under D's lowest vertex (part 2.4 / float2_room.md s.2: the cells x in (sup I_C, x_min(Y) - 1) are met by D only
unless C's low part or Y's left end reaches them) -- a 2-3 square lemma, not attempted here.  It would delete (L3)'s first half.
