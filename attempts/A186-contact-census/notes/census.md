# A186 — contact census of the eight budget-0 assignments of c0_Y1033: the numbers

Statement and lemmas: `docs/proofs/contact_census.md` (Theorem CC, Lemma CAND, Theorem CC-LP).  Figure:
`docs/residue_map/c0_Y1033_contacts.svg`.  Labels [T]/[S]/[M]/[F]/[P] as there.  All runs foreground,
one python at a time (the box held 12–14 pythons throughout: 8 lab workers + 4 Claude-extension
pythons caught by the CIM filter; no worker was launched — every computation here is a transient
process of 5–560 s), `PYTHONDONTWRITEBYTECODE=1`, read-only on every other attempt.

## 1. The assignments (`results/assignments186.json`, `code/nodes186.py`)

26 alive complete assignments in A182's journal (23 ALIVE(geometry) + 1 ALIVE(LP) + 2 [P]); 8 at budget 0.
The eight are FOUR geometries twice: the BL(0,2) choice F2+F4 vs F3+F4 leaves the same pieces (the meeter
windows of F2/F3 already contain BL(0,2)'s), the piece coordinates differing in the 10th digit.  Pin hulls
on the s0 slot lines within 6.3·10⁻⁸ [M]; `invariant: False` on every record (the failing A171 check is
not in the journal; see contact_census.md CC-3).

| # | assignment (TL00=F2+F3 throughout, BL11=F1+F2, BR01=TR01=H+F1) | pieces H/F1/F2/F3/F4/F5 |
|---|---|---|
| 1, 5 | BL02=F2+F4 / F3+F4, TR10=H+F5 | 49/47/39/51/50/49 |
| 2, 6 | BL02=F2+F4 / F3+F4, TR10=F2+F5 | 49/47/45/34/30/33 |
| 3, 7 | BL02=F2+F4 / F3+F4, TR10=F3+F5 | 49/47/39/42/50/49 |
| 4, 8 | BL02=F2+F4 / F3+F4, TR10=F4+F5 | 49/47/39/51/58/49 |

Hulls (assignment 1): H [2.498, 2.533]×[2.417, 2.498]×[17.2°, 28.1°]; F1 [2.374, 2.748]×[1.275, 1.519]×
[14.2°, 37.9°]; F2 [0.5, 1.583]×[2.144, 2.748]×[0°, 90°]; F3 [0.5, 1.733]×[2.144, 3.377]×[0°, 90°];
F4 [0.5, 1.733]×[1.5, 3.377]×[0°, 90°]; F5 [1.130, 2.136]×[2.144, 3.377]×[0°, 90°].  The pieces' tilt bins
are uniform in t = tan(θ/2) (Δt = 1/8, refined to 1/16).

## 2. Candidate graphs (`results/candidates186_b0.json`, `code/contacts186.py`, 4–6 s each) [M]

| # | edges | free–free | pin–free | walls | exterior faces H/F1/F2/F3/F4/F5 |
|---|---|---|---|---|---|
| 1, 5 | 24 | 15 | 9 (P0-F4, P1-F1, P1-F4, P2-F2..F5, P3-F1, P4-H) | F2:L F3:LT F4:LT F5:T | 116/127/127/155/129/133 |
| 2, 6 | 20 | 13 | 7 | F3:LT F4:LT F5:T | 116/127/104/129/98/114 |
| 3, 7 | 24 | 15 | 9 | F2:L F3:T F4:LT F5:T | 116/127/127/113/129/133 |
| 4, 8 | 22 | 15 | 7 | F2:L F3:LT F4:T F5:T | 116/127/127/155/135/133 |

Certified far [T, Lemma CAND]: H from every wall and from P0..P3 (H's only pin contact is P4, gap band
−0.028); F1 from every wall and from P0, P2, P4; F2..F5 from P3, P4 and the right/bottom walls; the
left/top walls only for F2..F5 as listed.  Every free–free pair is a candidate (the free boxes are
within √2 of each other); the deepest possible overlaps are F3|F4 (−1.79), F4|F5 (−1.73), F3|F5 (−1.68).
"Impossible piece pairs" (gap_hi < 0: a piece pair that cannot coexist) exist for 10–11 of the 15
free–free pairs — the piece-level coexistence cut of the memory note, not applied by A171's core clip.

## 3. The selection tree (`results/tree186.jsonl`, `code/tree186.py`) [M], Theorem CC-LP

Setting: s_lo = s0 (the record's question), s_hi = s0 + 0.05, pins slack 10⁻⁶, root cells ≤ 45°
(8–16 root cells), min cell 0.5°, exact check at width ≤ 2°.  2.5 ms a node.

| # | nodes | LP calls | closed dead | impossible cells | branch | bisect | exact-feasible | unresolved | min closed value | wall |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 209,006 | 158,155 | 83,919 | 50,851 | 10,112 | 64,124 | 0 | 0 | 3.877184 | 555 s (CAPPED) |
| 2 | 44,649 | 38,963 | 22,682 | 5,686 | 2,072 | 14,209 | 0 | 0 | 3.877212 | 125 s |
| 3 | 50,033 | 38,402 | 20,800 | 11,631 | 2,497 | 15,105 | 0 | 0 | 3.877154 | 125 s |
| 4 | 48,907 | 38,416 | 21,928 | 10,491 | 2,675 | 13,813 | 0 | 0 | 3.877100 | 125 s |
| 5–8 | 24–44 k | | 10–20 k | | | | 0 | 0 | 3.877100–3.877212 | 100 s |

Root menus: 25–27 near pairs, 10¹³–6·10¹⁵ interval leaves.  The lowest closed leaves are ROOT cells
(45° wide, all 27 selections fixed) at v = s0 + 1.0·10⁻⁴ — the coarse relaxation (McCormick loss
∝ q-range × cell width) is what keeps the tree open; no exact-tilt LP point at side ≤ s0 was ever found
(`live_low` 0) and no leaf is unresolved: every closed leaf is dead, the stack is simply not empty.
**[P] on all eight.**  Completion estimate: unknown (depth-first; the 555 s run closed 84 k leaves and
was still at root-level branches).

## 4. Stuck configurations (`results/global186.jsonl`, `code/global186.py`; `descend186.py`) [M]

`descend186` (LP descent from the lowest closed leaves) is uninformative: those leaves are 45° cells, and
the exact LP near their relaxed tilt point is infeasible with overlap 0.15–0.33 (results in
`results/descend186.jsonl`, kept as the negative).  `global186`: Nelder–Mead over the six tilts on the
exact ELASTIC LP (pair rows relaxed by a common τ ≥ 0, objective s + Mτ), selections by alternation,
starts inside the pieces.

| # | starts (M) | least τ | at side | support of the least-τ point | best side at any τ |
|---|---|---|---|---|---|
| 1 | 20 (50) + 16 (2000) | **0.0615** | s0 | F2\|F3, P2\|F2 (uprights at x = 0.5: the column above BL(0,1)) | 3.877084 (τ 0.06) |
| 2 | 8 (2000) | 0.123 | s0 | | |
| 3 | 8 (2000) | 0.079 | 3.9284 | | |
| 4 | 8 (2000) | 0.170 | 3.8793 | | |

No start reached τ = 0: **no disjoint configuration of the hull boxes was found** on any of the four
geometries.  The least-overlap point of assignment 1 is the upright column P2 (y ∈ [1, 2]) | F2 (box centre
y ≥ 2.144; to clear P2's top it needs centre y ≥ 2.5) | F3 (centre y ≤ 3.377 = s0 − ½): upright, F3 would
need centre 3.5, an overlap of 0.123; tilting spreads it to 0.06.  This is the coexistence obstruction A182's chord rows missed
(min rhs 0.51 there: the rows let F2/F3/F4/F5 dodge a single line; the elastic LP says they cannot dodge
all at once — measured, not certified).  The k7 + pinwheel4 shadow of the page's LP support does not
appear: the least-τ configurations are upright columns, not pinwheels.

## 5. Verdict per assignment

All eight: **[P]** — no witness (no exact-feasible LP point in 2·10⁵ + 3·10⁵ tree nodes, no τ = 0 in 52
elastic starts), not certified dead (tree capped at root-level branches).  What would certify: the
tree run to completion (Theorem CC-LP) — or, cheaper and now motivated, a certified COLUMN row for the
crowd P2 | F2 | F3 (| F4 | F5): the vertical extent needed by three bodies whose x-ranges all contain
[0.5, 1.58] against the height 2.877 above BL(0,1), stated as an interval inequality over the pieces
(the A97 wall-budget / A71 stuck-row pattern) — CC-5 in contact_census.md.
