# The budget — the live estimate of remaining compute, and where it goes

**Rule.** This file is the one place the total lives. Every landed measurement that changes a number updates the row,
its provenance, and the date; nothing else in the repo quotes a total without pointing here. Lean replay is excluded
(the PI's convention). Machine: i7-12700K, 6 usable LP slots with BLAS pinned; "wall-days at 5" assumes five
workers.

Last updated: **2026-09-08 22:30** (A149's re-price of A57 at 08:10; A156's day shift measured `D_2` ≈ 0.11 and the level-2 LP rate).

## A. The total

| layer | remaining | central | range | wall-days at 5 | provenance | levers not yet in the number |
|---|---|---|---|---|---|---|
| A57 window trees, k5_11 + k5_16 | **frontier counted id by id (A149, 2026-09-08): 2,052 nodes owe work on side 1** — 325 cover children never screened, 1,432 screened-but-unsolved LP jobs (L1 214, L2 1,117, L3 101), 201 recorded ALIVE (157 already deepened, 44 not), 94 recorded FAIL; 3,052 ids are DEAD. Plus **4,683 level-1 "ok" children on sides 2–4** of the δ = 1e-2 grid (`lemmas.md` T23). Of the 1,995 unsolved queued jobs, **563 (28 %) are already dead** and `mkqueue137.py` still hands them out | **≈ 1,800 CPU-h** (A149 `reprice149.json`, CENTRAL) | 1,150–3,150 | **≈ 15** (9.6 LOW – 26.0 HIGH). §B's recursion made absolute: `E_L = (1−g_L)[c + 8 d_L E_{L+1}]`, `E_5 = 0`, at the night's **measured** rates — `g` = 22.5 / 24.8 / 32.0 / 87.5 % by level, `d_1` = 23.5 %, `c` = **283 s** (LP + s0 exact certificate + frozen verifier, no 4-D verify: the window is the four-side grid, not a per-node pass), `D_2` = 0.113 (A96, the one input with no measurement under the exact cores). **The rise from ≈ 800 is one missing term, not a regression:** the standing figure was 6,418 ok children × 431 s with **no descent**; the node is now *cheaper* (283 s → 504 CPU-h on the same count) but one ok child costs **3.76 nodes** (`F_1/c`), because `8 × d_1 = 1.88` children at `E_2` = 415 s each. Corrected input: PAUSED v3's 27.4 % level-1 geometry and 78.8 % LP-kill are measured over 849 children of which **573 were re-screens of ids already in the corpus** (the shard index moved and `emit137`'s `done` check reads one shard file) — on the 276 genuinely new ones the rates are **22.5 %** and **76.5 %**, both of which move the schedule up. Previously: ≈ 800 / 6.4–7 (`lemmas.md` T23 grid); before that 10.5–11.7 (A124 `97aa4e9c`, relative to a 13.3-wall-day baseline) | **A149 (this row, 2026-09-08)**: `attempts/A149-a57-reprice/{notes/reprice.md, notes/dupwork.md, results/reprice149.json, results/frontier149.json}`; rates A137 `b91a2813`; grid counts `attempts/A57-shadow-trees/notes/lemmas.md` T23; model A124 `97aa4e9c` (`code/schedule124.py`) | **the 900 s re-check is NOT a lever: by the campaign's own rule (η < −0.005τ) the night's "11 kills" are 1 strict kill and today's 21 are 2 (both already known), the rest knife-edge at \|η\| ≤ 10⁻⁹ — 2 strict kills for 15 CPU-h against 54 free geometric kills banked in seconds; recheck96 never certified and never wrote node jsons (recheck124 now persists them)**; **PIN-CLIP (A131 `32d63560`, 2026-09-07): of the 607 unclosed nodes (414 ALIVE + 193 FAIL) 132 (21.8%) clip to EMPTY by exact geometry, 112 of them by the already-deployed trim — a backlog collectable in minutes (sweep running); on 10 alive nodes the clipped LP moved 5 from η ≈ 0 to η ≤ −0.5, 2 CERTIFIED dead through the frozen verifier, 3 cert-FAIL with holes (resolver path); modelled schedule effect only ≈ 0.4 wall-days but the LP effect is not in that model**; the POLYGON CORE (A132 running: 2 of the support columns in each alive L3 node are impossible under the hypothesis yet pass the axis-aligned core); the local certificate as YES leaf (**A136 `PENDING`, 2026-09-08: F-COVER fixed at emission — the NO zone rounded INWARD and `ZONE ⊆ BOX` checked on the WRITTEN rationals, so A120's `YES ∪ NO = H` is a tautology at the level of the files; A120's 22 certificates 22/22 re-certified, and the board went 4 CLOSED / 11 targets touched → **15 CLOSED / 24 touched** of the 35 in-N targets at a mean 2 932 s per closure, level 3 cheapest; 54 PASS / 6 CAP / **0 FAIL** over 60 attempts at `--rounds 6` wall 2 600 s, so certification is no longer the binding constraint — the wall is, and 15 genuine survivors in 5 nodes are beyond any certifier budget**; was A120: 4 of 9 closed); the Y0381 hang; **A137 (night of 2026-09-07/08) measured the two numbers this row's schedule rests on.** (i) **EXACT-CORE KILL RATE = 46 / 161 decided = 28.6 %** over 163 of the 305 surviving-ALIVE nodes re-solved with A135's exact certified cores under the FROZEN `verify_case.py` (15.5 CPU-h, median 426 s/node) — so D.1's 28 CPU-h chore now has a population rate, not a 20-node sample, and it converts ~29 % of the ALIVE queue at ~0.34 CPU-h per kill; A145's `frac_exact` ranking gates at the top (≥ 0.60: 25/66 = 37.9 %) but its "0 of 7 below 0.45" does NOT survive n = 63 (0.30–0.45: 15/63 = 23.8 %), so the 0.30–0.45 band must stay in the queue. (ii) **LEVEL-2 RATE = 27.5 % dead by geometry before any LP** (464 of 1,690 fresh level-2 children through pinguard-at-exact-core + T5″ + T5‴), against the **13.74 %** this row's schedule credits; the directly comparable incremental-over-T5′ figure is 8.6 % at `nsub = 1`, the difference being that the exact pin core moves boxes out of the incremental bucket into T5′. Level-1 emission: 27.4 % dead by geometry (245/893) and **78.8 % of those that reach the LP are certified dead** (149/189) — both on the mixed population; see the wall-days cell for the new-id split. Full accounting `attempts/A57-shadow-trees/PAUSED.md` v3 §C. **A149 (2026-09-08), and this is now the top lever on the row: `D_2` — the share of an emitted level-2 child's LP outcomes that still owes a split — is the single unmeasured input and it spans the whole estimate.** All 1,117 level-2 LP jobs are queued and untouched; A96's 0.113 is from the old tree with the stock cores. At `D_2` = 0.05 the row is 1,386 CPU-h (11.6 wall-days), at 0.113 it is 1,777 (14.8), at 0.20 it is 2,412 (20.1), at 0.30 it is 3,279 (27.3). **Draining ~300 level-2 LP jobs costs ≈ 24 CPU-h — a fifth of a wall-day at 5 — and collapses a factor-2.4 spread in an 1,800 CPU-h row.** Nothing else on this row has that return; do it before any other A57 work. **A156 (day shift, `9a18b867`, 28 CPU-h at 2–3 workers under chore contention): 339 kills — 269 certified by the frozen verifier, 70 by geometry; level 2 decided 93 jobs at 89.2 % PASS in 122 s median (against 72.4 % / 236 s at level 1), so `D_2` measured on the first 93 is ≈ 0.11 — A96's 0.113 stands and the row sits at its central ≈ 1,800 CPU-h / ≈ 15 wall-days; level 2 gives 2.4× the certified kills per CPU-hour and the queue now runs level 2 first. Also measured: the geometry kill rate is a FRONTIER property, not a level property (41.6 % on children of alive L2/L3 nodes, 0.6 % on children of fresh LP survivors), so any per-level geometry credit over-prices where the frontier is LP survivors. Open work 423 after ledgers.** Two further free cuts found in the same pass, both bookkeeping and neither touching soundness: **563 of the 1,995 queued jobs (28 %) are already dead** by a supersession of the node or an ancestor (`mkqueue137.py` tests recorded and claimed ids but not ancestry — ≈ 90 CPU-h), and **`emit137.py`'s `done` set reads one shard file instead of globbing `_s*`**, which is why 573 of the night's 849 level-1 children were re-screens and why ≈ 8 of that lane's 14.85 CPU-h went to re-proving already-PASS nodes. **A149's own day lane (2026-09-08/09, 29.7 CPU-h): the A57 ALIVE + FAIL population is DRAINED — 240 nodes, 93 certified kills under the frozen verifier, 0 WALL-CAP, 0 ERROR, and NOT ONE node reached FAIL-with-holes, so `verify_case_v3` was never invoked.** The decision-relevant split is by PRIOR VERDICT, not by level or by band: **recorded FAIL 62.5 % (70/112) at 0.220 CPU-h per kill against recorded ALIVE 16.0 % (20/125) at 0.693** — a FAIL is a node whose LP was already below budget and whose certificate merely had holes that a larger core closes, so **the exact-core chore should be run FAIL-FIRST** (A137 ran ALIVE-only; `targets137.py` defaults `--include_fail 0`). A145's `frac_exact` on n = 237 is sharp and monotone on ALIVE (100 / 50 / 28.2 / **7.3 %** by band) and nearly flat on FAIL (73.9 / 74.1 / 50 / 60 %), which settles PAUSED v3 §C.1's untested `< 0.30` band: 4× weaker, not worthless. **Third id-collision finding, and it cost certified kills: 19 open G1-tree nodes are masked by a dead L1-tree row of the same id** and had never been offered by any queue, because `targets137.py` builds a last-wins map over `tree_*.jsonl` and an id names a node in BOTH window trees (PAUSED v3 §C.3). Run as their own lane they gave **14 kills of 19 (74 %)** — the highest-yield population of the day. Key the corpus by **(tag, id)**. With A149's 93 kills folded (but NOT A156's 339, which are not yet in the frontier file) the id-level frontier is **1,817 owing** (down from 2,052) and the re-derivation gives **1,721 CPU-h / 14.3 wall-days**, so the ≈ 1,800 central here is if anything an over-estimate and a joint re-derivation over both lanes' ledgers is owed. Also refreshed: the dead-but-queued LP jobs are now **728 of 1,995 (37 %)**, up from 563, because every kill adds its subtree |
| Window stragglers | **CLOSED — scoreboard 52/52 full-window.** A146 closed k5_13, the last row, with the ORIGINAL A56 parametric certificate swept in 58 slabs of 10⁻³ (58/58 PASS, 0 bisections, 1.5 CPU-h, C2 triple-PASS); its A61 re-solve route is dead for a measured reason, not a resource one (dτ/dε = 119–132 against 57–90 on every converted row, so ε_geo 0.003 costs 0.34–0.38 of a 0.38 slack: at the 900 s cap stage B lands on τ = 6.000000 exactly). A114 had closed k5_02, k5_03, k5_12, k6_07, k6_23, k6_27 the same way (12.5 CPU-h) | **0 — done** | — | 0 | A146 (this row); A114 `ee0c18d5`; scoreboard 52/52 | none needed |
| Protected tier, 15 classes excl. k0_00 | conditioning trees per exact stratum; trump5's residual tree — **A60's alive trump5 population is down 87 of 218 (A149, 2026-09-09)** | **3,800 CPU-h** | 2,900–6,300 | 32 | A100 `a100_projection.json` (2026-09-05); trump5 exact-core lane A149 (`results/day149_a60_summary.json`) | tight core + trimming untested here (same box/pin geometry, expect a similar fraction); η-gating already in the number. **The exact core IS now measured on this tier and it is the strongest lever it has: A149 re-solved all 218 alive trump5 nodes with A135's exact certified-maximal core on the CONDITIONED square and killed 87 (40.7 % of 214 decided) in 17.1 CPU-h under the FROZEN `verify_case.py` — 0.20 CPU-h per kill, no verifier change, no Lean change, 4 WALL-CAP (never a verdict) and 0 FAIL-with-holes, so no v3.** A60's pins are already exact boxes and must KEEP the corpus core `16383999967232/32768001953125`: at `a = 1/2` the cores of two slots exactly 1.0 apart would touch and the `budget = n − #cores` bridge would lose pairwise disjointness (measured gap at the corpus core 6.2e-8), so the whole gain is H's — and it is much bigger than A57's pin gain, **×1.048 per side on average and ×1.109 at most** against A57's ×1.006. Ledger `attempts/A149-a57-reprice/results/superseded_by_exactcore_a60_A149.jsonl`, driver `code/node_a60.py`, fold-in paragraph in A60's `notes/ledger.md`. If the other 14 classes behave like trump5 this row is over-priced by of order a third, but that is one class measured, not a rate |
| k0_00 | the frame residue; tree at 9,300–21,700 CPU-h, or one theorem — **warm re-solves complete over every reachable open cell (A115 T4+T5+T6 `0d4c79fd`, 2026-09-07): 22 of the 216 level-1 root cells certified dead plus 13 level-2, 2 level-3 and 10 A85/A99 nodes for 29.8 CPU-h, removing 1,023–2,372 CPU-h (34–80× return); 14 of 14 of the PI's `i` readings certified; 71 stage-A kill candidates still lack the 900 s continuation (5 of the last 27 closed that way); 12 cells were converged-alive; **s3_far certified dead under the frozen verifier with exact cores (A140 `476f9108`), 3 kill candidates unconverged, 11 remain** — the same exact-core re-emission A135 named for A57 applies here and needs no verifier change** — **A141 (2026-09-07) then ran A118's lane leaf with A132's POLYGON cores over all 173 open k0 cells and killed 26 further distinct level-1 cells (A38 l1 idx 156, 157, 162–167, 198–215) + 1 new level-2, worth 1,130–2,620 CPU-h at A115's per-cell rates (43.2–100.3 CPU-h per level-1 cell, 5.4–12.5 per level-2), plus certificates for A118's 8 level-2 + 3 level-3 k0 kills (45–105 CPU-h); every lane kill is conditional on k1_00 (K0-O1) and pending two Lean obligations, and `s3_far_BL389484_TR018470` dies unconditionally by a pair contradiction — 1 of the 12 converged-alive cells removed** — **A143 (2026-09-07): the CORNER-FIRST root measured and priced, and it is NOT a saving.** Conditioning on the BL corner meeter instead of an interior-zone square is a sound independent cover (216 level-1 cells, 126 after the D4_BL /2, over the zone [1/2, a_w+√2/2]², a_w = 1.0255101 by K0-WIDEN; proved + 22,078 sampled poses / 0 misses) whose geometry kills **0 of 216** — the container clip empties no cell, K′ never leaves the container, and the K′ lane leaf cannot fire because the conditioned square is itself a BL meeter (M = 1, so the kill needs LANE(BL) = 0; 0 kills with A118 cores on all 216 and with A141's polygon cores on 27). The DOUBLY-MET form carries all the geometry: **9,638 of 11,772 canonical pair cells (81.9 %) emptied by three exact prunes for 90 CPU-s** (7,919 centre-distance, 1,313 K′-vs-K′, 406 A131 per-tilt-sub-bin), 2,134 survive, 12,000 sampled realised BL 2-crowds / 0 violations — but the LP does not convert it: at matched 240–285 s the corner-first level-1 slack is η = −0.044/−0.633/−0.000 (budget 10) and −0.083/−0.077 (budget 9, two cores) against A115's interior level-1 distribution (n = 89, median −0.729, 20 % at ≤ −1), so a second conditioned square at the SAME corner buys no slack for a whole unit of budget. Price: **3,800–8,900 CPU-h** (single root, decision depth 3) / **8,000–18,800** (pair root, depth 2) against this row's 12,000. Also of record: the k0 root definition carries NO simple-square tolerance (Lean `OccupiesSlot` is exact), so no tilt exclusion is available in the ∀-packings form — **A154 (2026-09-08) closes the corner-incidence row NEGATIVE and hands back a free screen.** A150's (R6) ("the widened corner boxes are s0 - 2a_w = 1.826 > sqrt2 apart, so a K0-BLOCKED packing has >= 8 of its 11 squares meeting a corner box") is A115's `d0` row verbatim, not a new row; A150 sec 6 item 1's contrast with "four separate >= 2 rows" is wrong twice (A115 ran the aggregate, and four per-corner rows would DOMINATE it). Measured: **0 attributable kills in 29 LPs, eta strictly WORSE on 26 (mean +0.65)**, canary `l1_153` alive; `c = dtau/de >= B` in **23 of 23** (R6) runs (min c-B = 0.000; on the eleven converged-alive cells with A135 exact cores c = 9.0-10.2 vs B in {7,8}) because a_w = 1.025520 > 1 makes the four boxes cover 28 % of the container and a covering measure is cheapest in the corners — the row prices what the LP wants to buy. **The deployable part is the ZERO-LP SCREEN**: on a CONVERGED record, c >= B at the stored dual PROVES the row cannot lower eta at any e — 166 open k0 cells in **5.2 CPU-s**, 8 of the 13 converged settled. A (R6) pass over the 216 level-1 cells would cost **9.5 CPU-h at 159 s/cell and remove 0** (net -9.5). Lemma ID (A89-O3) adds nothing: the area form is vacuous by inspection (4(1-d)^2 <= 4 < 4.0318) and the certified ">= 1 corner DEEP(0.3)" row has c_ID >= B_ID on **166/166** (B_ID = 0 on 87). Separation independently re-verified on 24,468 dual placements (max multiplicity 1, 0 disagreements). PROTECTED TIER: the class row is licensed NOWHERE (every k <= 4 class's corner extension is itself protected); trump5 has exactly ONE non-simple corner (TL, B = 2, s0-only via the PARTIAL k6_23), k5_16/k4_13 have none. For A150's price: rooting at the DEEPEST corner (D4 + Lemma ID) leaves **110 of 206 band cells**, a factor 0.534 on ONE corner — 5.28e6 -> 2.82e6 CPU-h, still 235x this row (`attempts/A154-r6-corner-row`) — **A159 (2026-09-08) closes the near-miss corners and credits this row NOTHING.** A141's 44 k0 NEAR-MISS corners were re-examined exactly: all **28** of its recorded two-crowd witnesses are real (interval arithmetic at 60 dps; the poses are container-frame, H lies in its own box B in every one — A148's "corner-frame transport bug" is A157's, not A141's, and its −0.026/−0.036 reading was measured against the UNWIDENED unit cell, which differs from the leaf's widened box by exactly `W0 = 0.0255100742`), and a direct joint search raises it to **30 of 44**. By Lemma A159-1 no lane leaf can ever fire at those 30; on the **14** remaining the joint split closed **0 of 9 distinct box classes**, with every open piece carrying a certified `lane_ub ≥ 1` and the frontier GROWING with depth (`l1_158` 15 → 349 opens from depth 9 to 15), and the unwidened (`w = 0`) lane leaf kills **0 of 44**. **0 cells removed, 0 CPU-h credited** (this row keeps the post-A141 9,400–10,900); cost **1.9 CPU-h** of a 3 CPU-h cap. The measured by-product is that the two-crowd is a *pad* phenomenon: in **0 of the 28** recorded witnesses do BOTH squares meet the plain cell `TR(0,0)`, and on 35 of the 44 corners the joint optimum at `w = 0` is `J ≤ 0` with 16 of them at `J = 0` to 10⁻⁹ — exactly tangent — so the PI's "mutually exclusive at TR(0,0)" reading is right on 35 of 44 and tight, but it is a statement about the unwidened cell and a kill there would be **s0-only** (A155's pad measurement, from the other direction) (`attempts/A159-k0-nearmiss-joint`) — **A191 (2026-09-10): THE FIRST k0 NODE KILLS UNDER THE FROZEN VERIFIER — 17 of `l1_104`'s 64 alive S2 nodes (27 %) die by the exact-core LP at budget 8 on the cascade's collapsed roles (τ = 7.000 < 8, all 17 PASS under `verify_case.py` sha `521cb01f…`, conditional on K0-O1 as every cascade kill), 5.4 CPU-h for the layer at 305 s per node; 19 more are unconverged LP kill candidates; the price of the cell is the S3+ fan-out against the deep kill rate (§D item 13, `attempts/A191-combined-cascade/notes/price191.md`)** | **theorem route: 0** / tree route **12,000 CPU-h** (13,500 less A115's midpoint; **9,400–10,900 after A141**) | 7,000–18,900 | 0 / 100 | A99 `99985b76`; A115 `0d4c79fd`; LOCK-FREE⁺ evidence A104 `af6456e1`; A113 `6409396b` | LOCK-FREE⁺(< 4); dual-guided re-branching on the slot the support keeps occupying (A113: the un-killable cells' supports are 2–6-slot partial skeletons of near-critical shadows; the cell's own box distance to the manifold predicts nothing, the support does); the k0 tree has zero logic kills today |
| **Total, theorem route** | | **≈ 6,100 CPU-h** | 4,650–10,050 | **≈ 51** | A57 re-priced 800 → 1,800 (A149, 2026-09-08); protected tier and k0 unchanged | |
| **Total, tree route** | | **≈ 19,500 CPU-h** | 12,550–31,050 | **≈ 163** | same | |
| PI target | | 400 CPU-h | | 3 | | |

The gap to the target is the protected tier and, on the tree route, k0_00. A57 is now under 1/3 of the theorem-route
total; the levers of this week (tight core −32%, trimming −20%) applied to the protected tier's trees would move that
row by a comparable fraction, but that is a projection, not a measurement.

**A57 re-priced, 2026-09-08 (A149).** The row went from ≈ 800 CPU-h to **≈ 1,800 (range
1,150–3,150; ≈ 15 wall-days at 5)** and the entire increase is a term the standing estimate never
carried. That estimate was `lemmas.md` T23's grid count — 6,418 level-1 "ok" children at 431 s
each, **one LP per child and no descent**. A137's night measured both halves of that product for
the first time. The node got *cheaper*: with A135's exact cores an LP plus an s0 certificate under
the frozen verifier is **283 s**, so the same 6,418 children cost **504 CPU-h**, a 34 % cut. But
an emitted level-1 child is not one node: at the measured level-1 rates it spawns
`8 × 0.235 = 1.88` children costing `E_2 = 415 s` each, so one "ok" child is **3.76 nodes**. The
same §B/A124 recursion, made absolute and evaluated against a frontier counted id by id (2,052
nodes on side 1, 4,683 level-1 children on grid sides 2–4), lands at 1,777 CPU-h. Two of the
night's headline rates needed correcting first, both in the unfavourable direction: 573 of the 849
level-1 children screened were re-screens of ids already in the corpus, and on the 276 genuinely
new ones geometry kills **22.5 %** (not 27.4 %) and the LP certifies **76.5 %** of decided (not
78.8 %). What the number does *not* yet rest on is a measurement: `D_2`, the descent share at
level 2, is A96's 0.113 from the old tree, and every one of the 1,117 level-2 LP jobs is still
queued. It alone spans 1,386–3,279 CPU-h, so ~300 level-2 solves (**24 CPU-h**) buy more
certainty about this row than any lever on it.

## B. Where a tree's time goes — the anatomy of a node (A57, measured)

| outcome of a node | share of nodes (level 1 → 4) | what runs | cost per node |
|---|---|---|---|
| KILL-BY-LOGIC (box vs pin cores; now T5′ tight core, T5″ trimming) | 29% → 60% (rises with depth: smaller boxes clash with pins) | geometry only | **~0 s** |
| PASS (LP dead, certificate verified) | 45% → 20% | LP 240–400 s + exact verify 100 s at s0 + 4-D window verify 545 s at level 2 | **~800–900 s** |
| FAIL (LP dead, certificate has holes) → resolver | 7–10% | LP + verify + resolver 3–11 s (or ε_geo retries, up to minutes) | ~900 s |
| ALIVE-at-LP (τ = budget, η = 0) → split into 8 children | 19% → 10% | LP 240–300 s, no certificate, then 8 children | **300 s + 8 × (the row above)** |
| timeouts (verify cap; atom-heavy children) | ~5% | wasted verify wall, then resolver | up to the cap (1,500 s) |

Two readings of that table. **Roughly half of a non-logic node's wall is verification, not LP** (100 s exact at s0
plus 545 s over the window at level 2, against 240 s of LP); the parametric route already cut this from four fixed
sides to one 4-D run, and the resolver turns completed FAILs into kills in seconds, so timeouts are the waste to
watch. **The expensive object is the ALIVE node**, because it pays an LP and then buys eight more nodes; the alive
population is the S01/S02 families of `residue_ledger.md`, and A109 found 28 of 46 sampled "alive" nodes were
merely unconverged at the LP time cap.

## C. What the compute is being spent on, by structure (the families of `residue_ledger.md`)

| structure | share of alive nodes | why the LP cannot kill it | kills that work | kills that do not |
|---|---|---|---|---|
| S01 "room at side 4": a slot left empty or singly met | ~45% | the LP does not know the teleport lemma; crowd rows re-price rather than forbid (A109) | splitting until the box clashes with a pin (logic) | crowd rows at licensed depth (0 of 18) |
| S02 the k7 pinwheel (= Trump's load path in k5_11's skeleton) | ~25%, and 10 of 19 level-3, 4 of 9 level-4 | 0.0097 of slack invisible to cores at a ≤ 0.48; the tree conditions on the rattler's pocket, not the load path | trimming (12 of 14 level-4 boxes), tight core; load-path branching (A111 measuring) | basin balls (no open box contains the shadow), grain flood (circular) |
| S03–S06, S08–S53 | ~20% | as S01 by type | splitting | |
| fractional supports | ~25% (mostly level 1) | genuinely undecided | splitting | nothing structural known |
| near-flush / η = 0 pin-contact stratum (cert_failures E) | the FAIL population | certificates refuse at η = 0 exactly | resolver, ε_geo retries | SNAP leaf (0 flips) |

## D. Where to look for improvements, ranked by CPU-h at stake

1. **Geometric kills that skip both LP and verification.** Every node killed by logic saves ~850 s. The two in hand
   (tight core, trimming) took A57 from 19.6 to 10–11 wall-days. The next candidates, in order of likely yield:
   pair kills once a node carries two boxes (core–core overlap; Lemma TC between bins — free after re-conditioning);
   box–pin octagon tests at emission (already what trimming does); box-vs-forced-neighbour kills, which need a
   second conditioned square and are the reason A112 (load-path branching) exists.
   *A111 (`4c6ace6e`), A112 (`e6690215`):* the region tree kills 3 of 11 non-trivial stalled S02 regions at 27–54×
   less wall than the old tree on those boxes (two certificates per kill), ordering is a tie-break, the free kills
   are all Lemma TC, the k0 cells do not move (η = 0 exactly). As a scheduler option for stalled nodes with
   fall-through it is worth of order a wall-day on A57. A117 (`6f160858`) delivered both prerequisites — verify_param_v2
   with NO-families (Lean-proved exemption clause) and TC as a leaf (170/170 fires, 1.7M samples) — but v2 buys
   validity, not wall (10× the four fixed sides), and YES-side boxes are refused as parametric cores, so
   certificate-based region-tree kills remain s0-only for now.
   *A116 (`74a34f96`):* the local certificate around a minimum is dead at (0.2, 10°) for S02 and (0.1, 40°) for S07
   — the YES leaf of the region tree at 20× A111's radius, covering the supports of 95 of the 252 S02-explained
   alive nodes. A119 (`71d18eba`) made the five neighbourhoods exact (independent rational checker, 53k leaves) and
   Lean-backed (0 sorries, one axiom: interior SAT); blocking boxes do not widen them; three of A116's larger cells
   are alive, not open. A120 (`9fa13dfe`) deployed it: 4 of the first 9 in-N nodes closed outright (≈ 0.05
   wall-days), the rest limited by certifier rounds at a 0.3% margin, not by the mathematics; 26 nodes continue.
   *A136 (`PENDING`, 2026-09-08):* finding F-COVER closed at the emitter (the NO zone was written
   OUTWARD by ≤ 1.1e-7, so `ZONE ⊆ BOX` — the hypothesis `LocalCompose.noneIn_of_clamped`
   needs — failed on every certificate); with the zone written INWARD and the clamp bound written
   EXACTLY, A120's 22 certificates re-certify 22/22 (997 s of replay against 16 462 s of emission) and
   the in-N board is **15 CLOSED, 9 OPEN, 11 not run of 35**, at a mean 2 932 s per closure. The
   certifier ceiling A120 reported is a rounds-1 artefact: at `--rounds 6` with a 2 600 s wall the
   verifier REFUSED nothing (54 PASS, 6 CAP, 0 FAIL) and the max PASS was 2 314 s. Remaining
   obstruction is 15 genuine survivors concentrated in 5 nodes, which need a different cover.
   *A151 (`PENDING`, 2026-09-08) — the pinwheel basin priced by family, and an ASYMMETRIC N:* the
   night's kill records joined to A107's shadow families, with the three lanes kept apart (A137's
   rows all carry `lane: exact-core re-emission`, including the first LP of the night's own
   children; mixing them inflates S02's rate from 36.8% to 43.6%). On the stubborn ALIVE population
   the exact pin core makes **S02 the best-yielding family — 36.8% (21 of 57) against the
   population's 25.9% and S01's 25.5%** — but only marginally: every S02 kill lands within 0.25
   budget units of the threshold (median τ 4.75 against S01's 4.00), **29.8% of S02 nodes fall in
   the LOST-KILL-ON-RESOLVE / TOO-TIGHT band** against S01's 5.2%, and the S02 nodes that do not
   fall sit at τ = 5.000000 exactly — A106's "no open box contains it", in the LP's own numbers.
   K′ is NOT the lever it was priced as here: **T5⁗ fired zero times on all 3,034 children** emitted
   that night (T5′ at the exact core already takes them) and the geometric lane kills S02 at the
   population rate (27.4% vs 27.1%), only the pin-clip preferring it (enrichment 1.37 — 50 of the
   159 clip kills on 22.9% of the pool). Growing A116's N coordinate by coordinate from (0.2, 10°)
   under a 3 CPU-h cap: **f1 certifies at 10× A116's cell volume** (x ±0.40, y ±0.25,
   θ ∈ [8.435°, 88.435°]; 72,138 leaves; 100,000 drawn → 2,959 tested → **0 hits**; box-constrained
   SLSQP minimum 3.885618; Trump outside), f2 only to θ ±14°, and **every other refusal is a wall
   cap with 0 witnesses and 0 unresolved leaves — no real partial packing was found inside any grown
   N**, so at this budget the limit is compute, not geometry, and A116's forced radii (f2 0.215,
   f1 0.019) rank the two squares backwards for this purpose. That N was re-emitted through A133's
   own generator and independent rational checker (imported unchanged, writes redirected) as
   `local-cert-t-v1` **`S02_k5_11_A151asym_f1.tcert.json.gz`, DEAD, 38,590 leaves, 555,068 rows all
   implied, exact certified minimum 3.8770844581 > s₀, checker VALID / 0 errors** (595 s emit,
   191 s check) — the same object and format as the YES-leaf citation A136 uses, so it is a drop-in
   replacement subject to the Lean re-emission. Consumers: **96 of the 184 k5_11-frame
   S02 nodes (42 alive) against the symmetric N's 72 (32)**, +33%. Priced at A136's measured
   3,469 s per target attempted and 69% close rate (**1.39 CPU-h per closure**), the widening is
   worth **6.9 closures for 9.6 CPU-h ≈ 0.08 wall-days at 5 workers** on its 10 new alive consumers;
   the exact-core re-solve is **3.6× cheaper per kill (0.39 CPU-h)** but closes only 37%, and the two
   compose — re-solve first, split what survives (~7.7 of 10 for ~7.2 CPU-h). **Widening N is not the
   binding constraint:** the symmetric N already has 26 alive consumers the YES/NO runner has not
   finished (21 that were never A120 targets, 3 NOT-RUN, 2 OPEN) — 25 CPU-h of exactly the same
   work, at the same price. Notes: `attempts/A151-pinwheel-basin/notes/{method,results,t2_table}.md`.
   *A118 (`405b6522`):* the lane-count leaf is a 0.37 s/cell emission-time pre-screen worth ~1.7% of LPs (0.05
   wall-days) — deploy at resume; the two-meeter cover does not terminate (2–500 CPU-h per node); the octagon pair
   test supersedes Lemma TC as the pair leaf.
   *A131 (`PENDING`) — the PIN-CLIP (T5‴), measured, not deployed:* shrink the centre box, not just
   the tilt bin. For each tilt sub-bin, discard every centre at which the conditioned square meets
   a pin core at EVERY tilt of the bin — the exact intersection over tilts of the forbidden
   octagons, in rational arithmetic with no epsilon (tilts as `t = tan(θ/2)` make cos/sin rational).
   Controls: 674/674 existing logic kills clip to EMPTY, 1,140,000 drawn → 897,320 tested → 0 hits,
   and the predicate matches a direct SAT grid on 40,000 random cases with 0 unsound / 0 missed.
   **It strictly dominates T5″** (all 159 of T5″'s empties, plus 21 more) and touches 2.7× as many
   boxes (455 vs 166). On the 1,744-box corpus: 10.3% clip to EMPTY, 26.1% are narrowed and
   survive, median 0.71 free levels among those narrowed; L4 85.7% emptied. **The decision-relevant
   slice is the 607 recorded-UNCLOSED nodes (414 ALIVE + 193 FAIL): 132 (21.8%) clip to EMPTY and
   292 more (48.1%) narrow** — 112 of the 132 need only the trim already deployed, and they are
   open only because T5′/T5″ are pre-filters on newly emitted children. That backlog sweep is pure
   geometry (minutes) against the 900 s re-check's 27 kills for 8.11 CPU-h, and the two sets
   overlap in one node. At emission the incremental value over deployed T5′+T5″ is small — 1.2% new
   outright kills plus ~2.6% of modelled level-promotion, ≈ 0.4 wall-days of the A57 row — so the
   ranking is: **run the retrospective sweep first (`attempts/A131-pin-clip/results/backlog131.jsonl`),
   deploy at emission second.** In vitro (10 nodes, 2.85 CPU-h, two-stage 240/900 s through
   recheck96's node path): **5 of 10 go from η ≈ 0 to η = −0.5 or −1.0 on the clipped box and 2 are
   certified dead through the frozen verifier** (`Y0036_D02` L2 PASS 11 s, `Y0186_D00_D00` L3 PASS
   219 s, both previously ALIVE); 3 more reach η ≤ −0.5 but the certificate has real holes →
   resolver. On the other 5 only the columns move (support 107→5, 1041→5), and which of the two
   happens is **not** predicted by how much is clipped. List, notes and the deployment shape:
   `attempts/A131-pin-clip/notes/{measurement.md, lp_effect.md, deploy.md}`, lemmas.md T5‴.
   *A132 (`polygon core`, 2026-09-07):* the same move on the OTHER side of the hypothesis — replace
   the box's inscribed square `K(a)` by `K′(B) = ⋂_{(c,θ)∈B} Q(c,θ)`, the exact intersection of the
   hypothesis square over the box (convex, certified vertex-by-vertex in exact rationals at 0.07 s
   per box; median area gain **1.225**, up to 1.53 at level 1). Over all 506 alive nodes (A57's 414
   + A60's 92) it excludes **22.3% of dual-support columns carrying 35.7% of τ** and **20.5% of the
   5.7 M-row pool**. Two levers, and BOTH pay. (i) **T5⁗ logic kill** — `K′(B)` meets a pin's
   `K′(P)` ⇒ node empty, no LP, no certificate, ~850 s plus eight children saved: fires on **64/506**,
   **37 new** on top of the deployed T5′ (27 the tight core already kills — 20 already recorded, and
   **7 A60 nodes where T5′ has never been applied**, a free kill for the protected tier). At 34/414 =
   8.2% on A57, and ASSUMING the alive population's box/pin geometry is representative and each
   killed alive node would otherwise have been split into eight children at ~850 s, that is ≈**64
   CPU-h ≈ 1.3 wall-days** on the A57 queue, plus the same fraction on the protected tier, whose
   box/pin geometry is identical. Cost: **no verifier change and no certificate change** — the kill
   certificate is one rational point plus two rational vertex checks, `Zones.core_meet_same_square`
   already takes arbitrary sets, so the only Lean obligation is the decidable vertex test (≈1 day);
   re-verification of the existing tree: none; positive control 854/854 known logic kills preserved.
   (ii) **The LP**, which the file predicted was worthless here (a `K′(B)` row drop is a strict
   special case of A96's all-poses filter, measured at zero kills above): **refuted.** In vitro (10
   alive nodes, both arms, identical warm start and oracle, recheck96's node path, 2.7 CPU-h) three
   pairs converged in BOTH arms and **all three are LP-dead under the polygon core and alive under
   `K(a)`** — `Y0871` 5.000 → 4.000, `Y1038` 5.000 → 4.500, `k5_16 Y0281_D03` 5.000 → 4.000. The
   attribution arm says why the prediction failed: with `K′` on the CONDITIONED BOX ONLY (A96's
   scope) `Y1038` converges back to 5.000 — that kill lives entirely in the **pin** polygon cores,
   which the all-poses filter never covered (T1: 21% of the excluded support weight). These are
   "LP-dead, CERTIFICATE PENDING"; the v3 clause that would close them (rational polygon–square SAT
   in the exemption test, ~140 lines + Lean bridge, 4–6 days) is specified in
   `attempts/A132-polygon-core/notes/spec.md`. **Do not price it off three pairs on nodes selected
   for the lever** — measure the rate on ~30 unselected alive nodes at a cap both arms converge
   under (~10 CPU-h) first. Composes with A131's pin-clip in the obvious direction: clip the centre
   box against the pins, then take `K′` of each surviving sub-box — `B′ ⊆ B ⇒ K′(B) ⊆ K′(B′)`, so
   the clip strictly enlarges the polygon core, and both are logic-level levers that touch no
   certificate. `attempts/A132-polygon-core/notes/{measurement.md, spec.md}`, lemmas.md T5⁗.
   *A135 (`polycore verifier`, 2026-09-07) — A132's three pending kills are now CERTIFICATES, and
   most of the lever is FREE.* **T1, the finding that reorders the work:** both frozen verifiers take
   the core half-side `a` VERBATIM from the certificate and never recompute it — neither is given the
   parameter box at all (`verify_case.py:707-710` and `verify_param.py:539-543` check only
   `0 ≤ tm ≤ 1` and `a > 0`; `verify_case`'s `box` field is floats and its loader never reads it).
   So a sound half-side is certifiable TODAY, with no verifier change and no schema change. For a
   PIN box (tilt 0, half-width `h = δ/√2`) the exact intersection over the box IS the axis square of
   half-side `1/2 − h`, while `Box.core()` bounds the offset by the circumscribed disc and returns
   `1/2 − h√2 = 1/2 − δ`: **0.489999969 → 0.492928902 certified exact, +0.6 % per side, ×1.012 in
   area**, and the T23 pin-core disjointness gate still holds (gap 0.020000 → 0.014142 > 0, min L∞
   slot separation 1.000000). **T2: 3 of 3 certified** — `k5_11 Y0871` under the FROZEN verifier with
   the exact **pin** cores alone (τ 4.1667, 656 s LP + 46 s verify), `k5_16 Y0281_D03` under the
   FROZEN verifier with exact cores on every box (τ 4.000, 36 s + 0.5 s), and `k5_11 Y1038` only
   under the new `verify_case_v3.py` (τ 4.500, 377 s + 20 s; the frozen verifier FAILS the same
   certificate with 5 real holes, so this one genuinely needs the clause). The v3 clause is
   **1,540 of 37,894 exempt boxes** on that node; v3 imports the frozen file rather than copying it
   and is identical to it on 24/24 `polycores`-free certificates — verdict AND box-tree statistics;
   `--replay` (no float pre-filter anywhere, one process) reproduces the PASS with a byte-identical
   box tree in 153 s. Sampled controls: 20,000 poses → 320,000 vertex tests → 0 violations;
   20,000 sub-boxes → 10,067 accepted → 201,340 pose tests by an independent SAT → **0 unsound
   exemptions**. Lean: `PolyCoreT5.lean` compiles clean and axiom-free (`propext`,
   `Classical.choice`, `Quot.sound` only) with `checkVertexInPBox_sound` **proved** — A132 sized it
   at a day and it came in cheaper because clearing `1 + t²` reduces the whole question to rational
   polynomial positivity, which A133's `LocalCertT.posCheck` already decides. **A132's caveat is
   untouched: three pairs on nodes chosen for the lever is not a rate.** What is now priced is the
   certificate side, and it is ~0 for the frozen path. **Next chore, and it is the cheap one:**
   re-emit the ALIVE population with exact pin cores — 414 LP re-solves at 240 s ≈ **28 CPU-h**
   (≈ 0.6 wall-days), no verifier change, no Lean change, no re-verification of anything already
   emitted; every node that drops below budget is a kill the frozen chain accepts as it stands.
   Run that before pricing v3 on 30 unselected nodes, because it is 3× cheaper and its yield is a
   strict lower bound on the polygon's. Ledger `attempts/A135-polycore-verifier/results/polycore_kills.jsonl`
   (64 T5‴ logic kills, 37 new, every witness re-certified closed AND strict against both boxes by an
   independent implementation, 64/64; plus the 4 certified LP kills);
   notes `{acceptance.md, certified.md, lean_bridge.md}`.
   *A164 (`PENDING`, 2026-09-08):* Leaf WASTE (the uncoverable area |U| against the wastage budget
   m² − 11 — A89's Lemma ID with the corner box replaced by any certified-uncoverable region) is the
   CHEAPEST screen in the toolbox — 8–18 s per node for the whole certificate (raster + Lipschitz
   margins + 10⁵ sampled poses), no certifier round at all, against ~850 s for an LP node — and it
   **fires on nothing at the current frontier**: over all 71 alive gallery nodes the best node reaches
   42.2 % of B₀ = 4.0318 at pitch 0.01 (47.1 % at pitch 0.005: `f1_L10_0003`, |U| = 1.8969), the median
   18.6 %, and the eleven pin-free k0 cells 0–8.3 %; the four corner boxes are coverable on every
   single node, so Lemma ID's own shallow-corner row has no consumer either. **0 CPU-h are at stake
   from deploying it on today's alive set.** The right disposition is a 15-s pre-screen inside the
   EMITTER at 7+ hypothesis boxes, where |U| scales with the box count (mean 0.128 at 1 box, 0.793 at
   6, 1.701 at 7) and the leaf's own extrapolation puts the first fire at 9–10 boxes. The transferable
   asset is W3, the Lipschitz-raster soundness obligation
   (`attempts/A164-wastage-area/notes/leaf.md` §3): A148's gallery pages and A164's leaf lean on the
   same two facts — clearance is 1-Lipschitz in the centre and (√2/2)-Lipschitz in the tilt — so
   writing W3 once in Lean pays for both, and Leaf WASTE then costs 0 new axioms.
2. **The alive population.** Re-run unconverged alive nodes with a longer LP cap before splitting them (A109's 28/46);
   branch on the load path instead of the rattler (A112); both are about not paying eight children for a node that
   was never alive or whose slack sits in squares it does not condition on.
   *Row-dropping by the all-poses test (2026-09-06, A96 `d016209b`):* the closed-form tilt-coherence screen alone
   removes a median 44% of a node's warm rows (13k of 30k); the exact all-poses test removes more. It is the
   strongest LP lever measured, and it is not free: it widens the frozen verifier's admissibility clause from
   "disjoint from every core" to "disjoint from some pose of the box", i.e. a new frozen verifier version with a Lean
   theorem parallel to T5. **Measured (A96 `37eae961`, three arms at 900 s): dropping a median 53% of rows produced
   zero additional kills** (arm C 3 kills vs arm B 4, none new); it buys convergence (7/26 vs 4/30) on nodes that
   land knife-edge or alive anyway. A speedup with no kill yield does not justify a soundness-relevant verifier
   change: row-dropping is shelved, spec on file. The 900 s cap stands on its own (2/29 converged at 240 s vs 4/30
   and 7/26 at 900 s). *Caution banked with
   it:* trimmed-bin re-solves at the 240 s cap moved the LP without deciding it (29 solved, 2 converged, 19 on the
   knife edge) — no kill count from a re-solve counts before the 900 s re-check.
3. **Verification wall.** Atom-dependent verify caps (in), resolver over timeouts (in), σ ladder to level 2 (recorded,
   not deployed: −2 wall-days, needs a coverage reset), 4-D verify sharing across siblings (untested).
4. **The protected tier.** No lever of this week has been applied there; the same box/pin geometry suggests the same
   fractions, and trump5's alive nodes are the same S01/S07 families. Worth a pilot before the tier runs at all.
5. **k0_00.** Not a compute question: LOCK-FREE⁺(< 4) or the 15,000 CPU-h tree. Corner-crowd rows at the node
   level are out (A115: the room supports have single deep meeters, nothing for a crowd row to charge; Trump realises
   nine incidences against a budget of eight at depth 0). What the k0 room needs is the teleport hypothesis itself as
   a node cut, i.e. re-branching on the singly-met corner (A112's k0 face), not a weighted row.

6. **The net-orientation verifier is a cross-check, not a lever — REJECTED as a replay verifier and as a
   certificate simplifier (A129 `[pending]`, 2026-09-07).** Burns–Massaccesi (Aug 2026, blog not arXiv) turns out
   to certify with *the same object we do* — an atomic measure with total weight < n — and to differ only in the
   verifier: a finite net of orientations, an "almost-unit" test square, and an exact per-orientation translation
   sweep. A129 built it sharply (`σ(δ) = 1/(cos δ + sin δ)` exactly, adaptive net, and — the change without which
   it replays nothing — the exemption clause decided for the *unit* square over the whole net cell rather than the
   shrunk one) plus an independent `Fraction`-only checker that imports the frozen exemption predicates.
   **As a replay verifier for A57's PASS leaves: no.** On 60 stratified PASS leaves it reproduced 26 inside a
   120 s budget at a **median 15× the frozen verifier's wall** (10.8× on the totals); an exact second pass on 12
   of the 34 that ran out of budget resolved 96 of 96 sampled tilt positions at levels 5–12 and put their cost at a
   **median 26.7× (up to 234×)**. It cannot replace any of the ~850 s: it multiplies the 100 s exact-verify half by
   10–30. **The failure mode is not the reviewer's predicted margin — 0 of 60 leaves lost the shrink.** The shrink
   consumed at the level that works is 6e−5 to 5e−2 in side and every certificate absorbed it, because a leaf
   certificate is a *measure*: the shrink comes out of its mass slack, not its side slack. What kills it is
   architectural — the frozen 3-D `(t, c_x, c_y)` tree discharges a whole band of orientations against the six
   cores with one `t`-box, while the net re-resolves the same exempt boundary at every one of a median 185 net
   orientations. Optimising the predicate moves this by ~2×, not by 10×.
   **As a certificate simplifier: no.** There are no Farkas vectors and no separating-axis selections to be had —
   the certificate stays the same atoms and weights, and the net certificate merely adds a tilt tiling (1,950 exact
   rationals for 3.82) and a σ per cell. The Lean shape is *worse* than A119's `leaf_*` lemmas, not better: it
   replaces one 3-D `native_decide` by one per net cell.
   **As a cross-check: yes, and it earns that outright.** Both whole-problem certificates were run to completion and
   both PASS: `s(11) ≥ 3.82` at 1,950 net orientations (deepest level 14, shrink 3.81e−3, 3.96e10 arrangement cells)
   in **2,148 s** against the frozen verifier's **587 s** (3.66×), and `s(12) ≥ 3.90` at 987 orientations in
   **802 s** against **232 s** (3.45×). Unconditional measure certificates are exactly where the method is cheap —
   no exemptions, so no bisection at all (the mass is constant on an arrangement cell, so the correct bisection
   depth is 0). That is a genuinely structurally independent decision procedure for the two headline theorems, for
   36 and 13 single-core minutes, sharing no code, no data structure and no search order with A07/A08; a fully
   exact `netcheck` replay of the same two would cost 19 h and 9.5 h (16 cells of each were run: both CHECKED).
   Take it for W7 and for the paper's "two verifiers" paragraph; do not schedule it against the A57 row.
   *Files:* `attempts/A129-net-verifier/{code,notes,results}`, notes `method.md` (Lemmas N1–N4) and `benchmark.md`.

7. **GUARD-LINE rows: a real but narrow LP lever — and the exact-core chore is the bigger prize
   (A144 `[pending]`, 2026-09-07).** For any line `l` inside `[0,s]^2` the chords of a packing are
   interior-disjoint, so `SUM |l n Q| <= s`; splitting off the hypothesis squares turns the PI's
   "a line crossing four squares through opposing sides forces side >= 4" into an LP **column** —
   a measure of density `z` on `l` priced at `rhs(l) = s0 - SUM_pins minchord - minchord(H)`
   instead of `s0`. `minchord` over a parameter box is FIVE exact rational evaluations (the chord
   depends on the tilt only through `y = cos+sin`, `A(y)` is monotone and `B(y)` attains its
   interval minimum at an endpoint), so the whole family is cheap: **all 448 surviving A57 nodes,
   <= 40 lines each, 43.5 s with no LP** — and **86 of them (19.2 %) have a line their stored dual
   support violates** (median depth 0.095, max 0.266; 15 of the top 40 by subtree cost). Sampled
   confirmation 80,640,000 poses -> 0 hits. **In vitro on 20 nodes (2 arms, 240 s, A132's node
   path, 2.34 CPU-h) the column is ACTIVE on exactly 2, and those 2 are exactly the 2 new kills**
   (`k5_11_interior_Y0147` 5.000000 -> 4.877459, `k5_16_interior_Y0101` -> 4.922603); at 900 s
   Y0147's control converges at 5.000000 while the guard arm holds 4.877459 with `minmass` 0.982 —
   **eta stable, coverage not yet closed, so not yet an LP kill**. Price it as a narrow lever: ~5 %
   of nodes (23 of 448 carry >= 4 unit chords on one line, all of them violating), ~0 s to screen,
   and a v3/v4 certificate clause (`guardlines`; ~120 lines + 2 Lean theorems, 0 new axioms,
   `attempts/A144-guard-lines/notes/spec.md`) that is needed at EMISSION as well as verification —
   `certify.py` re-derives the measure from atoms alone and returns to tau = 5.000. **The by-product
   is worth more than the lever:** the control arm is A135's EXACT cores and it kills **15 of the
   20**, and a third arm with A57's DEPLOYED cores at identical settings kills **0 of 6** — so the
   drop is the cores, not the re-solve. That is item 1's 28 CPU-h re-emission chore, now with a
   20-node datum behind it (caveat: the twenty were selected for guard-line violation and are tight
   by construction, so 15/20 is not a population rate).
   *Files:* `attempts/A144-guard-lines/{code,notes,results,figs}`, notes `spec.md` (the cut, the
   `guardlines` field, the v4 clause, `chord_sum_le_side` / `minchord_of_box`) and `measurement.md`;
   figure `figs/k5_11_interior_Y0147_guardline.svg`.

8. **The COVER-NUMBER leaf: a sound, LP-free, ~5 s/node price — that kills nothing, and provably will not.
   MEASURED AND CLOSED (A153, 2026-09-08, 2.5 CPU-h, 322 nodes).** Two interior-disjoint unit squares have centres
   ≥ 1 apart (each contains the open disk of radius 1/2 about its centre), so the centres a node still has to place
   are a 1-separated subset of A148's certified outer feasible-centre region `F_out`; if `F_out` is covered by `k`
   pieces of diameter < 1 then at most `k` more squares fit, and `k < budget` is a kill with no LP. The pieces are
   axis-aligned squares of side `6784897/9700000 = 0.699473918` (exact test `2d² < 1`), `F_out` is a union of A148
   grid cells so the covering check is finite integer arithmetic, and the whole leaf costs **one Lean structure, one
   decidable check and two Mathlib-level theorems — zero new axioms** (`attempts/A153-cover-number/notes/lemma.md`).
   **Over the 60 A57/A60 nodes A148 drew, the 11 k0_00 residue cells and all 251 alive A57 nodes of `PAUSED.md` v3:
   0 kills.** Exact minima by branch and bound on 197 of the 322; `cover − budget` median **+4**, best +0 (one node),
   k0 18–22 against budget 10. **The obstruction is a floor, not slack:** on 322 of 322 nodes `F_out` itself already
   holds ≥ budget points pairwise ≥ 1 apart, so no piece shape and no grid refinement can bring the count below the
   budget — checked directly by re-pricing the 18 tightest nodes at 4× resolution (13–25 % less area, at most one
   piece gained) and the tightest of all, `k5_11_interior_Y1104_D01`, at 16× (cover stays 5 = budget). The
   tilt-coherent variant (Lemma TC, conditional on a common-tilt branch) roughly halves the count and still kills
   nothing over any node's whole tilt window; its single hit dies at a tilt bin of half-width 0.1°. **Price it at
   zero as a lever and keep it as a free assertion on the gallery pages** — it is the disk bound's combinatorial twin
   and 2–4 pieces tighter (Y1117: disk bound 10, cover number 8), so it costs nothing to print and it bounds the
   node honestly. *Files:* `attempts/A153-cover-number/{BRIEF.md,code,results,certs,notes/lemma.md}`; certificate
   format and checker fixture `certs/k5_16_interior_Y1117.cover.json` (a demonstrator, not a kill: every clause of
   `check153.py` passes on it except `#pieces < budget`).

*A160 (`PENDING`, 2026-09-08) — the pinwheel's two extra directions, and the finding that the local
certificate is a UNION, not a growable box:* S02's `f0` is a **rattler with a one-parameter slide** —
the ten-square core minimises at the same 3.886746028606 to twelve digits with `f0` deleted, and
`f0`'s admissible set there is an exact segment of **length 0.298419** along its own body axis at a
FIXED tilt (area and width vanish linearly in the relaxation, the tilt window like its square root),
running from a `BR(0,1)` stop to an `f1` stop with `BL(1,0)` and `f3` as rails. **`f3` is not a
rattler** — it is the shadow's most load-bearing square (Δs\* 0.1190); the second rattler is the
*slot* square `BR(0,0)` (slide 0.5357). Putting `f0`'s slide-cover box into `N` is a **net loss** —
one more clause takes A151-B's 96 in-N nodes / 42 alive to **15 / 8**, recovering only when the box
reaches ±0.50/±0.47/±45° — and the tree with `f0` as a fifth free body **caps** (wall cap at 420 s and
still 0 witnesses / 0 unresolved at 1024 s, certified min 3.8770844 > s₀), so no `N` with `f0` was
certified in a 4 CPU-h cap. The **common-tilt chain is cheap and works**: `s*(θ)` on the shared tilt of
`f1 f2 f3` is above s₀ everywhere, 24 links of half-width 1.25° certify a **60.0°-wide** shared-tilt
range at a median 7 s a link, and 4 links of half-width 10° cover **80.0°** at 55–285 s — but its
consumer ceiling is the count of nodes whose support tilt SPREAD is ≤ 2h (**63/27 at 1.25°, 91/40 at
5°, 124/53 at 10°**), and of the 20 alive nodes outside A151-B **`f2`'s tilt binds 14 and `f3`'s binds
10, 9 by those two alone** — INDEPENDENT windows a common tilt cannot open. Slicing those windows
instead **works and is nearly free**: with `f1` at A116's own box, **all eight axis slices certify with
zero failures in 348 s total**, extending `f2`'s and `f3`'s tilt windows independently over the whole
fundamental domain [−1.56°, 98.44°], and the corner slices of the 5 × 5 product certify at 2–188 s
each. **The load-bearing discovery is that the directions TRADE OFF**: `f2`'s upward slice certifies
at `f1`'s base box in 108 s but is **REFUTED BY A WITNESS** together with A151-B's grown `f1` (the
witness puts `f1` at 83.44°, a pose only the ±40° window admits; side 3.869337946 < s₀, re-verified),
and growing all four centre boxes together is refuted by witnesses at **r = 0.25 already** (certified
at Δθ = 0 and −10°, witness at +10°; r = 0.30 witness at 0°; r = 0.40 witness everywhere) — the first
LIVE-LOW witnesses anywhere in the A116/A151/A160 line, all ten re-verified from scratch. So
A151's "compute-limited, not geometry-limited" holds for single knobs and **fails for compounded
ones**, and the right object for A136's YES leaf is a `N_boxes` **LIST whose hypothesis is a
disjunction**: A151-B ∪ the common-tilt chain ∪ the independent tilt slices reaches **114 of 184
in-N nodes / 50 alive against A151-B's 96/42 and A116's 72/32**, for ≈ 0.9 CPU-h of tree time in 50+
certified boxes, every refusal in the union either a wall cap (labelled) or a drawn witness.

**Re-framing a basin is cheap, and it is the cheapest S02 work left (A163).** Carrying A160's 53
box sets + A151-B into k5_16's and trump5's pin sets cost **3 824 s of selection tree** (1 688 s +
2 136 s, 240 s cap, two BLAS-pinned BelowNormal processes) plus **2 104 s of exact emission and
independent checking** for **all 94** t-certificates (1 616 s generator + 488 s checker, 125 840
leaves, 58 MB; an h = 1.25° chain link is 0.6 s and 0.01 MB, a tilt slice 1–98 s, A151-B 229 s and
9.4 MB) — about **1.6 CPU-h for 94 fully certificated objects in two frames that had none** — and it
buys 38 in-N / 21 alive k5_16 nodes and 3 in-N / 3 alive trump5 nodes at
≈ 0.05 CPU-h per alive consumer, against A160's ≈ 0.9 CPU-h for +8 alive in k5_11; the k5_16 frame
is where the remaining cheap S02 yield is (its two refusals are wall caps at 240 s, so a longer cap
finishes it), while trump5's 12 nodes are capped by geometry, not compute — 9 of its 12 refusals are
re-verified LIVE-LOW witnesses, so no wall time closes them and the only route to its other 9 nodes
is boxes that do not lean into the unpinned `TL(0,0)` corner.

9. **The `make_certificate` stock-core reversion: a real emission bug, but a SMALL lever, and now
   fenced (A170, 2026-09-09).** `caselp.make_certificate` ends with `hyp = Hyp.from_json(res["hyp"])`,
   and `Hyp.__init__` recomputes `self.cores = [b.core() for b in boxes]` — the STOCK cores — so the
   `cores` field the json carries is discarded and an `ExactHyp` LP emits a certificate exempting a
   strictly smaller core than its row filter dropped rows against; every LP-dropped placement in the
   1.4–15 % annulus is then a guaranteed hole (A166 `bc8b5dd5`). A170 measured the blast radius
   **empirically on all 3,378 certificates on disk** — for each, the exact core recomputed from the
   box the certificate itself carries and compared with the `a` it wrote. **The bug reaches only the
   lanes that call `caselp.make_certificate` / `caselp92.make_certificate` DIRECTLY with an
   `ExactHyp`: A150, A165, A166** (A168 already carries A166's patch). Every lane routed through
   A135's `emit135.make_cert` — A137, A140, A145, A149 (both the `__exall` and the `__exH` arms),
   A156 — writes **exact cores, 698 of 698**, because that function exists precisely to avoid the
   round-trip (`emit135.py:94-100`). **59 certificates recovered over 409 re-certified, 59/59 clearing
   a 100 % independent check** (A132 `polycore.vertex_ok` re-run on the written rationals, the measure
   recomputed exactly in `Fraction`, and a depth-64 frozen replay), in two kinds. **(i) 25 repairs,
   8 nodes, 3 of them new:** A165's `l1_104_spread_spread00/02/03`, taking that leaf from 1-of-4 to
   **4 of 4** certified and refuting its note's "they need the separation loop with more rounds, not a
   different core" — they needed the cores they were solved with; the other 5 nodes are A150's and
   A166's own, re-derived here through a separately written path and agreeing 22/22. **(ii) 34
   upgrades on stock-core lanes, all of them A59/A60 zero-atom VACUITY certificates** (`total = 0 <
   budget = 1`), where the whole content of the certificate is "every admissible square is exempt", so
   a wider certified core is exactly the lever: A59's residual ladder around Trump's packing now
   certifies at **8–14 % less exemption parameter `a` at every rung** (`rb hw = 0.002`: `a_min`
   0.009062 → 0.007969; `rk hw = 0.02`: 0.074883 → 0.067500) — **the certified `hw` envelope does not
   move**, the ladder gets cheaper, not longer. **Everything else is a genuine FAIL:** 118 exact-core
   certificates are NO-CHANGE, and the whole k0 pool — all 128 `kill-candidate (cert FAIL)` records of
   `cells140.open_pool`, re-emitted from A115's **stored** measure with exact cores at zero LP cost —
   yields **0 PASS** (unconverged single-box LPs at `τ ≈ 9.977` against budget 10, cores widening
   0.6–11.8 %, and 9 failing on `total ≥ budget` outright). So A166's "127 candidates for immediate
   certification" is closed at zero: none of them was emitted through an exact-core path. **The A57
   row's exact-core kill rate of 46/161 = 28.6 % is unchanged** — A137's 44 FAILs are all NO-CHANGE.
   The shadow board does not move either: `status_gallery.py` goes 5,332 → 5,344 kills and **0 new
   distinct pages** (k0v4 11 ALIVE, a57v4 53 ALIVE / 7 DEAD, unchanged). Cost **2.35 CPU-h of
   verifier**, no LP solved. The forward fix is
   `attempts/A170-certfix/code/certwrap170.py` (a wrapper, `caselp.py` untouched) plus
   `code/test_cores170.py`, a 50-box regression that asserts a certificate's cores equal
   `exactcore.exact_a` **and** that the unwrapped emitter still writes the stock core, so the guard
   fails loudly if the upstream ever changes. *Files:* `attempts/A170-certfix/{notes/audit.md,
   notes/recovered.md, notes/fix.md, results/scan170.json, results/summary170.json,
   results/check170.json}`.

10. **The assignment search is node-bound, not LP-bound (A182, 2026-09-09).** `c0_Y1033` under the
   forced-first assignment: 584 multibox nodes in 3.0 CPU-h, 26 LP-leaf calls of which ONE solved (ALIVE,
   τ ≥ 2 at budget 2) — the rest were refused by the page's LP quota or by a role hull without an exact core.
   Where the nodes go: option refinement (up to 100 sub-box combinations per option) and the cell-pair splits
   are two thirds of them (`Y1104`: 120 + 63 of 231); the 8/3 re-pass costs 4× the 4/2 pass on a tree node
   (2.4 → 9.8 s at the base) and buys H 0.271 → 0.209; a lane cover costs 6–12 s and returned information once
   in 20 calls. A k5_11 page cannot decide its first cell inside 300 nodes / 1,200 s. The lever, if the
   construction is pursued: cap the refinement (combos ≤ 40 costs nothing in kills on `c0_Y1033`), drop lanes
   at the root, and spend the LP only where every role hull has an exact core — or replace the clip leaf by
   the piece-granularity coexistence cut (A174), since no complete assignment died under the clip.

11. **A 47-second geometric leaf that A182 never ran (A189, 2026-09-09).** The NO-ROOM leaf costs one
   multibox normalise (20-25 s at 4/2), one shallow exact bisection of the free unit square against the
   node's k cores (20 s at depth 13, 0.99962 of the centre x tilt volume certified dropped on the STEP 34
   node) and one lane cover per residue pocket (2.5 s) - **47 s against the ~850 s a killed node costs
   through LP and verification, and against A182's own 3.0 CPU-h / 584 nodes on one page.** Run as a
   post-hoc pass over what A182 happened to journal it kills 5 of 19 `k = 10` nodes and retires no page,
   because the search stopped on node budget and only 4 of `c0_Y1033`'s 30 alive/undecided leaves sit
   under a dead node. Run INSIDE the search, at every node before branching or LP, it is 5.5 % of a node's
   cost for a test that killed the deepest node A182 reached. Two prices worth knowing before spending on
   it: (a) it needs the roles' K' to be non-empty, and an `F_i` carried as a whole meeter window has an
   EMPTY K', which is what keeps 26 of the 33 journaled nodes UNDECIDED - so the leaf pays off exactly
   where the assignment has been refined enough to give each role a real core, i.e. deep, where the nodes
   are; (b) the container-partition form (Lemma 2) needs a LANE verdict on every cell, and at the grid
   coarseness that is affordable (4 x 4, `N = 1`) the bound is 16 for 7 free squares - it cannot bite at
   `k = 4`, so do not spend k0-cascade compute on it.

12. **The two unpriced classes are theory-limited, not compute-limited (A193, 2026-09-10 night).** corners4
   (k4_13) and k4_05 were the only campaigns in the dependency graph without a price ("kill-only trees, no route
   beyond"). Probed with the k0 toolkit at s0 (every forced cell instantiated, A182's search, no-room, chord
   rows, windows + guard-line LP under v5): **0 kills** — corners4's leaves sit at τ = 11.000 exactly with a
   half-integral support, k4_05's at 10.77–10.86 unconverged with certificates failing at the k5_11 / k5_16
   images and re-solves crossing 11. Measured costs, for whoever prices the route once the missing pieces
   exist: multibox node 5.0 s (corners4) / 6.8 s (k4_05, lonely clip at TR); ≈ 60 option-test nodes per tree
   level; first complete leaf at ≈ 500 / ≈ 180 nodes; no-room 100–170 s per leaf (never decides: the centre
   block is one 5.9–6.8 pocket); windows + guard-line LP 340–420 s at cap 300; v5 certificate + one re-solve
   260–430 s. Per complete leaf ≈ 0.25 CPU-h; the assignment trees have ≳ 10³–10⁴ leaves (branching 3–10 per
   cell over 5–8 cells).

13. **The k0 S2 layer is priced and it kills (A191, 2026-09-10 night).** The combined cascade leaf — corner no-room lanes (29 s), the v1-style exact-core LP on the roles' union boxes with guard-line columns at budget 8 (162 s, converges), the windows LP at budget 11 as a diagnostic (101 s, never converges) and a v5/frozen certificate on a kill (46 s) — costs **305 s per S2 node (max 663 s)**, and on `l1_104`'s 64 alive S2 nodes it kills **17 (27 %) under the FROZEN verifier**, leaves 19 (30 %) as unconverged LP kill candidates and 26 (41 %) converged alive at τ = budget exactly: **5.4 CPU-h for the layer**, 0.32 CPU-h per kill. The killed nodes are the ones whose A183 fixed point collapsed H (kept ≤ 0.02): the geometry does the killing and the LP witnesses it, so the price of the cascade is the price of the GEOMETRY at depth. Read the price table in `attempts/A191-combined-cascade/notes/price191.md`: S2 measured; S3 sampled (coarse 4/2 children of the S2 survivors: the first cover box dies at 4/2 in 60 s on 4 of 4 parents, an interior child dies by the LP in 279 s); S4–S8 ASSUMED at the S3 rate with fan-out 112 / 56. At the measured rates the tree does not close (survival × fan-out ≫ 1), so the cell's price is astronomical unless the deep layers kill at ≥ 0.99 — the table prints the CPU-h for 0.27 / 0.90 / 0.99; what would make it compute-bound at a payable price is a per-layer kill rate above 0.99 from S4 on, i.e. A174's coexistence cut and A178's partner-first ordering on the fan-out, not more LP cap (the diagnostic windows LP at 1,500 s buys nothing at S2). The canary `l1_153` (1 alive S2 node) is alive converged at τ = budget: the construction transfers; the cell has nothing to kill at S2. **S3 addendum (05:30) [M]/[C]: 22 of 23 S3 nodes tried are DEAD -- coarse parent-seeded children of the S2 survivors 14 of 15 (the corner-nearest B0 by EmptyBox(B) at 4/2 on 6 of 6 parents, 37-75 s; the interior children by the exact-core LP at budget 7 CONVERGED at tau = 6.000 on 8, 1 undecided at cap 240 s) and A183's fine 8/3 records 8 of 8 (the same LP, tau = 6.000); every LP kill PASS under v5 AND under the FROZEN verifier (`certs/*_B*_v1.frozen.certify.json`) -- the LP value drops by exactly one unit per pinned square (8 -> 7 at S2 on the collapsed nodes, 7 -> 6 at S3 on every node tried), so with four cores the S3 layer is where l1_104 closes: 5,432 A168-alive S3 children under the 47 S2 survivors at 249 s each = **376 CPU-h = 23 instance-hours at 16 vCPU** for the whole layer (the sample is 23 nodes biased to the root/D0 and root/D1 chains; `notes/price191.md` gives the 0.9x / 0.99 / 1.00 scenarios and the S4 residue).  Audit (`code/audit191.py`, `results/audit191.json`): every kill certificate's cores are pairwise interior-disjoint (exact SAT) and bound to their union boxes by v5's own `point_in_all_poses` check; frozen PASS on all.**

   | class | window state | s0 state under the toolkit | what is missing | price |
   |---|---|---|---|---|
   | corners4 (k4_13) | nothing forced (all 8 extensions = k5_16, open); root LP alive 7.195 (K1) | 3/3 leaf LPs ALIVE at τ = 11.000, half-integral; no-room 0/6; chord rows 0 | a two-square row (pair clause: the two FC meeters of one slot) and/or the MEET clip (bounded spec., one afternoon in `multibox`) | **theory-limited: half-integral phantom.** With the MEET clip: one night (≈ 0.5 CPU-h geometry + 3 LPs) to re-measure; H-box datum: the YES box at the phantom's tilted pose dies by the pair leaf in 1.1 s, so the A57-type split below a leaf costs ≤ 14 geometric YES nodes (1–20 s) + one NO node whose LP needs the NoFam-in-windows clause — unpriced until that clause exists |
   | k4_05 | 3 cells forced (BR(0,1), BR(1,0), TL(1,0)); root LP 6.965 = A55, cert FAIL → 7.189 (K1) | 3/3 leaf LPs 10.77–10.86 UNCONVERGED, certs FAIL (holes at the k5_11 / k5_16 images), re-solves 10.93 / 11.10 | the δ-resister split at BL(1,0) and TR(0,0): NO = NoFam at the slot (the v4/v5 windows clause has no NoFam for window rows — a small clause), YES = slack-pin k5_11 / k5_16 nodes (P-list item 7) | **theory-limited: Lemma K1.** The all-NO node costs ≈ 2.5 CPU-h to measure; the YES side is A57's row (≈ 1,800 CPU-h), not a new item |

## E. The slab-width law (window certificates; A114's k6_07 log, 2026-09-06)

The 4-D verifier bisects tilt, position and side to a cap of 48 levels per path. Two constants belong to the
certificate and the class, not to the slab: the leaf s-cell width it needs, w_min (k6_07: 2.3·10⁻⁵, set by the
certificate's slack against the dilation sensitivity), and the pose depth it needs, d_pose (k6_07: ≈ 39). **A slab
passes iff log₂(width / w_min) + d_pose ≤ 48.** k6_07: passing 0.0029 slabs reached s-depth 7 and max depth 46 at
167–215 s each (rising gently toward s0 with the admissible area); the 0.0235 halves reached s-depth 10, hit the cap
with 8 undecided boxes and 0 holes, and cost 1,500 s each for nothing. Predictor: one narrow probe slab gives w_min
= width / 2^(max s-depth) and d_pose = max depth − max s-depth; width_max = w_min · 2^(48 − d_pose) (k6_07: 0.012, five
pieces would have done). Once slabs fit, total cost is ≈ linear in band width (k6_27 11 s, k6_07 65 s, k5_03 340 s
per 10⁻³ of side); over-splitting costs percent, under-splitting costs a failed slab.

**Measured cost profile along the side (A114 L7, 224 verifier runs):** seconds per 10⁻³ of side from the bottom of
the window to the slab ending at s0 — k6_07 53 → 91, k6_27 20 → 1,589, k5_02 89 → 502, k5_03 412 → 1,064, k5_12
129 → 4,181. The bulk trend is mild (+38% to +59% across the window); the blow-up is confined to the last 10⁻⁴ to
5·10⁻⁴ below s0, where w_min shrinks (k5_12: 1.7M boxes for a 5·10⁻⁴ slab at 3.8405 vs 12.7M at 3.877) and d_pose
climbs. That is the S02 shadow in the arithmetic, and it says the per-slab re-solve I proposed is unnecessary: the s0
certificate closes every class, including the top slabs, once the slab width is set by the law (every earlier bulk
FAIL was a slab over its width_max, k5_02's by 4×, never node hardness). Measured width_max: k6_27 0.014, k6_07
0.012, k5_02 0.0018, k5_03 0.0018 → 0.0010 at the top, k5_12 0.0010 → 0.0005 at the top.

**Third confirmation, and the sharpest (A146, k5_13, 2026-09-07 night).** k5_13 was the last OPEN
row and had cost ~40 CPU-h to an LP hang. Its A56 run FAILed on the whole window as ONE slab
(0.057084) with max_depth 48, max_s_depth 10, worst witness `undecided`, **0 holes**. One probe
slab of 10⁻³ at the bottom of the window PASSed in 74 s and priced the class: w_min = 1.56·10⁻⁵,
d_pose = 41, **width_max = 0.002** — the failing slab was **28× over the law**, so no certificate
could have rescued it (a fatter measure raises w_min, not by 28×). Swept at 10⁻³: **58/58 slabs
PASS, no bisections, 5,491 verifier-seconds**, C2 PASS at s_lo/mid/s0. The cost profile is 74 s
per 10⁻³ at the bottom, flat through the bulk, then 99 → 108 → 115 → 126 → 182 → **507** s over
the last five slabs, with d_pose stepping 41 → 42 and **width_max halving to 0.001 in the slab
ending at 3.877** — the same top-of-window narrowing measured for k5_12, arriving as a step in
d_pose. Operational rule: **when a parametric run FAILs with 0 holes and a depth-limited worst
witness, price the slab (one 75 s probe) before you price the certificate.**

**Near a solution the law stops being linear.** w_min and d_pose are set by the certificate's slack, and a class whose
boundary carries a shadow at side s* has slack ≈ (s* − s) at side s: k5_02's s0 certificate has margin 0.0006 and
k5_03's fails on bulk slabs near s0 while both pass cheaply at the bottom of the window — and both are classes the k7
pinwheel (s* = s0 + 0.0097, A107's S02 list) sits on. So the cost per unit of side is flat far below the shadow and
rises steeply as s approaches s* − (s* − s0), diverging only if a class contains an actual minimum (Trump's classes,
which is what the basin/tube machinery is for). Consequence for sweeps: anchor a fresh certificate at the top of each
slab (its slack is then s* − s_top, not s* − s0) rather than reusing the s0 certificate across the band.

What is *not* the cost driver: certificate-margin stragglers (hours each), exact endpoint certificates (seconds), the
Lean replay (excluded).
