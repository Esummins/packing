## 2026-09-08/09 — A166-nearest-corner-subtree (Opus engineer) — the PI's per-node nearest-corner sub-tree: one sub-tree, not eleven; the canary forces a second branch; the (C) leaf is provably unavailable

**The corner is `TR`, for everything.** The metric is `|z_H − p_c|` from the conditioned box's CENTRE to
the corner POINT. It comes out **`TR` on all eleven converged-alive k0_00 cells** (`d` = 1.8536 … 2.3943,
smallest margin to the runner-up 0.042) **and on 117 of the 119 remaining open k0_00 cells** (A115's 166
open records minus A141's 47 `K'`-lane kills; the other two are `BL`). The reason is structural: A38's
level-1 cover conditions a square in the D4 **fundamental triangle** of the interior zone, which lies in
the TR quadrant. So the brief's "a sub-tree per hard node" is ONE sub-tree, the corner never has to be
chosen, and it is rooted at exactly the corner A141/A159 found at NEAR-MISS on five of the eleven.

**The canary passes, and it corrects the construction.** `l1_153` is Trump's image `g4`, square `sq9` —
one of the three INTERIOR tilted squares — with pose distance **0.000000** to `B_H` in all three
components (`code/trump166.py`; the other seven images have no square in `B_H`, so only `g4` imposes an
obligation). `g4`'s two widened `TR` meeters are the corner slot square `sq5` (penetration 1.000, cover
cell `(0,0,0)`) **and `sq9 = H` itself** (penetration 0.0359, cover cell `(3,4,3)`). Enumerated literally,
`l1_153`'s budget-8 pair cover is EMPTY: 193 of the 216 cover cells are dead, 3 degenerate, 20 alive, and
all 20 alive cells lie in the corner-hugging block, so every pair of them is within centre distance 1.
**A tool that read "all pair cells dead ⇒ dead" would have certified a kill of a family that exists.**
K0-BLOCKED says the corner box has two DISTINCT meeters; it does not say either differs from the
conditioned square. So the sub-tree owes two branches — (a) budget `11 − 3 = 8`, both meeters `≠ H`;
(b) budget `11 − 2 = 9`, one meeter IS `H` — and (b) exists exactly when some pose of `B_H` meets
`int B_TR^w`, decided exactly by A161's `box_misses_cell_exact`. `g4` lands in (b). Recorded as a rule in
`notes/canary.md`.

**What conditioning on `H` is worth, geometrically: 91–100 % of the corner-first pair root, for pennies.**
The shared census (A143's `(P2)`/`(P1)`/`(P1s)` over all `216·217/2 = 23 436` unordered pairs of A155's
216-cell cover — no transpose quotient, because `H` breaks the corner's stabiliser) leaves 4 244 live
pair cells at the window pad (3 646 at pad 0). Conditioning on `H` leaves **0, 0, 0, 0, 16, 25, 60, 139,
178, 237, 371** on the eleven, in increasing order of `d`, for 3–95 CPU-s a cell after a 100 CPU-s
census. The whole cut is the two `H` stages: **99–191 of the 216 cover cells (46–88 %) cannot hold a
corner meeter distinct from `H` at all**, because a square there would have to overlap `H`'s own square
(`H2` = centre distance < 1; `H1` = `K'(B_H)` meets `K'(X)`). A161's exact reach test removes a further
constant 16, A131's clip with `H`'s inscribed axis core (A158's rule) 0–6, and A143's own pair chain plus
A158's mutual clip (run FIRST, per tilt sub-bin) and an exact core-disjointness budget gate only 0–26 pairs on top.

**And the free lunch is provably unavailable.** A (C) leaf — branch (a) empty AND branch (b) impossible,
i.e. a kill with no LP, no certificate and no depth — needs `H` close enough to the corner to crowd the
whole zone AND far enough that it cannot reach the corner box. Measured over the whole pool: `H` can meet
`int B_TR^w` exactly on `d ∈ [1.5715, 2.0573]` (53 cells) and provably cannot exactly on
`d ∈ [2.0127, 2.5943]` (66 cells), while every one of the 11 + 41 cells with an empty branch (a) has `d ≤ 1.9319` — and the smallest
`can_meet = False` cell (`l1_148`, `d = 2.0127`) already keeps 25 pair cells. **The two conditions are
anti-correlated and their intersection is empty on all 119 cells.** Lemma A166-1 (the "squeeze": if
`diam(Z(w) \ ∪_{v ∈ R_H} B(v,1)) < 1` then `H` must itself be a meeter, with an exact grid+hull bound)
fires on 1 of 22 (cell, pad) pairs — `l1_124` at pad 0, bound 0.7255 — and never at the window pad,
because `Z(w_max)` is 1.2326 wide and the far set generally has two components more than 1 apart. The
box-level cover is the sharper instrument here and `K'` is why: on `l1_153` the cell at local `(5,0)`
survives `H2` at `maxdist = 1.1075` and dies on `H1` at `K'` depth `1.09e-3`.

**The PI's prediction, decided; and the coordinator's two additions.** *Prediction:* "for a Trump-like
`H` whose nearest corner is SIMPLE in Trump, forcing that corner doubly met contradicts the Trump-like
packing and the LP dies at once; only the `H` adjacent to the non-simple corner survives." **Right in
direction, wrong in consequence.** The six cells whose nearest corner is SIMPLE in their matching Trump
image are exactly the six with the closest Trump matches (pose distance 0.000–0.226) and the smallest
`d`, and four of them have branch (a) ANNIHILATED — forcing `TR` doubly met by two squares OTHER than
`H` is indeed contradictory there. But that is not a kill: those same four are precisely the cells where
`H` itself can reach the corner box, so branch (b) survives — as on `l1_153` it must. The five cells
whose nearest corner is NON-SIMPLE all survive branch (a) with 16–371 pair cells, so "only the `H`
adjacent to the non-simple corner survives" is backwards as a statement about which branch is empty.
*Addition (1):* every one of the eleven matches one of Trump's three INTERIOR tilted squares — `sq9`
(`l1_153` exactly, `l1_159`, `l1_148`), `sq8` (`l1_104`, `l1_124`, `l1_158`), `sq7` (the five NON-SIMPLE
cells) — and `sq7`, the "third" interior square, is the one whose matches are POOR (0.19–0.73) and whose
cells the geometry hits LEAST, so "the third interior square should die fastest" does not survive; in
`g0`'s frame `sq7` is nearest `TL` (2.554) with `BL` a close second (2.586), not clearly at the
three-simple corner. *Addition (2):* the quadrant census (split at `s0/2`) is **`3/3/3/2` in every one of
Trump's eight images, and the sparse quadrant is always the one DIAGONALLY OPPOSITE the three-simple
corner — never the non-simple one**, so "the non-simple quadrant holds exactly the two meeter centres and
nothing else" is not Trump's pattern: it always holds a third centre, and that third centre is always one
of the three interior tilted squares. The corrected signature is *one sparse quadrant, opposite the
three-simple corner*. On the eleven the dual support's sparsest quadrant is `TR` on 8 of 11 — thin exactly
where `H` and the forced corner crowd both live — but supports of 10–83 placements are not comparable
one-for-one with 11 squares, so this is a shape statement, not a count.

**Free by-product worth keeping: 66 certified `M = 0` corners.** A141/A148 record `TR(0,0): M 0?` on six
of the eleven — a sampled 0 with a question mark, because A141's `box_misses_cell` separates only along
the CELL's normals with the box's bounding half-width and so can never fire for a box whose square clears
the corner box along one of its OWN edge normals. A161's full separating-axis test over the parameter box
**certifies** `M = 0` on 66 of the 119 open cells and refutes it on the other 53. That is a strict
strengthening of A141's lane ledger, obtained for free.

**LP.** Budget 8 (`H` + two `TR` squares, A135 exact cores, `K'` an audit column, warm from the cell's own
A115 record, 240 s cap, FROZEN `verify_case.py` sha `521cb01f…`) and budget 9 (the degenerate branch).
33 nodes decided in 7 244 s of measured solve time (≈ 1.2 CPU-h at the ~28 % CPU share two BelowNormal
processes got on a box carrying 7–14 other lab pythons), inside the 3 CPU-h cap. **Budget 8, n = 21:
`η` min −1.4706, Q1 −0.5000, median −0.0993, max 0.0000; 9 converged; 2 converged kills. Budget 9
(degenerate), n = 12: `η` min −0.0097, median −0.0000, max 0.0000; 0 kills.** The reading: A158b's
exact-1 accounting is the default — the degenerate child returns `τ = 9.000000` on every cell measured,
which is A143's "second core at the same corner" geometry (`η ≈ −0.08`) with `H` added, and no amount of
compute moves it. The budget-8 child spans A143's one corner (`η = −0.04`) and A150's four
(`median η = −1.0`): it reaches `η = −1.4706` (`l2_p65_101`, unconverged), `−1.0000` (twice, converged
and certified), `−0.5000`, `−0.4680`, and sits at `0.0000` on the rest. **Three spread cores are not four
spread cores: two of A166's three sit at the same corner, and that is the whole difference from A150.**

**One CERTIFIED kill — and getting it certified uncovered a bug in SHARED machinery
(`notes/certificate_bug.md`).** `l2_p65_101_b8_005_512` converges at `τ = 7.000000` against budget 8 in
118–134 s and the frozen verifier first reported 32 HOLES at every one of five separation rounds. The
cause is not the LP and not the margin: **`caselp.make_certificate` rebuilds the hypothesis with
`Hyp.from_json`, whose `__init__` sets `cores = [b.core() for b in boxes]` — the STOCK cores — discarding
the `cores` field the json carries.** Every attempt that runs a node with A135's certified EXACT cores
uses the `ExactHyp` pattern (A150, A158b, A166, A140's exact-core re-solves): the LP's row filter drops
placements penetrating the EXACT core, the certificate then exempts only the STOCK core, and every
placement in the annulus between the two is a guaranteed hole. All 32 holes here are the single
axis-aligned placement `(3.35109, 1.49000, 0°)`, at SAT depth **+0.029594 against the exact core** and
**−0.000001 against the stock core**, with `exact_mass = 0` — which is why the A13/A14 separation loop
cannot move it: the row it is asked to add is precisely a row the LP is entitled to drop. Confirmed
independent of the scale (1.005, 1.02, 1.05, 1.10, 1.14) and of the rational grid (1e6, 1e9, 1e12): the
same 32 holes every time. **Carrying the exact cores — sound, because A135's `exact_a` certifies
`K(B) ⊆ Q(p)` for every pose `p ∈ B`, and the bug over-claims so old PASSes stay valid — gives PASS on
the frozen verifier for 15 of 15 certificates** (`code/certfix166.py`,
`results/certfix166_l2_p65_101_b8_005_512.json`), so A166 has a certified budget-8 kill:
*no 11-square packing has a square in `l2_p65_101`'s conditioned box together with two distinct squares
in those two `TR` cover cells* (total `7.035000 < 8` at scale 1.005). **And the same substitution turns
5 of 5 of A150's previously-FAILING certificates into PASSes** (`code/certaudit166.py`,
`results/certaudit166.json`; A150 is read-only, the patched copies live under A166, and A165's live
`l1_104_spread_*` certificates in the same directory are excluded by prefix), so **A150's four-corner
root is 7 converged kills and 7 CERTIFIED, not 4**, and its §5 sentence "they need the A13/A14
separation loop with more rounds and a longer `cert_time`" is wrong — they needed the cores they were
solved with. `caselp.py` was NOT edited (read-only); A166 patches the certificate in its own emission
path. **127 of the 166 open k0_00 records carry the verdict `kill-candidate (cert FAIL)`; if they were
emitted through an exact-core path they are candidates for immediate certification at zero LP cost**, and
the same question applies to A140, A149, A158 and A165. `code/certaudit166.py --dir <certs dir>` runs
that audit on any directory, writing only under A166.

**Price.** Geometry: 0.5 CPU-h for the whole 119-cell pool — the cheapest per-node geometry in the k0 lab,
and worth running for the 66 certified `M = 0` corners and the survivor counts alone. LP: 1 048 nodes to
decide the eleven at level 1 (70–95 CPU-h), ≈ 1.2·10⁴ nodes and **800–1 000 CPU-h** for the pool at level
1, **6 000–8 000 at depth 2** under A85's law, plus ≈ 400 degenerate nodes at 25–30 CPU-h — i.e. the same
order as `docs/budget.md`'s 12 000 CPU-h k0 row, without removing any of the interior tree's obligations.
**Window transfer costs nothing new**, unlike A155's slab route: every A166 stage is stated at the full
K0-WIDEN pad `w_max = 0.0255100742` and every test is monotone in `w`, so a fixed-side `verify_case` PASS
carries all of `[3.82, ŝ)` by Lemma B.0 + Lemma K0-WIDEN alone (both `[T]`); certificates are stamped
`scope: s0_fixed_side`, `window: transfer pending (k0_route sec 4.1)` until that two-lemma chain is signed
off in `k0_route.md`, which is proof-reading, not compute. The remaining window debt is the old one:
K0-O1 (k1_00's tree, ∀-packings, ~200–300 CPU-h, paid once).

**Two corrections to inherited code.** (i) `exactcore.cores_pairwise_disjoint` compares
`max(|Δkx|, |Δky|) − (a_i + a_j) > 0`, the separating-axis test on the `x`/`y` axes with support radius
`a`; a core at tilt `θ` has `x`-support radius `a(|cos θ| + |sin θ|) > a`, so the function is **not a sound
interior-disjointness test for TILTED cores** — it can report DISJOINT for cores that overlap. It is
correct for the axis-aligned pin cores it was written for. A150's four-corner LP (four tilted cores) and
A158b's seven-box gate both called it; A166 uses its own exact rational SAT over the four edge normals
instead (`geo166.cores_disjoint_exact`), and both earlier gates should be re-checked. (ii) A141's
`box_misses_cell` vs A161's exact version, as above.

**The coordinator's mid-attempt reinforcement (from the PI's review of A165) — already satisfied, and
the run was redone in that order to be sure.** Every pair box is clipped against `K'(H)` AND against the
other pair box's core (A158's mutual clip) **per tilt sub-bin (`nsub = 4`) and BEFORE** the pair leaf, the
reach test, the exact-core gate, the figures and the LP; the boxes' `K'` and their four sub-bin `K'`s are
rebuilt on the clipped boxes, so every later test uses the smaller box. A box all of whose poses meet
`K'(H)` is emptied and the case dies — that is A166's `DEAD_CLIP` (or `DEGENERATE_CLIP`, where the box
could BE `H`; the split is what the canary needs). The earlier ordering (mutual clip last, `nsub = 1`) is
retained in `results/v1/`: moving the mutual clip first and refining it to 4 sub-bins takes `MUT` from 1
to 8 pair kills on `l1_071` and 0 to 10 on `l1_104`, empties one further cover box on `l1_124` and one on
`l1_158`, and lowers survivor counts by 1–5 per cell — **no verdict changes**, and the two certified
kills were solved on the (larger) `nsub = 1` boxes, so they remain valid a fortiori. Kept fractions per
box per cell are in `notes/tables.md` §6b and in each `survivors166_*.json`. The figures follow the same
instruction: `K'` of each box SOLID as the box's core, the pose union a thin dashed outline only, with
the legend saying it is not feasible space.

**Discipline.** Read-only on every campaign and prior attempt, A165's live `l1_104` files included (A165
was running throughout; nothing of it was read or written). Frozen verifiers byte-identical
(`verify_case.py` imported by path, sha checked into the certificate records). Every sentinel polled by
`lp166.py` before every node; no shard launched; no recursive deletes; `PYTHONDONTWRITEBYTECODE=1`
everywhere; 2 BLAS-pinned BelowNormal LP processes at affinity `0xFFFF` with the lab-python count polled
before launch (the box carried 7–14 other lab pythons throughout, so the LP ran at ~28 % CPU and the wall
per node was ~270 s). Independent checker `ALL_OK` (20 000 cover draws, 2 109 corner-meeting poses, 0
misses; 0 contradictions over 4 213–9 639 sampled pose pairs per stage per cell; realised triples found
for the survivors of three cells, so those survivors are not artefacts).

**Files.** `attempts/A166-nearest-corner-subtree/` (`BRIEF.md`; `code/{cells166,geo166,subtree166,
squeeze166,pick166,lp166,canary166,check166,trump166,price166,draw166,report166,cert166,certfix166,
certaudit166,clipaudit166}.py`, `run166.ps1`;
`results/{subtree166.jsonl,subtree166_wmax.jsonl,subtree166_w0.jsonl,survivors166_*.json,
paircensus166_*.json,nearest166.json,trump166.json,squeeze166.json,canary166_wmax.json,
coverplan166_wmax.json,nodes166_wmax.json,price166_wmax.json,check166_wmax.json,clipaudit166_*.json,
cert166_*.json,certfix166_*.json,certaudit166.json,lp166_wmax_s*.jsonl,lp166_retry.jsonl}`;
`certs/`; `figs/a166_{wmax,w0}_*.svg` (one page per cell per pad, A148 panel style, the three boxes
drawn); `notes/{method,canary,certificate_bug,composition,tables,registry_row,doc_lines,log_entry}.md`;
`logs/`), plus the
registry row, this entry, and one paragraph in `docs/residue_ledger.md` §4.
