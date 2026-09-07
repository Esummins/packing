# The residue ledger — everything still standing between us and s(11) = ŝ, as of 2026-09-06 02:00

Companion to `residue_map.md` (the narrative, kept as a log) and `shadows.md` (the gallery). This file is the
**exhaustive list** of what is not yet killed, organised by node family, with a picture for each family, its current
status, the technique that applies, and the n-general lemma it instantiates. Read the pictures first; each section
says what a drain from the PI would change.

Frozen facts: ŝ = 3.877083590022814 (Trump), s0 = 969271/250000 = ŝ + 4·10⁻⁷, window W = [3.82, s0]. Second-best known
packing: S07 at 2 + 4√2/3 = 3.885618 (known_results 26a). Every k ≥ 5 class is dead at the fixed side s0; the proof
needs every class dead on W, and only Trump's class alive there with Trump unique.

**Totals and time estimates live in `budget.md` (the one fixed home; updated on every landed measurement). This file
lists what is left; that file prices it.**

## 0. The one-table version

| layer | family | what is left | count | technique now | needs |
|---|---|---|---|---|---|
| A57 window trees (k5_11, k5_16) | S01 "room at side 4" | boxes whose LP support leaves a slot empty/singly met | ~420 alive-at-LP (k5_11 238 + k5_16 178) | crowd rows tried (A109): 0 kills at licensed depth | splitting (tree terminates); or a depth lemma above s0 |
| | S02 the k7 pinwheel | boxes whose support is the 3.8867 pinwheel | 252 (184 + 68), carries the deep tree | tight core (in), deeper levels terminate (f₄ = 0) | grain kill (§6) or just time |
| | S03–S06, S08–S53 | 45 smaller shadows, mostly level 1 | ~250 | as S01/S02 by type | PI review of the gallery |
| | fractional | no integral support at all | 264 (151 + 113) | tree only | the genuine tail |
| Window stragglers | k5_02, k5_03 (partial), k5_12 (k5_13 running) | thin whole-window certificates | 3–4 k5 classes; **k6 and up all full** (A114 closed k6_07, k6_23, k6_27) | slab sweeps, resumable | ~5–15 CPU-h |
| Protected tier | trump5 cover/slackcore | residual tree ending in Trump's basin | 325 alive nodes in A107's input (S01 196, S07 18, S02 12 …) | A60 route, paused | S01 crowd rows; k6_07 window for the S07 slot |
| | the other 15 protected classes | conditioning trees per exact stratum | 3,500–4,200 CPU-h priced (A100) | A84/A100 model | same levers as A57 |
| k0_00 | the frame residue | K0-BLOCKED packings in W with every intruder locked | conjecturally empty (LOCK-FREE⁺) | tree priced 9,300–21,700 CPU-h (A99) | one theorem: LOCK-FREE⁺(< 4) |
| Lean | TopLevel axioms | `stratum_kill`, `trump_residual`, `a22_exact_structure` | 3 | replay of certificates + the above | the above |

---

## 1. The A57 window trees (k5_11 = BL[2,1] + TL[1] + BR[1]; k5_16 = corners4 + BL[1,1])

**What a node is.** One conditioned square with a centre box and a tilt bin; the five class pins fixed; the other five
squares free and seen only through the LP. Levels halve each box coordinate. Alive-at-LP means τ = budget exactly.

![A57 level-1 residue by status, alive lineages, hole witnesses](residue_map/a57_residue.svg)

**Where it stands (paused 2026-09-06 00:45, A96 PAUSED.md).** Window fraction k5_11 0.978, k5_16 0.991. Open boxes
before the tight core: k5_11 L1 158 / L2 122 / L3 10 / L4 4; k5_16 L1 213 / L2 9. The tight core (T5′) removes 70 of
them (20/32/7/11 by level) with the certificate unchanged. Level-4 descent measured 0 of 30: the tree terminates.
**Schedule if simply resumed: 13.3 wall-days at 5 workers** (19.6 without T5′; 27 at the 95% upper bound on the tail).
**Tilt trimming (PI, 2026-09-06; A96 `155a3c5b`, measured, not deployed):** certify dead every tilt sub-interval of a
box for which the whole centre box lies inside one pin's octagon (Minkowski sum of the pin core and the reflected
square) — T5 with a tilt-range parameter, no new verifier. On 2,222 boxes: 159 boxes' surviving bin is empty (51 L1, 86 L2, 10 L3, 12 of 14 at
L4), of which **70 are exactly T5′'s kills (trimming subsumes the tight core) and 89 are new** (31 L1, 54 L2, 3 L3,
1 of the 3 post-T5′ L4 boxes); 155 more are partially trimmed; positive control 618/618. **Schedule 13.3 → 10–11
wall-days at 5 workers** (the credible saving is levels 2–3; the L4 rate rests on three boxes; ALIVE kills also remove
their subtrees, which the direct figure does not count, so 10–11 is a conservative upper bound). Deployment shape:
node = trimmed child (ordinary certificate) + k excluded tilt intervals (T5 with a range, "T5″"); not yet deployed. The value is the outright kills, not the core enlargement (median
a_tight gain 1.000). Lemma TC (tilt coherence) is exact to machine epsilon as a support-function identity but as a
kill test is 4.8× weaker than the octagon interval test (33 vs 159) because it discards direction; it stays as the
O(1) pre-screen. LP re-solves on trimmed bins and the schedule effect pending.

**What the alive nodes are** (A107, LP dual support drawn directly — the PI's rule):

![the LP support at the four alive level-3 nodes](residue_map/a57_lp_support.svg)

### 1a. Family S01 — "room at side 4" (k5_11 238, k5_16 178, trump5 196)
![S01](shadows/S01.svg)
The support minimises to side exactly 4.000 in 62 combinatorial variants: a slot left empty or singly met. Every such
configuration teleports into a higher-k class that is dead on W. **The LP does not know the teleport lemma.** Technique tried:
SLOT-CROWD incidence rows at the node level — **A109 (2026-09-06, `7daabe6f`): 0 of 18 genuinely-alive nodes killed at
every depth the window licenses, 18 of 18 at the unlicensed depth 0.3, and 0 of 10 LP-dead nodes certified** (the
multiplicity runs fail on 5–32 exact holes at r = 1 already). Two exact facts behind the zero: (i) on a window ending
at side s, SLOT-SLIDE's depth margin and the dilation pad cancel exactly, so the only licensed row is "two non-pin
squares MEET the open slot" (depth 0), and the fourth slot of k5_11 carries no hypothesis above 3.877; (ii) 94% of
the supports do violate SLOT-CROWD, but the rows re-price rather than forbid — the slot boxes are 0.877 apart while a
45° square spans 1.414, so one placement meets two or three slots at once and the incidence budget pays for it
(c = 6.2 vs B = 4.4). Depth breaks the multiplicity and only depth; the prize if a lemma ever licenses depth 0.3 on
this window is the entire remainder (+12.7 wall-days). Until then this family dies by splitting, which the measured
tail says terminates. Side finding: 28 of the 46 sampled "alive" nodes were not genuinely alive (τ < budget, LP
unconverged at the time limit) — a longer LP time on unconverged alive nodes is a cheap re-check when A57 resumes.
**A118 (`405b6522`), the lane-count leaf** (a usable cell that at most one non-pin square can reach, given walls, pin
cores and the conditioned core, is dead by teleport): sound, 0.37 s per cell, reproduces 25 kills the trees paid ~850 s
each for, and finds **13 new** — 1 A57 box, 12 k0 cells conditional on k1_00 — worth 0.05 wall-days. The lane that
stays open is always the same one: 1,323 cells reach LANE ≤ 1 and are saved only because the node's own conditioned
square is allowed to be the second meeter. Corner cells dominate the fires (two walls behind them); BL(1,1), the cell
the crowd LPs leaned on, fires once in 3,580 nodes. Deploy at emission as a pre-screen, never as a re-solve. The
reversed leaf (branch on the two meeters, the complement free) is sound but does not terminate: 26–14,099 pair-children
per node at a 9% per-child kill rate, 2–500 CPU-h to kill one node against 850 s for its own LP — k0_route's C3
("K0-BLOCKED has no finite case list") reproduced at the pinned classes; its value is the free branch. Also from
A118: the octagon PAIR inequality is strictly stronger than Lemma TC (fires at centre distance < 1 vs ~0.7) and
subsumes the TC-leaf obligation; the usable-slot table gains BR(1,0), TL(1,0) for k5_16 and BR(0,1), BL(0,2) for
trump5 after A114's closures; A109-O1 discharged.
Generalises as: *crowding rows need certified depth; depth needs the extension classes dead ABOVE the target side.*

### 1b. Family S02 — the k7 pinwheel (k5_11 184, k5_16 68, trump5 12; carries the deep tree)
![S02](shadows/S02.svg)
![the pinwheel, optimised, with contacts](residue_map/pinwheel_k7_shadow.svg)
![side vs common tilt](residue_map/pinwheel_tilt_curve.svg)
Seven slot squares (BL L-shape 3, BR stacked 2, TL 1, TR 1) + three load-bearing squares at one tilt 48.435° + one
strut/rattler; s* = 3.886746 = s0 + 0.0097 (certified endpoint). Binding contact: f1 on the top wall (Fritz-John 0.87);
the mirror pair f0/f2 next; f3 idle, flat direction blocked at second order. **No open box contains it** (A106): boxes
are alive because the relaxed core cannot see 0.0097 of slack. Techniques: the tight core (in); the tree terminates at
level 4 by pin clashes; or the grain kill of §6. **A111 (2026-09-06, `4c6ace6e`), load-path branching measured:** sound
on 146 of the 286 shadow-explained nodes; ≈ 35 kills at a 2/3 certify rate (n = 3), worth about one wall-day; two
nodes killed end to end. The chain YES kill certifies only for r < s* − s0, i.e. level-4 box widths, because the
fixed-tilt bound is exactly s* − r. The octagon and TC tests kill nothing between load-path boxes at s0 (genuine room:
side-blind rules cannot make a side statement) but fire constantly between a node's own bin and a load-path box — the
**free pair kill**, 113 of 264 S02 nodes at level 1 rising to 200 of 264 at level 4, 19 of 19 S07 nodes from level 2,
confirmed on 57,840 sampled pose pairs. The NO side is a convergence-time problem (dead-unconverged at 80 s, converged
dead at 900 s), 8 of 22 nodes had every NO child LP-dead, certificates 14 PASS / 4 FAIL, fixed-side only until
verify_param supports NO-families. The S07 branch is unsound at level 1 (Trump sits inside the YES region at A57's
level-1 tilt half-width) and usable from level 2. **A112 (`e6690215`), the region tree measured:** on 17 S02-explained
level-2/3 nodes the tree terminates in 77 nodes / 56 LPs / 51 minutes against the old tree's projected 671 nodes and
54 hours for the same region, and kills 9 of 17 — 6 of them already dead by the T5″ root trim, so the tree's own
score is **3 of 11 non-trivial regions**: one free at the root by Lemma TC (bin against pin, a rule A57 does not
apply at emission), two by a certified three-node tree (root, YES, NO; two certificates each; 27–54× less wall than
the old tree on the boxes it kills). Containment checks hold with zero failures. **The branching order is a
tie-break, not a lever**: all four orders land within 73–77 nodes and kill the same set. The two-stage protocol
priced: 2.26× cheaper than a flat 900 s cap. All ten free pair kills are Lemma TC, four of them between boxes the
tree itself introduced — the second conditioned square the tree exists to produce — and none are core–core; the
chain kill never fired at tree depth (its controls are clean; the trees reached only r = 0.0125). On the k0 cells:
0 kills under every order, every LP at η = 0 exactly — removing a support placement from a k0 cell does not move τ,
so branching on corners does not by itself supply the missing logic kills. Corrections of record: η does not predict
the certificate (PASS ∈ [−1.0, −0.25], FAIL ∈ [−0.71, −0.16]); the k0 YES shortcut "a square in a slot box ⇒ k ≥ 1"
is unsound as box containment (A53 stratifies by grid-locked squares) and was never taken. Integration: a resumable
`--region-tree` option in A96's scheduler for nodes alive twice or unconverged at 900 s, falling through to the split
on a wall cap. Certificate accounting: **A117 (`6f160858`) delivered verify_param_v2** (NO-families in the 4-D verifier; 30/30
byte-identical to v1 without NO-families; Lean lemma `nofamExemptIV_sound` proved, axioms unchanged; v1 never
edited) **and Lemma TC as a leaf** (170/170 stored fires reproduced, 1.7 million sampled pairs, 0 counterexamples;
Lean statement frozen as a Prop, the separating-axis step [C]). What v2 buys is window VALIDITY, not wall: 16 of 48
NO certificates re-verified over the window, none of the fixed-side passes became a window FAIL, but the 4-D pass
costs 10× the four fixed sides it replaces (a NO certificate is tiny at a fixed side precisely because the NO-family
exempts most of the container). And the blocker moved to the YES side: a branch box enters the YES certificate as a
core that the parametric core-affine form refuses, so certificate-based region-tree kills stay s0-only; the one
window-valid claim today is the free TC kill of `k5_11_interior_Y0041_D02`, whose boxes are s-independent. Generalises as: *a class-boundary shadow — a dead class's minimiser
sitting on a live class's box; the basin/grain lemma is the transfer.*

### 1c. Families S03–S06 (PI-read) and S08–S53
![S03](shadows/S03.svg) ![S04](shadows/S04.svg)
![S05](shadows/S05.svg) ![S06](shadows/S06.svg)
S03: f0/f1/f2 essentially simple (SNAP → higher k). S04: f0 teleports to BR(0,1). S05: the S07 pinwheel inverted. S06:
the optimal five-square packing (2 + 1/√2) with a unit band = the s(10) optimum 3 + 1/√2, a ten-square shadow (the LP
found room for ten and only fractional room for the eleventh). S08–S53: 1–17 nodes each, mostly level 1, the gallery
has each drawn. With crowd rows out (1a), all of these die by splitting; the measured tail says that terminates.

### 1c′. The PI's first pass over the gallery (review.csv, validated by A121 `4a3b0078`)
83 rows, 219 items, 1,487 (node, cut) rows: **9 node kills, none new** (all A118's lane-count kills; corner cells take
all nine). All 18 `r` readings exactly right; of 64 `ns` items 6 are genuine uncrowded near-snaps, 24 sit on their cell
already (the gallery under-count, fixed in the v2 re-render), 28 are flush along a wall (A101's population), and the
cell names are the identity fit over 784 relabellings. The `st4` token (four flush squares on one wall ⇒ side ≥ 4) is
sound and kills S50/S52/S53 as configurations, not nodes. S34 is the same minimum as S33 (A122: ds 6·10⁻¹⁵), S35 is
not (tilt 6.9° apart), S09 is not S05, S21 is a related near-Trump packing rather than S07. Seven grain rows have
Fritz-John residuals above 10⁻³: nnls fits, not certified load paths. **The structural fact**: 81 of 83 right panels are
rearrangements of their node's support, not snaps (two are tilt-only: S02, S07) — a reading is a pointer to a cell,
never a fact about the node, and a node kill needs the lane test, which the node's own conditioned square blocks in
every close case (6 misses at LANE ≤ 1, M = 1: S37/S38 TL(0,0), S40 BR(0,1), S42 TL(1,0)).

### 1d. The fractional tail (k5_11 151, k5_16 113)
No integral component in the dual support; 303 of 306 top out at four disjoint placements of the five needed. Nothing
to draw. These are what the tree is for, and they are mostly level 1 (110 + 106), i.e. cheap.

---

## 2. The window stragglers (A56 scoreboard **48/52 full-window** after A114, 2026-09-06 `9ef80bfa`)

| class | window status | note | next |
|---|---|---|---|
| k6_23 | **FULL** (A114: resolver on the same certificate closed the 8.4·10⁻⁵ sliver in 0.17 CPU-h) | | done |
| k6_07 | **FULL** (A114: 16-piece slab grid + bisection, 2.3 CPU-h) — **the BL(0,2)/S07 slot is now a full-window kill** | | done |
| k6_27 | **FULL** (A114: resolver-first showed the 4-D failure was s-axis starvation; 14-slab sweep, 0.55 CPU-h) — **the last whole-window k6 class** | | done |
| k5_05, k5_14, k6_21, k5_10 | FULL (A61 pass 5) | folded into the scoreboard | done |
| k5_03 | PARTIAL: [3.82, 3.823345] banked (5.9%) | resolver closes every recorded witness cell but bulk slabs fail: genuinely thin | slab sweep of the rest, ~5 CPU-h (A114 continuing) |
| k5_02 | PARTIAL: [3.82, 3.820223] banked (0.4%) | same | slab sweep, cost projected first (cap 8 CPU-h) |
| k5_12 | OPEN | the gate was never the issue: both LP stages unconverged, certify FAILs at depth 56 and witness feedback drives τ to exactly the budget — no certifiable measure at ε_geo 0.003 with this column pool | slab sweep, projected first |
| k5_13 | A61 running — **the only open window row (scoreboard 51/52)** | | wait |
| k5_02, k5_03, k5_12 | **FULL** (A114 `ee0c18d5`: slab sweeps sized by the slab-width law with the ORIGINAL s0 certificates, 12.5 CPU-h; every earlier bulk FAIL was an over-width slab, never node hardness; k5_12's dead LP route was never needed) | | done |

**k6 and up: nothing open.** Method lessons banked (A114 notes L1–L5): grid a band rather than bisect from the top
(k6_07 as one slab timed out at 1,800 s and both halves failed; as 16 pieces every slab passed at ~190 s); A56's
witness files are truncated and are diagnostics, not gap lists — every closure rests on complete slab PASSes; measured
cost per 10⁻³ of side at depth 48: k6_27 11 s, k6_07 65 s, k5_03 340 s.

Techniques that apply (from this week): (1) SLOT-CROWD rows at the root add budget 2e per usable slot, exactly the
few tenths these are short — but A109's node-level result (the multiplicity runs fail on exact holes even for small
boxes) and A94's own root failure make this unlikely to certify; try only after the resolver; (2) A96's resolver re-verifies the same certificate on the 4-D witness cells (closed 20/20
in A100) instead of re-solving the LP; (3) bisection of the side window for the two fragments. The tight core does not
apply (no boxes).

---

## 3. The protected tier (Trump's 16 sub-skeletons)

![Trump](residue_map/trump.svg)
![S07 beside Trump](residue_map/s07_vs_trump.svg)

![S33 beside S07 and Trump](residue_map/s33_vs_s07_trump.svg)

Trump's skeleton carries at least four exact local minima now: Trump (ŝ), S07 (2 + 4√2/3), S33 = S34 = K19 (3.91693,
smooth interior critical point, all eleven squares load-bearing), S35 (3.91742, distinct), plus S38 (3.92891, degree 9)
on k6_21 (known_results 26d). All are separate basins: S07's crest toward Trump is +0.0011, S33's +0.038. The local
certificate applies to S33 and S38 with no Trump cut out to r = 0.2 and 0.68.

trump5 (BL[2,1] + BR[1] + TR[1]) contains Trump, so its kill is a residual tree ending in Trump's basin (rBasin =
3/2000, A63). A60's cover ran at 0.781 kill rate; paused. Its 325 alive nodes are, by A107: S01 196 (room), S07 18
(the exact 45° packing above — needs k6_07's band to make BL(0,2) a usable slot), S02 12, S03 16, S05 7, others small.
The other 15 protected classes are priced at 3,500–4,200 CPU-h by A100's pilots (k4_11, k3_02 end to end; η law exact
on 54/54 cover nodes; parametric route carries to protected classes; the resister branch at level 2 killed 1 of 16).
Everything that kills S01/S02 in A57 kills the same families here. Generalises as: *the class containing the optimum
needs a basin certificate; every other class needs only crowd rows and a tree.*

---

## 4. k0_00 — the frame residue

![the strict record and its drain](residue_map/strict_3p9907_drain.svg)
![the record's drain](residue_map/record3985_drain.svg)
![A104: the grid closes; the lowest fully-held packing at 4.000237](../attempts/A104-grid-lock/results/lock104.svg)
![A105: the one-wall obstruction](../attempts/A105-lockfree/results/hookwall105.svg)

Proved chain: K0-FREE/teleport (Lean) → K0-BLOCKED residue → NOCRIT-SEL (every intruder anchored under translation) →
Lemma ROT (every intruder HELD under translation and rotation at the weighted-Ψ minimiser) → residue RES-LOCK: a
K0-BLOCKED packing in W with every intruder locked. **Conjecture LOCK-FREE⁺(< 4): none exists.** Evidence: 0 of 12
corpus packings and 0 of 443 descent endpoints below 4 are fully held; the closing iteration (follow the contact
manifold) frees a corner every time below 4; the first fully-held packing is at 4.000237; even the ε-grid is
LOCK-FREE. What a lock is made of: 3.3 square–square rows + 1 wall row per intruder, so the proof is a supply count
(the crowd arms cannot furnish three square rows to all eight corner members at side < 4), not a wall budget. The
one-wall lemma is false (two held walls below 4 exist: the mixed hook pair, closed form 2 + (2−s)/c + tan(θ/2)). The
tree alternative: 9,300–21,700 CPU-h (A99). **A113 (2026-09-06, `6409396b`): where that cost sits.** Measured on the
cell's own box, only 1.4% / 4.6% / 18% of the projected cost is within η = 0.05 / 0.1 / 0.2 of the k ≥ 1 manifold, and
the five alive level-1 cells sit at η 0.23–0.37 — but that is the wrong object: the tree conditions on an interior
square, and Trump's interior squares are the tilted ones (its cells sit at η = 0.366). On the right object, the LP's
dual support, the PI's hypothesis holds exactly: cells the LP kills have supports with ≤ 1 simple placement matching
only S01 (room); the un-killable cells (0 of 26 with position distance ≤ 0.05 ever killed; the six most resistant,
τ up to 10.5, all at distance ≤ 0.02, and τ climbs under row generation so more LP time cannot kill them) have
supports that are 2–6-slot partial skeletons of near-critical shadows — one alive cell matches S38 (trump5 boundary,
3.9289) slot for slot, an A85 FAIL matches S07 at Jaccard 0.83. Position distance predicts τ (Spearman −0.44 inside
every tilt bin), tilt distance predicts nothing, LP wall is flat in η. Consequence: a *re-branching* rule — branch a
cell on the slot its support keeps occupying, readable only after the LP — the k0 face of A112's dual-guided
branching, with the YES side handled by K0-FREE/teleport plus crowd rows (licensed at depth 0 at fixed s0, since
every k ≥ 1 class is dead there) and the NO side by the LP without its support. Also: the k0 tree has zero logic
kills (it never branches on corners), and A107's gallery missed the 264 k0 LP jsons through a glob bug. **Fixed
(A107 Part II, `87ed93bb`): 217 alive k0 cells, 30 shadow values explain 161, 56 have no integral support.** The
dominant one is **K01, "room at side 4.000", 84 cells** — the k0 twin of S01; below it the k0 spectrum reproduces the
A57 one down to K06 = the k7 pinwheel at 3.886745 reached independently from k0. One correction to the A113 reading
above: a slot-set match is not a packing match — A113's S38 "exact" cell minimises to 3.914 (K04), and its S07 cell
to 4.000 (K01) — so the un-killable k0 cells are mostly room, not near-critical grains. Since a k0 packing with a
singly-met corner is K0-FREE (teleport, Lean), K01's configurations are dead by theorem and the tree's LP does not
know it; unlike A94's slot rows, the four corner cells are far apart so a square meets at most one — no multiplicity
re-pricing. **A115 (`f37487d3`): corner rows at the node level do not kill either** — 36 cells × 3 depths, 108 LPs,
one attributable certified kill (a level-3 cell), zero of the genuinely alive cells. The failure mode is new, not
A109's: the crowd certificate charges the SECOND meeter of each corner, and the K01 supports have none — every corner
of all 84 supports is met, by a single DEEP meeter (depth ≥ 0.30 in 296 of 486 incidences), never empty; that is the
K0-FREE teleport hypothesis exactly, and no crowd-weighted row can price it. Worse, at depth 0 every Trump image
realises nine corner incidences against a guaranteed budget of eight (its tangent squares count), so the root crowd
LP can never pass at depth 0, and at depths 0.05–0.1 the measured incidence rate c ≥ B in 100 of 101 runs — no
weight e can kill. **The cheap control beats the mechanism (A115 T4, `71a5b20b`): a plain 240 s warm re-solve from each cell's
stored rows and atoms, no rows added, certifies 10 of the 55 open k0 cells reached — 7 of A99's plain level-1 cells,
two of them never run before — for 5.1 CPU-h, removing 300–700 CPU-h from A99's frontier.** The stored node results
were simply row-generation-incomplete. Four cells are CONVERGED-alive (τ = budget, minmass 1, converged): no LP time
kills them, they need a different hypothesis — the two-meeter cover (A118 T4) is the candidate. **Continued (A115 T5, `e7a53299`): 17 of the 216 level-1 root cells are now certified dead (16 new), plus 6 level-2, 1
level-3 and 4 A85 nodes, for 15.4 CPU-h in all — 770–1,780 CPU-h off A99's frontier, a 48–111× return; the PI's 14
`i` readings from the gallery review certified 14 of 14, seven of them level-1 cells no queue would have reached.**
Seven cells are converged-alive (τ = budget, minmass 1, converged; one is a Trump-image cell that must be alive): no
LP time kills them; they are the two-meeter-cover candidates. 34 never-run level-1 cells and most open level-2/3
cells remain; the pass continues. Generalises as: *for any n, below the grid side ⌈√n⌉ every blocked packing
has an unlocked intruder — the drain theorem; the hook/chain formulas are one-wall tools with 4 → ⌈√n⌉.*

---

## 5. Lean / TCB

TopLevel roster: K0-O1 + chain replays + ShellKill (Crowd, CrowdZone, Slide, PinnedSlide, Ceil, Composition);
teleport_packing, T5 (core_meet_same_square, unchanged by T5′), N1, M1, T11. Remaining axioms: `stratum_kill` (the
replay of every class certificate on W), `trump_residual` (the protected tier + basin), `a22_exact_structure`
(Trump's exact data). Every leaf above has a Lean shape written (noroom.md §8, lockfree.md §7, slot_crowds.md).

---

## 6. Bottom-up: grains, and how to expand a kill in phase space by more than 0.004 (PI question, 2026-09-06 02:00)

The 0.004 is a ball: side is Lipschitz in the poses, S07 is 0.0085 above s0, so a ball of radius ~0.004 around S07 is
certifiably above s0, and a level-1 box is 0.14 wide. Balls are the wrong shape. **The right shape is the grain**: the
set of configurations sharing S07's load-bearing contact graph G. Inside a grain the side is a closed-form function of
the tilts alone (A108: 3s = 6 + 8·(√2/2) for S07; A105's chain/hook formulas in general), because the load path is a
wall-to-wall chain and a chain's length depends only on its members' tilts and contact types. So:

* **Grain minimum.** For a load-bearing structure G, s_min(G) = min over the grain of the chain length — an algebraic
  minimisation in the tilts (for S02: the curve `pinwheel_tilt_curve.svg`, minimum 3.886746 at 48.435°; for S07:
  exactly 45°, 3.885618). If s_min(G) > s0, **the entire grain is dead**, whatever the rattlers do and wherever the
  free squares sit — not a ball, a semi-algebraic region of phase space with diameter of order 0.1–1.
* **Grain boundaries.** The PI's observation: rotating the pinwheel changes many contacts, but s_min is continuous
  across every boundary except the one where the tilted square's corner drops into the gap between BL(0,2) and
  BL(0,1) — i.e. the boundary into Trump's grain. Contact changes that keep the same load path keep the same chain
  formula; only a change of the load path can lower s_min. So grains form an adjacency graph labelled by s_min, and
  **a kill floods along it**: every grain connected to a dead grain by boundaries that do not change the load path is
  dead by the same formula. The live component is Trump's grain and nothing else.
* **What is proved.** Chain length as a tilt function for axis-aligned columns (CHAIN-AX [T]); the hook formulas
  (HOOK-α/β/βα [T]); the exact grain minima for S02 and S07 [T]; the tilt sweep [M].
* **What is missing — the box-to-grain map.** A box's configurations need not have the load path at all (fewer
  contacts, flexible). The bottom-up theorem that closes this is Morse-style: the side over a box attains its minimum
  either at a local minimum, which IS a grain with a known s_min, or on the box boundary, where the flow leaves the
  box (A106 measured: always the boundary). So "min side over the union of boxes that flow into each other ≥ min over
  the grains they reach" — and the grains a class can reach are finite (A107 found 53 values across 1,566 nodes).
  The certificate would be: (i) the list of grains of the class with s_min > s0 exactly (algebra, per grain),
  (ii) a proof that no other local minimum exists in the class's phase space below s0 — which is the class kill
  itself, circular unless (iii) the flow from every box is certified to stay above s0, i.e. a Lyapunov-type bound.
  The honest status: (i) is in hand for the top grains; (ii)/(iii) is the theorem. A110 (Fable) is briefed on it:
  state GRAIN-FLOOD exactly, prove the load-path continuity across boundaries, and give the box-to-grain certificate
  or the exact obstruction.
* **Cheap instance to try first.** S07's grain around trump5: enumerate the contact changes as the common tilt runs
  from 45° down to 41.6° (the crest) and up to 60°, verify s_min(θ) ≥ 3.8856 across every boundary except the Trump
  one, and count which of the 18 S07 nodes' supports lie inside the swept grain family. If all 18 do, the grain kill
  is 18 nodes for one algebraic certificate.

Generalises as: *the bottom-up side of the search is a flood over the grain adjacency graph; the top-down tree only
has to reach grains, not points.*

### 6.1 A110's verdict (2026-09-06, `docs/proofs/grain_flood.md`, `411cc79d`)

![the box-to-grain obstruction](../attempts/A110-grain-flood/results/box_to_grain_110.svg)

**GRAIN-FLOOD as stated is true and empty.** A packing at side ≤ s0 makes the global minimum over the class's compact
phase space a local minimum ≤ s0, so "every local minimum ≤ s0 lies in Trump's grain" is the class kill itself. Both
certificate shapes reduce to it: the only quantity monotone along a flow from a box is the side, which is the node's
own bound; and the grains reachable from a box are the selection census (≈ 8⁴⁵ separating-axis choices for five free
squares), which is what the tree prunes by localising — the existential-filter law again. The obstruction, drawn:
node c0_Y0324's box holds its LP support's rattler (tilt 53–64°) and no load-bearing S07-family square at any tilt;
the nearest is 0.21 away against a half-width of 0.07.

**What is proved and n-general.** Lemma GRAIN-LP: at fixed tilts and a fixed separating-axis selection, the side
minimum is an LP whose dual is a balanced force system, i.e. a load path — the same object as the leaf certificate's
dual. Lemma INHERIT: the chain formula survives every unloaded contact change. Theorem CONT: s_min is continuous in
the tilts; the PI's dichotomy is about which rows are loaded, not about continuity. GRAIN-ROW: a conflict row on the
support's cells, sound, kills the support pattern, not the node (yield open).

**The menu.** Trump, S07 and S02 are three kink minima of one family of chain formulas in the common tilt θ, with
u = cos θ + sin θ: the ladder Λ(θ) = 2 + 4u/(u² + 1) (minimum 2 + 4√2/3 at 45° only; = 4 at 0° and 90°, the grid), the
column chain Y(θ), the diagonal chain D(θ) = 2 + (2 + cos θ)/u, and the gap chain F_T(θ) = 2 + (2 + sin θ)/u = D(90° − θ).
S07 = Λ crossing Y at 45°. S02 = the triple point sin θ cos θ = 2 sin θ − 1 of Λ with D, θ* = 48.43512°, s* = Λ(θ*) =
3.886746029. **S07's Trump boundary** is at sin θ cos θ = 2 cos θ − 1, θ = 41.56488°, where f0's vertex reaches
BL(0,1)'s corner and the basis changes to F_T; the crest there is exactly S02's value 3.886746029, and F_T then falls to
ŝ. **Corollary TRUMP-GAP: ŝ = 2 + (2 + sin θ_T)/(cos θ_T + sin θ_T) at Trump's tilt, to 40 digits.** So on the S07
sweep exactly two load-path changes matter: 45° (both formulas ≥ 2 + 4√2/3, the flood crosses) and 41.565° (the
formula drops toward ŝ, the flood stops). Sweeps with all eleven squares free confirm each formula to 10⁻⁷ with one
loaded set per side while thirteen contacts flicker unloaded. S02's family never touches Trump's grain.

**T4 counts.** S07 family: 0 of 19 supports inside it (the six f1 nodes match Trump's grain at 39–41°, the canary;
the cover nodes draw the skeleton at 21–44° or 58–69°). S02 family: 56 of 267 (37 level 1 + 19 level 2 of A57; none of
the 14 deep nodes, none of A60's or A61's). Price of the sound consumer: two one-variable inequalities per family —
but it kills support patterns, not nodes, so the tree price is unchanged.

**What this leaves of the idea.** The grain menu is real, exact, and three-for-three on the known minima; it is the
right language for the paper's "why Trump" and for higher n (the same four chain formulas with ⌈√n⌉ in place of 4).
As a kill it needs the localisation the tree provides; the honest form is GRAIN-ROW inside the node LP, priced next.

### 6.2 The local certificate (A116, 2026-09-07, `74a34f96`, `docs/proofs/local_certificate.md`)

**Theorem LOCAL, proved and measured.** Around a known minimum with load-bearing squares L and class pins P, the
selection tree over the near pairs (COVER: separating axes per pair, ≤ 8^k leaves, impossible ones by interval) has
leaves whose minimum side is the chain formula (LEAF: LP duality = balanced force system); the neighbourhood N is
dead iff every possible leaf's minimum over every tilt cell exceeds s0; nothing about the other squares is assumed
(DROP). **Certified radii, 20× A111's: S02 dead at (r, ρ) = (0.2, 10°) and (0.05, 20°) in k5_11's frame; S07 dead at
(0.1, 40°) and (0.2, 10°) in trump5's frame with the single cut F_T(θ) > s0 (θ > θ_T + 6·10⁻⁵°).** Every N confirmed by
10⁴ samples, Trump outside. A111's r < s* − s0 law was the dropped ambiguous rows letting the LP escape into the box
rows; none of (i)–(iii) remains. The PI's stability-radius route is confirmed pair by pair
(`attempts/A116-local-selection-tree/notes/stability_table.md`): S07's chain contacts are forced to 0.18–0.23, f4 against
BR(0,0) to 0.254 at fixed tilt — the PI's 0.25 — and the limiter is f0 against BL(0,1), whose vertex sits 0.057 below
the corner: the Trump boundary. **Limiter at r = 0.3**: a genuine rearrangement of L ∪ P that the dropped squares
would block (S02: BR(0,1) leaves its slot, f3 climbs onto it, 3.8733; S07: the ladder shears, 3.856) — adding the
blockers as boxes extends it (A119). **Consumer: 72 of 184 k5_11 and 23 of 68 k5_16 S02-explained alive nodes have their
support inside a certified N**, 4–445 s per N shared by every node inside it; the NO side is what remains. Precision
from A96's replay (`ef646f0f`): of A112's 17 stalled nodes only 4 lie inside a certified N and 2 close outright (YES
free, NO already dead), so the overlap with the current stall set is thin; the value is in pointing the region tree at
the ~70 other in-N alive nodes, which is running offline. YES kills by the local certificate are tagged, not counted
with frozen-verifier kills, until A119's rational/Lean form lands. **A119 (`e07f8808`, `71d18eba`) made it exact: five certificates (S02 at (0.2, 10°), (0.1, 10°), (0.05, 20°); S07 at
(0.2, 10°), (0.1, 40°)) with 53,094 dead leaves and 769,440 rational multipliers, all VALID under an independent
dyadic-interval checker that imports no numpy and rebuilds every relaxation row itself (1,072 s); `Local.lean` builds
with 0 sorries and exactly one project axiom, Lemma SAT for interiors (`sat_selection`), the closed-square form being
already proved in CaseSat.** Two corrections to A116: (i) three of its four "capped" ρ ≥ 20° cells are ALIVE — a
checked packing of L ∪ P below s0 exists inside N (S07 (0.2, 20°): the ladder shears at 65°, 3.8734; S07 (0.2, 40°):
3.8696; S02 (0.2, 40°): 3.8767) — A116's own witness files already contained it under a `capped` label; (ii) the
blocking squares as boxes do NOT extend the radius (six free bodies, 16–23 near pairs; only S02 (0.1, 5°) closes),
though they do lift the closed part's minimum, so the certified radii stand as listed. Tilt-cell sharing implemented
(99.4–100% census hits; the LP is the whole cost). Consumer unchanged at 95 of 252. Open: `LocalDead` for a concrete N
inside Lean (the recorded cover is checked outside), the interior-SAT axiom.
